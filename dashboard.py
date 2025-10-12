# dashboard.py
import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import pandas as pd
import time
from signal_engine import get_scored_companies
from ai_insights import (get_initial_analysis, get_follow_up_response, 
                         generate_outreach_email) 
from database_setup import Company
from stock_info import get_stock_data
from google_search import get_latest_news_from_google

# --- Page Configuration & Initialize State ---
st.set_page_config(page_title="AI Buying Signals Dashboard", layout="wide", initial_sidebar_state="collapsed")

# State for Miki Chat
if "active_chat_company_id" not in st.session_state:
    st.session_state.active_chat_company_id = None
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}

# State for the Notes feature
if "active_note_company_id" not in st.session_state:
    st.session_state.active_note_company_id = None

engine = create_engine('sqlite:///data/app_database.db', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
session = Session()

# --- Custom CSS ---
st.markdown("""
<style>
    /* Main page styling */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    /* Header row for the custom table */
    .header-row {
        font-weight: bold;
        color: #1DB954;
        padding-bottom: 10px;
    }
    /* Contact icons container */
    .contact-icons {
        display: flex;
        gap: 15px; /* space between icons */
        align-items: center;
    }
    .contact-icons img {
        transition: transform 0.2s;
    }
    .contact-icons img:hover {
        transform: scale(1.2);
    }
    /* Styling for the chat window */
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1em;
        font-weight: bold;
    }
    /* CSS for the scrollable chat expander */
    div[data-testid="stExpanderDetails"] div[data-testid="stVerticalBlock"] {
        max-height: 400px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# --- Main Dashboard Title & Filtering ---
st.title("AI Buying Signals Dashboard")
st.markdown("A prioritized feed of companies showing strong buying intent. Select an industry to filter the list.")

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
header_cols = st.columns([2, 1.5, 1.5, 3, 1.5, 1.5, 2, 1.5])
st.markdown('<div class="header-row">', unsafe_allow_html=True)
header_cols[0].markdown("<strong>Company</strong>", unsafe_allow_html=True)
header_cols[1].markdown("<strong>Industry</strong>", unsafe_allow_html=True)
header_cols[2].markdown("<strong>Location</strong>", unsafe_allow_html=True)
header_cols[3].markdown("<strong>Stock Market Info</strong>", unsafe_allow_html=True)
header_cols[4].markdown("<strong>Notes</strong>", unsafe_allow_html=True)
header_cols[5].markdown("<strong>Contact</strong>", unsafe_allow_html=True)
header_cols[6].markdown("<strong>Website</strong>", unsafe_allow_html=True)
header_cols[7].markdown("<strong>Ask Miki</strong>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Interactive Table Rows ---
if not scored_companies:
    st.warning("No companies match the selected filter or no signals have been detected.")

for company in scored_companies:
    with st.container():
        cols = st.columns([2, 1.5, 1.5, 3, 1.5, 1.5, 2, 1.5])
        
        # Display main row data
        cols[0].markdown(f"**{company['name']}**")
        cols[1].markdown(f"<span style='font-size: 0.9em; color: #FFFFFF;'>{company['industry']}</span>", unsafe_allow_html=True)
        cols[2].caption(f"{company['location']}")
        stock_data = get_stock_data(company.get('ticker_symbol'))
        if stock_data:
            stock_info_html = f"""
            <div style="font-size: 0.9em;">
                <span><strong>Price:</strong> {stock_data['Price']}</span> | 
                <span><strong>P/E:</strong> {stock_data['P/E Ratio']}</span><br>
                <span title="Market Capitalization"><strong>M. Cap:</strong> {stock_data['Market Cap']}</span>
            </div>
            """
            cols[3].markdown(stock_info_html, unsafe_allow_html=True)
        else:
            cols[3].caption("Not Publicly Traded")

        # --- Notes Button Logic ---
        with cols[4]:
            note_exists = company.get('notes', '').strip() != ''
            button_type = "primary" if note_exists else "secondary"
            button_label = "🗒️ View Note" if note_exists else "📝 Add Note"
            
            if st.button(button_label, key=f"notes_btn_{company['id']}", type=button_type):
                if st.session_state.active_note_company_id == company['id']:
                    st.session_state.active_note_company_id = None
                else:
                    st.session_state.active_note_company_id = company['id']
                st.rerun()

        # Contact, Website, and Miki Button
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
            else:
                st.session_state.active_chat_company_id = company['id']
                if company['id'] not in st.session_state.chat_histories:
                    st.session_state.chat_histories[company['id']] = [{"role": "assistant", "content": "Hi, I am Miki! Your AI-powered Chief of Staff. Click below to get my analysis of this signal."}]
            st.rerun()

        # --- The Notepad Expander ---
        if st.session_state.active_note_company_id == company['id']:
            _, note_col, _ = st.columns([1, 2, 1])
            with note_col:
                with st.expander(f"Note for {company['name']}", expanded=True):
                    note_key = f"note_text_{company['id']}"
                    note_content = st.text_area(
                        "Note Content",
                        value=company.get('notes', ''),
                        key=note_key,
                        height=150,
                        label_visibility="collapsed"
                    )
                    if st.button("Save Note", key=f"save_note_{company['id']}", type="primary"):
                        company_to_update = session.query(Company).filter(Company.id == company['id']).first()
                        if company_to_update:
                            company_to_update.notes = note_content
                            session.commit()
                            st.session_state.active_note_company_id = None # Close notepad on save
                            st.toast(f"Note for {company['name']} saved!", icon="✅")
                            time.sleep(1)
                            st.rerun()
        
        # The Chat Expander
        if st.session_state.active_chat_company_id == company['id']:
            latest_signal = company['latest_signal_obj']
            active_company_obj = session.query(Company).filter(Company.id == company['id']).first()
            active_chat_history = st.session_state.chat_histories[company['id']]

            _, chat_col, _ = st.columns([1, 2, 1])
            with chat_col:
                with st.expander("Chat with Miki", expanded=True):
                    for message in active_chat_history:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
                    
                    if len(active_chat_history) == 1:
                        if st.button("Get Actionable Insights", key=f"get_insight_{company['id']}"):
                            with st.spinner("Miki is analyzing the signal..."):
                                analysis = get_initial_analysis(latest_signal)
                                active_chat_history.append({"role": "assistant", "content": analysis})
                                st.rerun()

                    st.markdown("---")
                    btn1, btn2, btn3 = st.columns(3)

                    if btn1.button("📝 Write Email", key=f"email_{company['id']}"):
                        with st.spinner("Miki is drafting an email..."):
                            email_response = generate_outreach_email(latest_signal)
                            active_chat_history.append({"role": "assistant", "content": email_response})
                            st.rerun()
                    
                    if btn2.button("📰 Latest News", key=f"news_{company['id']}"):
                        with st.spinner("Searching Google for the latest news..."):
                            news_response = get_latest_news_from_google(company['name'])
                            active_chat_history.append({"role": "assistant", "content": news_response})
                            st.rerun()
                    
                    if btn3.button("🗑️ Clear Chat", key=f"clear_{company['id']}"):
                        st.session_state.chat_histories[company['id']] = [{"role": "assistant", "content": "Hi, I am Miki! Your AI-powered Chief of Staff. Click below to get my analysis of this signal."}]
                        st.rerun()

                    if prompt := st.chat_input("Ask a follow-up question..."):
                        active_chat_history.append({"role": "user", "content": prompt})
                        with st.chat_message("user"):
                            st.markdown(prompt)
                        
                        with st.chat_message("assistant"):
                            with st.spinner("Miki is thinking..."):
                                response = get_follow_up_response(active_chat_history, prompt)
                                st.markdown(response)
                        active_chat_history.append({"role": "assistant", "content": response})
                        st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)