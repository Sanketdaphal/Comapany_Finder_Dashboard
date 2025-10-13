# signal_engine.py
from datetime import datetime
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine
from database_setup import Company

# Database connection
engine = create_engine('sqlite:///data/app_database.db')
Session = sessionmaker(bind=engine)
session = Session()

def get_scored_companies():
    """
    Fetches all companies with their signals and contacts, calculates a priority score,
    and generates an outreach verdict.
    """
    companies = session.query(Company).options(
        joinedload(Company.signals),
        joinedload(Company.contacts) 
    ).all()
    
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
            
            priority_score = round(total_score)

            # --- UPDATED VERDICT LOGIC WITH NEW COLOR PALETTE ---
            verdict = {}
            if priority_score > 150:
                verdict = {"text": "🔥 Hot Lead", "color": "#FF5A5F", "explanation": "High-value signals detected. Recommend immediate and personalized outreach."}
            elif priority_score > 70:
                verdict = {"text": "🔶 Warm Lead", "color": "#F5B700", "explanation": "Showing strong intent. A good candidate for outreach in the next cycle."}
            else:
                verdict = {"text": "❄️ Cold Lead", "color": "#4A90E2", "explanation": "Low intent signals. Monitor for now, but not an immediate priority."}
            # --- END OF UPDATED LOGIC ---

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
                "priority_score": priority_score,
                "latest_signal_obj": latest_signal,
                "verdict": verdict
            })
            
    return sorted(scored_companies, key=lambda c: c['priority_score'], reverse=True)
