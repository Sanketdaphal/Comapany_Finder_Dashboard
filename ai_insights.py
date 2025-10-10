# ai_insights.py
import streamlit as st
import google.generativeai as genai
from database_setup import BuyingSignal

try:
    # Get the key from Streamlit's secure secrets manager
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    # Corrected model name
    model = genai.GenerativeModel('gemini-2.5-flash')
except (KeyError, AttributeError):
    st.error("Google API Key not found. Please set it in your Streamlit secrets.")
    model = None

def get_initial_analysis(signal: BuyingSignal):
    """Generates a strategic sales plan based on a buying signal."""
    if model is None: return "⚠️ AI model is not configured."
    
    prompt = f"""
    You are Miki, an elite B2B sales strategist AI. Your task is to analyze a buying signal and create a hyper-personalized outreach plan.

    **SIGNAL CONTEXT:**
    - **Company:** {signal.company.name}
    - **Industry:** {signal.company.industry}
    - **Signal Type:** {signal.signal_type}
    - **Signal Details:** "{signal.signal_data}"

    Based on this context, provide a concise and actionable sales plan in Markdown with the following four sections:

    1.  **Pain Point Analysis:** What is the most likely business problem or challenge this company is facing that led to this signal?
    2.  **Key Persona to Target:** What specific job title is the best person to contact about this problem?
    3.  **Core Value Proposition:** In one sentence, how can our (hypothetical) product solve their specific pain point?
    4.  **Outreach Email Hook:** Write two compelling, personalized opening sentences for a cold email to the target persona.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ An error occurred: {e}"

def get_follow_up_response(chat_history: list, question: str):
    """Generates a follow-up response with more flexible guardrails."""
    if model is None: return "⚠️ AI model is not configured."

    # Format the history for the prompt
    formatted_history = ""
    for message in chat_history:
        role = "User" if message["role"] == "user" else "Miki"
        formatted_history += f"{role}: {message['content']}\n"
    
    # === THIS IS THE UPDATED PROMPT WITH NEW RULES ===
    prompt = f"""
    You are Miki, an AI-powered Chief of Staff, an expert in B2B sales strategy.

    **Your Strict Instructions:**
    1.  Your primary purpose is to answer questions related to B2B sales, business strategy, writing emails, or analyzing the company and signals from the conversation history.
    2.  You ARE allowed to respond to simple greetings (like "Hi", "Hello") and questions about your own purpose (like "What can you do?"). For these, be polite and brief.
    3.  If the user asks any other irrelevant, off-topic question (e.g., about sports, politics, personal opinions), you MUST respond with ONLY this exact phrase: "I can only answer questions related to our work."

    **Conversation History:**
    {formatted_history}
    ---
    Your task is to act as Miki and provide the next response based on the last user message in the history. Adhere strictly to your instructions.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ An error occurred: {e}"
