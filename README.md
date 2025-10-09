# 🎯 AI Buying Signals Dashboard

This project is an interactive web application built with Streamlit that identifies and ranks companies based on real-time buying signals. It uses a custom scoring engine and a generative AI co-pilot (powered by Google's Gemini) to provide actionable sales insights.

![Dashboard Screenshot](link_to_your_screenshot.png)
*(Tip: Take a screenshot of your app, upload it to your GitHub repo, and link it here.)*

## ## Features

- **Real-Time Signal Feed:** A continuously updating, prioritized list of companies.
- **Dynamic Priority Scoring:** Ranks companies based on signal intensity, recency, and type.
- **Interactive UI:** A clean, modern interface for viewing company and signal data.
- **AI Co-pilot:** On-demand, AI-generated sales strategies for any company in the feed.
- **Custom Theming:** Supports both light and dark modes with custom CSS.

## ## Tech Stack

- **Frontend:** Streamlit
- **Backend/Logic:** Python, SQLAlchemy, APScheduler
- **Database:** SQLite
- **AI:** Google Gemini API
- **Data Simulation:** Faker

## ## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YourUsername/your-repo-name.git](https://github.com/YourUsername/your-repo-name.git)
    cd your-repo-name
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API Key:**
    - Rename the `config.py.template` file to `config.py`.
    - Open `config.py` and paste your Google AI API key.
    *(Note: You will need to create a `config.py.template` file for this step, which is good practice. Your actual `config.py` is ignored by git.)*

5.  **Initialize the database:**
    ```bash
    python database_setup.py
    python data_seeder.py
    ```

6.  **Run the application:**
    ```bash
    streamlit run dashboard.py
    ```
