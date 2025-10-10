# dashboard.py
import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from streamlit_autorefresh import st_autorefresh
from signal_engine import get_scored_companies
from ai_insights import get_ai_recommendation
from faker import Faker
import random
from datetime import datetime

# --- Page Configuration & Database ---
st.set_page_config(
    page_title="AI Buying Signals Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)
engine = create_engine('sqlite:///data/app_database.db', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
session = Session()
fake = Faker()

# --- Custom CSS (Your latest version) ---
st.markdown("""
<style>
    .stApp { background-color: #1E1E2E; color: #FFFFFF; }
    h1 { color: #FFFFFF; }
    .stMarkdown p { color: #FFFFFF; }
    .header-row {
        background-color: #1A1A2E;
        padding: 3px 30px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid #3A3A4A;
        display: flex;
        align-items: center;
    }
    .header-row .stMarkdown { flex-grow: 1; }
    .header-row .stMarkdown p { margin: 0; }
    .header-row .stMarkdown strong {
        font-family: 'Verdana', sans-serif;
        color: #C792EA; 
        font-size: 1.1em;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stContainer {
        border-radius: 8px;
        border: 1px solid #3A3A4A;
        padding: 15px 20px;
        background-color: #43455C;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
    .stContainer:hover {
        border-color: #C792EA;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
    }
    hr {
        margin-top: 1rem;
        margin-bottom: 1rem;
        border-top: 1px solid #3A3A4A;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Management Functions ---
def initialize_data():
    """Loads initial data from the DB into session state, runs only once."""
    if 'companies_data' not in st.session_state:
        st.session_state.companies_data = get_scored_companies()

def add_new_signal():
    """Generates a new fake signal and adds it to the top of the in-memory list."""
    if 'companies_data' in st.session_state and st.session_state.companies_data:
        new_company_name = fake.company()
        new_signal_options = {
            'FUNDING': {'data': f"Raised ${random.randint(1, 20)}M Series {random.choice(['A', 'B', 'C'])}"},
            'HIRING_SPREE': {'data': f"Hiring for {random.randint(5, 20)} new roles"}
        }
        sig_type, sig_info = random.choice(list(new_signal_options.items()))
        
        class FakeSignal:
            def __init__(self, sig_type, sig_data):
                self.signal_type = sig_type
                self.signal_data = sig_data
        
        new_entry = {
            "id": f"fake_{random.randint(1000, 9999)}",
            "name": new_company_name,
            "industry": random.choice(["FinTech SaaS", "AI/ML Platform"]),
            "location": f"{fake.street_address()}, {fake.city()}",
            "website": f"https://www.{fake.domain_name()}",
            "linkedin_url": f"https://linkedin.com/company/{fake.slug()}",
            "contact_phone": fake.phone_number(),
            "contact_email": fake.email(),
            "priority_score": random.randint(450, 600),
            "latest_signal_obj": FakeSignal(sig_type, sig_info['data'])
        }
        st.session_state.companies_data.insert(0, new_entry)

# --- Initialize Data & Start Auto-Refresh ---
initialize_data()
st_autorefresh(interval=20000, key="data_refresher")

if 'initial_load' not in st.session_state:
    st.session_state.initial_load = False
else:
    add_new_signal()

# --- Main Dashboard Title ---
st.title("🎯 AI Buying Signals Dashboard")
st.markdown("A **live, simulated feed** of companies showing strong buying intent. New data is added every 20 seconds.")

# --- Instant Single-Select Filter ---
all_scored_companies = st.session_state.get('companies_data', [])
scored_companies = all_scored_companies

if all_scored_companies:
    industries = sorted(list(set([c['industry'] for c in all_scored_companies])))
    filter_options = ["— Select an Industry to Filter —"] + industries
    selected_industry = st.selectbox(
        "", 
        options=filter_options,
        index=0
    )
    if selected_industry != "— Select an Industry to Filter —":
        scored_companies = [
            company for company in all_scored_companies if company['industry'] == selected_industry
        ]

st.markdown("---") 

# --- Custom Table Header ---
header_cols = st.columns([2, 1.5, 1.5, 2.5, 1, 1.5, 2, 1.5])
st.markdown('<div class="header-row">', unsafe_allow_html=True)
header_cols[0].markdown("<strong>Company</strong>", unsafe_allow_html=True)
header_cols[1].markdown("<strong>Industry</strong>", unsafe_allow_html=True)
header_cols[2].markdown("<strong>Location</strong>", unsafe_allow_html=True)
header_cols[3].markdown("<strong>Latest Signal</strong>", unsafe_allow_html=True)
header_cols[4].markdown("<strong>Score</strong>", unsafe_allow_html=True)
header_cols[5].markdown("<strong>Contact</strong>", unsafe_allow_html=True)
header_cols[6].markdown("<strong>Website</strong>", unsafe_allow_html=True)
header_cols[7].markdown("<strong>AI Co-pilot</strong>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# --- Interactive Table Rows ---
if not scored_companies:
    st.warning("No companies match the selected filter or no signals have been detected.")

for company in scored_companies:
    with st.container():
        cols = st.columns([2, 1.5, 1.5, 2.5, 1, 1.5, 2, 1.5])
        
        cols[0].markdown(f"**{company['name']}**")
        cols[1].markdown(f"<span style='font-size: 0.9em; color: #FFFFFF;'>{company['industry']}</span>", unsafe_allow_html=True)
        cols[2].caption(f"{company['location']}")
        latest_signal = company['latest_signal_obj']
        cols[3].markdown(f"**{latest_signal.signal_type.replace('_', ' ')}**")
        cols[3].caption(f"{latest_signal.signal_data}")
        cols[4].markdown(f"<span class='priority-score'>{company['priority_score']}</span>", unsafe_allow_html=True)
        contact_md = []
        if company.get('linkedin_url'):
            contact_md.append(f"<a href='{company['linkedin_url']}' target='_blank'><img src='https://cdn-icons-png.flaticon.com/512/174/174857.png' width='24' title='LinkedIn'></a>")
        if company.get('contact_phone'):
            contact_md.append(f"<a href='tel:{company['contact_phone']}'><img src='https://cdn-icons-png.flaticon.com/512/5585/5585856.png' width='24' title='Call'></a>")
        if company.get('contact_email'):
            contact_md.append(f"<a href='mailto:{company['contact_email']}'><img src='https://cdn-icons-png.flaticon.com/512/732/732200.png' width='24' title='Email'></a>")
        cols[5].markdown(f"<div class='contact-icons'>{' '.join(contact_md)}</div>", unsafe_allow_html=True)
        cols[6].markdown(f"[{company['website'].replace('https://www.', '').replace('https://', '')}]({company['website']})")
        
        insight_key = f"ai_insight_{company['id']}"
        if cols[7].button("Get Insight", key=f"ai_btn_{company['id']}"):
            with st.spinner(f"AI Co-pilot is analyzing {company['name']}..."):
                st.session_state[insight_key] = get_ai_recommendation(latest_signal)
        
        # Corrected logic for showing and hiding the AI insight
        if insight_key in st.session_state:
            info_box = st.info(f"**AI Strategy for {company['name']}**", icon="🧠")
            info_box.markdown(st.session_state[insight_key])
            if info_box.button("Hide Insight", key=f"hide_btn_{company['id']}"):
                del st.session_state[insight_key]
                st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
