# ai_insights.py
import streamlit as st # <-- Make sure this is imported
import google.generativeai as genai
from database_setup import BuyingSignal

# Get the key from Streamlit's secure secrets manager
# This line only works when the app is deployed on Streamlit
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# Configure the API with the key we just got
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_ai_recommendation(signal: BuyingSignal):
    # ... (The rest of the file remains the same)
    prompt = f"""
    You are an expert B2B sales strategist named "AI Co-pilot". A prospect company has triggered a buying signal.
    Your task is to provide a concise, actionable recommendation for a sales development representative (SDR).

    **Company:** {signal.company.name}
    **Industry:** {signal.company.industry}
    **Signal Type:** {signal.signal_type}
    **Signal Details:** "{signal.signal_data}"

    Provide the following in a clear, brief format using Markdown:
    1.  **Interpretation:** Why this signal matters for sales right now.
    2.  **Actionable Advice:** The specific next step the SDR should take.
    3.  **Email Hook:** A compelling opening sentence for a cold email that references this signal.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response.parts else f"⚠️ AI response was blocked. Reason: {response.prompt_feedback.block_reason.name}."
    except Exception as e:
        return f"❌ An error occurred while contacting the AI model: {e}"