# data_seeder.py
import random
import pandas as pd # <-- ADD THIS LINE
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Company, BuyingSignal, Contact

fake = Faker()
engine = create_engine('sqlite:///data/app_database.db')
Session = sessionmaker(bind=engine)
session = Session()

def seed_initial_data(num_signals=200):
    # --- This part remains the same: Clear old data ---
    session.query(BuyingSignal).delete()
    session.query(Contact).delete()
    session.query(Company).delete()
    session.commit()
    print("🗑️ Cleared existing data from all tables.")

    # --- THIS IS THE NEW LOGIC: Read from CSV ---
    try:
        df = pd.read_csv('data/companies_dataset.csv')
    except FileNotFoundError:
        print("❌ Error: 'data/companies_dataset.csv' not found.")
        print("Please ensure you have created the CSV file in the 'data' directory.")
        return

    companies_added = 0
    for index, row in df.iterrows():
        # Combine locality and country for the location field
        location = f"{row['locality']}, {row['country']}"

        # Create a full website URL from the domain
        website = f"https://www.{row['domain']}"
        
        # Ensure LinkedIn URL is a full URL
        linkedin_url = f"https://{row['linkedin_url']}" if not row['linkedin_url'].startswith('http') else row['linkedin_url']

        company = Company(
            name=row['name'].title(),
            location=location,
            industry=row['industry'].title(),
            website=website,
            linkedin_url=linkedin_url,
            phone=fake.phone_number(),
            ticker_symbol=row['ticker_symbol'], # <-- ADD THIS LINE
            notes=""
        )
        
        
        session.add(company)
        
        # We can still generate a few fake contacts for each real company
        for _ in range(random.randint(1, 3)):
            contact = Contact(company=company, name=fake.name(), email=fake.email(), phone=fake.phone_number())
            session.add(contact)
        
        companies_added += 1
            
    session.commit()
    print(f"🌱 Seeded {companies_added} companies from CSV file.")

    # --- This part remains similar: Generate random signals for the new companies ---
    for _ in range(num_signals):
        generate_random_signal(commit=False)
    session.commit()
    print(f"📡 Seeded {num_signals} random buying signals for the new companies.")


def generate_random_signal(commit=True):
    # This function remains unchanged, it will now pick from the companies loaded from the CSV
    company = random.choice(session.query(Company).all())
    signal_options = {
        'FUNDING': {'data': f"Raised ${random.randint(1, 20)}M Series {random.choice(['A', 'B', 'C'])}", 'intensity': random.randint(70, 100)},
        'HIRING_SPREE': {'data': f"Hiring for {random.randint(5, 20)} new roles in {random.choice(['Sales', 'Engineering', 'Marketing'])}", 'intensity': random.randint(60, 90)},
        'TECH_CHANGE': {'data': f"Announced new integration with {random.choice(['HubSpot', 'Salesforce', 'AWS', 'Stripe'])}", 'intensity': random.randint(40, 70)},
        'COMPANY_NEWS': {'data': fake.bs().title(), 'intensity': random.randint(20, 60)},
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
    if commit:
        session.commit()

if __name__ == '__main__':
    seed_initial_data()
