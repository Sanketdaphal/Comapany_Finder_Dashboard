# data_seeder.py
import streamlit as st
import random
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
from database_setup import Company, BuyingSignal, Contact, Base

# Use Streamlit's built-in SQL connection
conn = st.connection("sql", dialect="sqlite")

def seed_initial_data(num_signals=200):
    with conn.session as session:
        # Clear old data
        session.query(BuyingSignal).delete()
        session.query(Contact).delete()
        session.query(Company).delete()
        session.commit()
        st.toast("🗑️ Cleared existing data...")

        try:
            df = pd.read_csv('data/companies_dataset.csv')
        except FileNotFoundError:
            st.error("❌ Error: 'data/companies_dataset.csv' not found.")
            return

        companies_added = 0
        for index, row in df.iterrows():
            location = f"{row['locality']}, {row['country']}"
            website = f"https://www.{row['domain']}"
            linkedin_url = f"https://{row['linkedin_url']}" if pd.notna(row['linkedin_url']) and not row['linkedin_url'].startswith('http') else row['linkedin_url']

            company = Company(
                name=row['name'].title(),
                location=location,
                industry=row['industry'].title(),
                website=website,
                linkedin_url=linkedin_url,
                phone=Faker().phone_number(),
                ticker_symbol=row['ticker_symbol'],
                notes=""
            )
            session.add(company)
            
            for _ in range(random.randint(1, 3)):
                contact = Contact(company=company, name=Faker().name(), email=Faker().email(), phone=Faker().phone_number())
                session.add(contact)
            
            companies_added += 1
        
        session.commit()
        st.toast(f"🌱 Seeded {companies_added} companies...")

        all_companies = session.query(Company).all()
        if not all_companies:
            st.warning("No companies to add signals to.")
            return

        for _ in range(num_signals):
            company = random.choice(all_companies)
            signal_options = {
                'FUNDING': {'data': f"Raised ${random.randint(1, 20)}M Series {random.choice(['A', 'B', 'C'])}", 'intensity': random.randint(70, 100)},
                'HIRING_SPREE': {'data': f"Hiring for {random.randint(5, 20)} new roles in {random.choice(['Sales', 'Engineering', 'Marketing'])}", 'intensity': random.randint(60, 90)},
                'TECH_CHANGE': {'data': f"Announced new integration with {random.choice(['HubSpot', 'Salesforce', 'AWS', 'Stripe'])}", 'intensity': random.randint(40, 70)},
                'COMPANY_NEWS': {'data': Faker().bs().title(), 'intensity': random.randint(20, 60)},
                'WEBSITE_TRAFFIC_SPIKE': {'data': f"{random.randint(50, 200)}% increase in organic traffic", 'intensity': random.randint(50, 80)}
            }
            sig_type, sig_info = random.choice(list(signal_options.items()))
            new_signal = BuyingSignal(
                company=company,
                signal_type=sig_type,
                signal_data=sig_info['data'],
                intensity_score=sig_info['intensity'],
                timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 60))
            )
            session.add(new_signal)
        
        session.commit()
        st.toast(f"📡 Seeded {num_signals} random buying signals.")

if __name__ == '__main__':
    # This part is for local testing if needed, but the main use is via the app
    print("This seeder is intended to be run from the Streamlit app's admin panel.")
