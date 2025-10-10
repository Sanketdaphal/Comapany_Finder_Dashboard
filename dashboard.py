# dashboard.py
import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from signal_engine import get_scored_companies
from ai_insights import get_ai_recommendation

# --- Page Configuration & Database ---
st.set_page_config(
    page_title="AI Buying Signals Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)
engine = create_engine('sqlite:///data/app_database.db', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
session = Session()

# --- Custom CSS for Dark Purple Theme ---
st.markdown("""
<style>
    /* ... (CSS remains the same) ... */
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


# --- Main Dashboard Title ---
st.title("🎯 AI Buying Signals Dashboard")
st.markdown("A prioritized feed of companies showing strong buying intent. Select an industry to filter the list.")

# --- Instant Single-Select Filter ---
all_scored_companies = get_scored_companies()
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
        
        # === THE FIX IS HERE ===
        # Changed 'st.session_-state' to 'st.session_state'
        # and removed the unnecessary 'in locals()' check.
        if insight_key in st.session_state:
            st.info(f"**AI Strategy for {company['name']}**", icon="🧠")
            st.markdown(st.session_state[insight_key])

    st.markdown("<hr>", unsafe_allow_html=True)
