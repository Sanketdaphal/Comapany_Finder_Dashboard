# Company Finder Dashboard
![Python](![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg))
![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

An advanced sales intelligence platform that transforms raw company data into a prioritized, actionable feed. This tool leverages AI to provide deep strategic insights, generate outreach content, and integrate real-time financial and news data, all within a clean, interactive user interface.

---

## 🚀 Live Demo

**[>> Access the live application here <<](https://ai-buying-signals-dashboard-guovm6evzxexnwxnmxmekh.streamlit.app/)**

 

---

## 📸 Application Preview

![AI Buying Signals Dashboard Screenshot](Image.png)
 

---

## ✨ Key Features
 
### 🤖 AI Co-Pilot ("Miki")
An interactive chatbot designed to be a sales strategist. The interface provides one-click actions and a conversational text input for custom queries.
* **Actionable Insights:** Generates a full strategic plan, including likely pain points, key personas to target, and a core value proposition.
* **AI Email Writer:** Drafts a complete, personalized, and ready-to-send cold outreach email.
* **Live News Feed:** Fetches and summarizes the top 3 latest news articles for any company using a live Google Search.
* **Follow-up Q&A:** Allows for multi-turn, context-aware conversations to refine strategy and ask specific questions.

### 💹 Integrated Financial Intelligence
* For publicly traded companies, the dashboard displays key stock market data directly in the company row.
* Metrics include current stock price, P/E ratio, market capitalization, and the 5-Year Compound Annual Growth Rate (CAGR).
* Data is fetched from Yahoo Finance and cached to ensure a responsive UI.

### 🗒️ Persistent User Notes
* A built-in notepad for every company allows users to add, view, and save their own qualitative insights.
* The button dynamically changes to show whether a note already exists.
* Notes are saved persistently in the database, creating a system of record.

### 🖥️ Interactive & Responsive UI
* Built with Streamlit, the UI is clean, modern, and easy to navigate.
* Features an industry filter to instantly narrow down the list of companies.
* Includes quick-access icons for LinkedIn, email, and phone, plus a direct link to the company website.

---

## 🛠️ Technology Stack

* **Frontend:** Streamlit
* **Backend:** Python 3.9+
* **Database:** SQLite + SQLAlchemy ORM
* **AI & Data APIs:**
    * Google Gemini API (for AI strategy & text generation)
    * Google Custom Search API (for live news)
    * `yfinance` (for stock market data)
* **Data Seeding:** Pandas, Faker

* ## ⚙️ Setup and Installation

Follow these steps to get the dashboard running on your local machine.

---

### 1. Prerequisites

* Python 3.8+
* Git

---

### 2. Clone the Repository


git clone <your-repository-url>
cd <repository-name>

. Set Up a Virtual Environment
It's recommended to use a virtual environment to manage dependencies.

Windows:

Bash

python -m venv venv
.\venv\Scripts\activate
macOS / Linux:

Bash

python3 -m venv venv
source venv/bin/activate

4. Install Dependencies
Install all the required Python packages from the requirements.txt file.

Bash

pip install -r requirements.txt
5. Configure API Keys
The application uses Google's Custom Search API to fetch news. You'll need to create a secrets file for your API keys.

Create a new directory in the root of the project:

Bash

mkdir .streamlit
Create a secrets file inside this new directory:

Bash

touch .streamlit/secrets.toml
Add your Google API Key and Search Engine ID to the secrets.toml file. You can get these credentials from the Google Cloud Console and the Programmable Search Engine control panel.

Ini, TOML

# .streamlit/secrets.toml
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY_HERE"
SEARCH_ENGINE_ID = "YOUR_SEARCH_ENGINE_ID_HERE"

# Note: If using a Generative AI model like Gemini, add its key here too.
# GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
6. Prepare the Company Dataset
The application seeds its initial data from a CSV file.

Ensure you have a data directory in the root of the project.

Create a CSV file named companies_dataset.csv inside the data directory (data/companies_dataset.csv).

 
Export to Sheets
Note: For private companies, leave the ticker_symbol column empty.

7. Initialize the Database and Seed Data
Run the following scripts from your terminal in order.

Set up the database schema:

Bash

python database_setup.py
This will create an app_database.db file in the data directory.

Seed the database with initial data:

Bash

python data_seeder.py
This will read your companies_dataset.csv, populate the database, and generate random buying signals for the companies.
