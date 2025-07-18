import streamlit as st
import pandas as pd
import gspread
import requests
import time
from google.oauth2.service_account import Credentials


# Function to get live prices from CoinGecko
@st.cache_data(ttl=3600)  # cache for 60 minutes (3600 seconds)

def get_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum",
        "vs_currencies": "usd"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    try:
        prices = response.json()
        btc_price = int(prices["bitcoin"]["usd"])
        eth_price = int(prices["ethereum"]["usd"])

    except Exception as e:
        st.error(f"Failed to fetch prices: {e}")

    return btc_price, eth_price


# Function to get raw treasury data from Google master sheets
def load_data():
    BTC_PRICE, ETH_PRICE = get_prices()
    print(f"Current BTC/USD: {BTC_PRICE}, \nCurrent ETH/USD: {ETH_PRICE}")
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("master_table_v01")

    btc_data = pd.DataFrame(sheet.worksheet("aggregated_btc_data").get_all_records())
    eth_data = pd.DataFrame(sheet.worksheet("aggregated_eth_data").get_all_records())
    #meta = sheet.worksheet("metadata").cell(1,1).value
    meta = "July 17, 2025"

    df = pd.concat([btc_data, eth_data], ignore_index=True)
    df = df[["Entity Name", "Entity Type", "Country", "Crypto Asset", "Holdings (Unit)"]]
    df["Holdings (Unit)"] = (
        df["Holdings (Unit)"]
        .astype(str)
        .str.replace(".", "", regex=False)  # remove thousand separators
        .str.replace(",", ".", regex=False)  # convert decimal comma to dot
        .astype(float)
    )
    df["USD Value"] = df.apply(lambda x: x["Holdings (Unit)"] * (BTC_PRICE if x["Crypto Asset"] == "BTC" else ETH_PRICE), axis=1)

    return df, meta
