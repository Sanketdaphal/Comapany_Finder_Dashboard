# data_seeder.py
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Company, BuyingSignal, Contact

fake = Faker()
engine = create_engine('sqlite:///data/app_database.db')
Session = sessionmaker(bind=engine)
session = Session()

def seed_initial_data(num_companies=50, num_signals=200):
    session.query(BuyingSignal).delete()
    session.query(Contact).delete()
    session.query(Company).delete()
    session.commit()

    companies = []
    for _ in range(num_companies):
        company = Company(
            name=fake.company(),
            location=f"{fake.street_address()}, {fake.city()}",
            industry=random.choice(["Computer Software", "Healthcare Software", "FinTech SaaS", "AI/ML Platform"]),
            phone=fake.phone_number(),
            # Change this line: ensure website starts with https://
            website=f"https://www.{fake.domain_name()}", 
            linkedin_url=f"https://linkedin.com/company/{fake.slug()}" # Ensure LinkedIn URL is also seeded
        )
        companies.append(company)
        session.add(company)
        
        for _ in range(random.randint(1, 4)):
            contact = Contact(company=company, name=fake.name(), email=fake.email(), phone=fake.phone_number())
            session.add(contact)
            
    session.commit()
    print(f"🌱 Seeded {num_companies} companies with updated details.")

    for _ in range(num_signals):
        generate_random_signal(commit=False)
    session.commit()
    print(f"📡 Seeded {num_signals} initial buying signals.")

def generate_random_signal(commit=True):
    # ... (This function remains unchanged)
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
    print(f"⚡ Added signal '{sig_type}' for company '{company.name}'")

if __name__ == '__main__':
    seed_initial_data()