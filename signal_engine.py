# signal_engine.py
import streamlit as st
from datetime import datetime
from sqlalchemy.orm import joinedload
from database_setup import Company, Base # Import Base

# --- Use Streamlit's built-in SQL connection, explicitly setting the dialect ---
conn = st.connection("sql", dialect="sqlite")

def get_scored_companies():
    """
    Fetches all companies with their signals and contacts, and calculates a priority score.
    """
    try:
        with conn.session as session:
            # Create tables if they don't exist
            Base.metadata.create_all(session.bind)
            
            companies = session.query(Company).options(
                joinedload(Company.signals),
                joinedload(Company.contacts) 
            ).all()
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        st.info("If this is the first run, please use the Admin Panel in the sidebar to seed the database.")
        return [] # Return an empty list to prevent crashing
    
    scored_companies = []

    for company in companies:
        total_score = 0
        if not company.signals:
            continue

        for signal in company.signals:
            days_old = (datetime.utcnow() - signal.timestamp).days
            recency_weight = max(0, 1 - (days_old / 90.0))
            type_weight = {'FUNDING': 1.5, 'HIRING_SPREE': 1.2, 'WEBSITE_TRAFFIC_SPIKE': 1.1, 'TECH_CHANGE': 1.0, 'COMPANY_NEWS': 0.8}.get(signal.signal_type, 1.0)
            signal_score = signal.intensity_score * recency_weight * type_weight
            total_score += signal_score
        
        if total_score > 0:
            latest_signal = max(company.signals, key=lambda s: s.timestamp)
            first_contact = company.contacts[0] if company.contacts else None

            scored_companies.append({
                "id": company.id,
                "name": company.name,
                "industry": company.industry,
                "location": company.location,
                "website": company.website,
                "linkedin_url": company.linkedin_url,
                "ticker_symbol": company.ticker_symbol,
                "notes": company.notes,
                "contact_phone": first_contact.phone if first_contact else None,
                "contact_email": first_contact.email if first_contact else None,
                "priority_score": round(total_score),
                "latest_signal_obj": latest_signal
            })
            
    return sorted(scored_companies, key=lambda c: c['priority_score'], reverse=True)
