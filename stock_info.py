# stock_info.py
import yfinance as yf
import streamlit as st
import pandas as pd 

# Use Streamlit's cache to avoid re-fetching data on every single interaction.
# Data will be cached for 15 minutes (900 seconds).
@st.cache_data(ttl=900)
def get_stock_data(ticker_symbol):
    """
    Fetches key stock information for a given ticker symbol.
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

        # Format the data neatly
        data = {
            "Market Cap": f"${market_cap / 1_000_000_000:.2f}B" if market_cap else "N/A",
            "Price": f"${current_price:.2f}" if current_price else "N/A",
            "P/E Ratio": f"{pe_ratio:.2f}" if pe_ratio else "N/A",
            "Day Range": f"${day_low:.2f} - ${day_high:.2f}" if day_low and day_high else "N/A"
        }
        return data

    except Exception as e:
        # This can happen for invalid tickers or network issues
        print(f"Could not fetch stock data for {ticker_symbol}: {e}")
        return None