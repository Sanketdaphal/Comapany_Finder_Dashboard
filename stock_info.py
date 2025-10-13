# stock_info.py
import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import datetime

# Use Streamlit's cache to avoid re-fetching data on every single interaction.
# Data will be cached for 15 minutes (900 seconds).
@st.cache_data(ttl=900)
def get_stock_data(ticker_symbol):
    """
    Fetches key stock information, including 5-year CAGR, for a given ticker symbol.
    """
    if not ticker_symbol or pd.isna(ticker_symbol):
        return None
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        # yfinance sometimes returns strings 'None' or None, so we check carefully
        market_cap = info.get('marketCap')
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        pe_ratio = info.get('trailingPE')
        day_high = info.get('dayHigh')
        day_low = info.get('dayLow')

        # --- NEW: CAGR CALCULATION ---
        cagr_5y = "N/A"
        hist = ticker.history(period="5y")
        
        # Check if we have enough data and a valid current price
        if not hist.empty and current_price:
            # Get the oldest available closing price (start price)
            start_price = hist['Close'].iloc[0]
            start_date = hist.index[0]
            end_date = hist.index[-1]
            
            # Calculate the number of years between the start and end dates
            num_years = (end_date - start_date).days / 365.25

            # Ensure there's a valid start price and at least one year of data
            if start_price > 0 and num_years >= 1:
                # CAGR Formula: (Ending Value / Beginning Value)^(1 / Num Years) - 1
                cagr = ((current_price / start_price) ** (1 / num_years)) - 1
                cagr_5y = f"{cagr:.2%}" # Format as a percentage
        # --- END OF NEW CODE ---

        # Format the data neatly
        data = {
            "Market Cap": f"${market_cap / 1_000_000_000:.2f}B" if market_cap else "N/A",
            "Price": f"${current_price:.2f}" if current_price else "N/A",
            "P/E Ratio": f"{pe_ratio:.2f}" if pe_ratio else "N/A",
            "Day Range": f"${day_low:.2f} - ${day_high:.2f}" if day_low and day_high else "N/A",
            "CAGR (5Y)": cagr_5y # Add the new CAGR value to the dictionary
        }
        return data

    except Exception as e:
        # This can happen for invalid tickers or network issues
        print(f"Could not fetch stock data for {ticker_symbol}: {e}")
        return None
