# dashboard.py
import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from signal_engine import get_scored_companies
from ai_insights import get_initial_analysis, get_follow_up_response

# --- Page Configuration & Initialize State ---
st.set_page_config(page_title="AI Buying Signals Dashboard", layout="wide", initial_sidebar_state="collapsed")

if "active_chat_company_id" not in st.session_state:
    st.session_state.active_chat_company_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

engine = create_engine('sqlite:///data/app_database.db', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
session = Session()

# --- Custom CSS ---
st.markdown("""
<style>
    /* Your existing CSS goes here */

    /* CSS for the scrollable chat expander */
    div[data-testid="stExpanderDetails"] div[data-testid="stVerticalBlock"] {
        max-height: 400px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# --- Main Dashboard Title ---
st.title("🎯 AI Buying Signals Dashboard")
st.markdown("A prioritized feed of companies showing strong buying intent. Select an industry to filter the list.")

# --- Data Loading and Filtering ---
all_scored_companies = get_scored_companies()
scored_companies = all_scored_companies 

if all_scored_companies:
    industries = sorted(list(set([c['industry'] for c in all_scored_companies])))
    filter_options = ["— Select an Industry to Filter —"] + industries
    selected_industry = st.selectbox("", options=filter_options, index=0)
    if selected_industry != "— Select an Industry to Filter —":
        scored_companies = [c for c in all_scored_companies if c['industry'] == selected_industry]

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
header_cols[7].markdown("<strong>Ask Miki</strong>", unsafe_allow_html=True)
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
        
        if cols[7].button("Ask Miki", key=f"ai_btn_{company['id']}"):
            if st.session_state.active_chat_company_id == company['id']:
                st.session_state.active_chat_company_id = None
                st.session_state.messages = []
            else:
                st.session_state.active_chat_company_id = company['id']
                st.session_state.messages = [{"role": "assistant", "content": "Hi, I am Miki! Your AI-powered Chief of Staff. Click below to get my analysis of this signal."}]
            st.rerun()
        
    # --- The Chat Window (Expander) ---
    if st.session_state.active_chat_company_id == company['id']:
        _, chat_col, _ = st.columns([1, 2, 1])
        with chat_col:
            with st.expander("Chat with Miki", expanded=True):
                
                # --- THIS IS THE CORRECTED AND FINAL CHAT LOGIC ---

                # 1. Display all existing messages from the history
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                
                # 2. Check if the LAST message was from the user, if so, get a response
                if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                    with st.chat_message("assistant"):
                        with st.spinner("Miki is thinking..."):
                            response = get_follow_up_response(st.session_state.messages, st.session_state.messages[-1]["content"])
                            st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

                # 3. Handle the initial "Get Insights" button
                if len(st.session_state.messages) == 1:
                    if st.button("Get Actionable Insights", key=f"get_insight_{company['id']}"):
                        with st.spinner("Miki is analyzing the signal..."):
                            analysis = get_initial_analysis(latest_signal)
                            st.session_state.messages.append({"role": "assistant", "content": analysis})
                            st.rerun()
                
                # 4. Handle all follow-up questions
                if prompt := st.chat_input("Ask a follow-up question..."):
                    # When user types, just add their message to state and rerun
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
