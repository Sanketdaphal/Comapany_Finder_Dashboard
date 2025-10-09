# database_setup.py
import datetime
from sqlalchemy import (create_engine, Column, Integer, String, Float,
                        DateTime, Text, ForeignKey)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    industry = Column(String)
    location = Column(String) 
    
    # ADD THIS LINE BACK
    linkedin_url = Column(String)

    phone = Column(String)
    website = Column(String) 
    
    signals = relationship("BuyingSignal", back_populates="company", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")

class Contact(Base):
    # ... (This class remains unchanged)
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    company = relationship("Company", back_populates="contacts")


class BuyingSignal(Base):
    # ... (This class remains unchanged)
    __tablename__ = 'buying_signals'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    signal_type = Column(String)
    signal_data = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    intensity_score = Column(Float)
    company = relationship("Company", back_populates="signals")

def setup_database():
    engine = create_engine('sqlite:///data/app_database.db')
    Base.metadata.create_all(engine)
    print("✅ Database and tables updated successfully.")

if __name__ == '__main__':
    setup_database()