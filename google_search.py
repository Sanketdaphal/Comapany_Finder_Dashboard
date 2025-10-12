# google_search.py
import streamlit as st
from googleapiclient.discovery import build
import pandas as pd

@st.cache_data(ttl=3600)  # Cache results for 1 hour to save API quota
def get_latest_news_from_google(company_name):
    """
    Performs a Google search for the latest news about a company.
    """
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        search_engine_id = st.secrets["SEARCH_ENGINE_ID"]

        # Build the search service
        service = build("customsearch", "v1", developerKey=api_key)
        
        # Define the search query
        query = f"{company_name} business news"

        # Execute the search
        res = service.cse().list(q=query, cx=search_engine_id, num=3).execute()

        # Format the results
        if 'items' in res:
            news_items = []
            for item in res['items']:
                title = item['title']
                link = item['link']
                snippet = item['snippet'].replace('\n', '')
                news_items.append(f"**- {title}**: *{snippet}* [Read more]({link})")
            
            return "Here are the top 3 recent news items I found:\n\n" + "\n\n".join(news_items)
        else:
            return "I couldn't find any recent news for this company."

    except KeyError:
        return "⚠️ Google API Key or Search Engine ID is not configured in secrets."
    except Exception as e:
        print(f"An error occurred during Google Search: {e}")
        return f"❌ An error occurred while searching for news: {e}"