# dashboard.py
import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from streamlit_autorefresh import st_autorefresh
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

# --- Custom CSS for Light Theme ---
st.markdown("""
<style>
    /* ... (other styles remain the same) ... */
    .stApp { background-color: #FFFFFF; color: #262730; }
    h1 { color: #1E1E1E; }
    .stMarkdown p { color: #4F4F4F; }
    .header-row { background-color: #F0F2F6; padding: 15px 20px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #DADCE0; }
    
    /* === CSS FIX IS HERE === */
    .header-row .stMarkdown strong {
        color: #212529; /* Dark color */
        font-weight: 700; /* Bolder */
        text-decoration: underline; /* Added underline */
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 1em;
    }

    .stContainer { border-radius: 8px; border: 1px solid #DADCE0; padding: 15px 20px; margin-bottom: 12px; background-color: #FFFFFF; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); transition: all 0.2s ease-in-out; }
    .stContainer:hover { border-color: #4A00E0; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
    .priority-score { font-size: 2.2em; font-weight: 800; color: #D90429; }
    .stButton > button { background-image: linear-gradient(to right, #8E2DE2 0%, #4A00E0 51%, #8E2DE2 100%); background-size: 200% auto; color: white; border-radius: 6px; border: none; padding: 8px 15px; font-weight: 600; transition: 0.5s; }
    .stButton > button:hover { background-position: right center; transform: translateY(-1px); }
    .stAlert { border-radius: 8px; border-left: 5px solid #4A00E0; background-color: #F0F2F6; }
    .contact-icons img { margin-right: 8px; opacity: 0.7; transition: opacity 0.2s ease-in-out; }
    .contact-icons img:hover { opacity: 1.0; }
    .stMarkdown a { color: #4A00E0; text-decoration: none; }
    .stMarkdown a:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)


# --- Auto-Refresh Component ---
st_autorefresh(interval=20000, key="data_refresher")

# --- Main Dashboard Title ---
st.title("🎯 AI Buying Signals Dashboard")
st.markdown("A prioritized feed of companies showing strong buying intent. The data feed refreshes automatically every 20 seconds.")
st.markdown("---")

# --- Custom Table Header ---
with st.container():
    st.markdown('<div class="header-row">', unsafe_allow_html=True)
    header_cols = st.columns([2, 1.5, 1.5, 2.5, 1, 1.5, 2, 1.5])
    
    # === CODE FIX IS HERE ===
    # Added unsafe_allow_html=True to every column header
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
scored_companies = get_scored_companies()

if not scored_companies:
    st.info("Scanning for buying signals... The feed will populate as new signals are detected.")

for company in scored_companies:
    with st.container():
        cols = st.columns([2, 1.5, 1.5, 2.5, 1, 1.5, 2, 1.5])
        
        cols[0].markdown(f"**{company['name']}**")
        cols[1].markdown(f"<span style='font-size: 0.9em; color: #4F4F4F;'>{company['industry']}</span>", unsafe_allow_html=True)
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
            contact_md.append(f"<a href='mailto:{company['contact_email']}'><img src='https://cdn-icons-png.flaticon.com/512/542/542689.png' width='24' title='Email'></a>")
        cols[5].markdown(f"<div class='contact-icons'>{' '.join(contact_md)}</div>", unsafe_allow_html=True)
        cols[6].markdown(f"[{company['website'].replace('https://www.', '').replace('https://', '')}]({company['website']})")
        insight_key = f"ai_insight_{company['id']}"
        if cols[7].button("Get Insight", key=f"ai_btn_{company['id']}"):
            with st.spinner(f"AI Co-pilot is analyzing {company['name']}..."):
                st.session_state[insight_key] = get_ai_recommendation(latest_signal)
        if insight_key in st.session_state:
            st.info(f"**AI Strategy for {company['name']}**", icon="🧠")
            st.markdown(st.session_state[insight_key])