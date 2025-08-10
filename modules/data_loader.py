import streamlit as st
import json, os, time, requests, gspread, pandas as pd
from google.oauth2.service_account import Credentials


# Function to get real-time price feed from CoinGecko, incl. fallback option
FILENAME = "data/last_prices.json"

def load_last_prices():
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            return json.load(f)
    else:
        return {"btc": 115_000, "eth": 3_500}

def save_last_prices(btc, eth):
    with open(FILENAME, "w") as f:
        json.dump({"btc": btc, "eth": eth}, f)

@st.cache_data(ttl=3600)
def get_prices():

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin,ethereum", "vs_currencies": "usd"}
    last = load_last_prices()

    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            prices = response.json()
            btc_price = int(prices["bitcoin"]["usd"])
            eth_price = int(prices["ethereum"]["usd"])
            save_last_prices(btc_price, eth_price)
            print(f"Current BTC/USD: {btc_price}, Current ETH/USD: {eth_price}")
            return btc_price, eth_price
        except:
            time.sleep(5)
    
    st.warning("CoinGecko API unreachable. Showing last saved prices.")

    return last["btc"], last["eth"]

# Function to get raw treasury data from master sheets
def load_units():

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("master_table_v01")

    btc_data = pd.DataFrame(sheet.worksheet("aggregated_btc_data").get_all_records())
    eth_data = pd.DataFrame(sheet.worksheet("aggregated_eth_data").get_all_records())

    df = pd.concat([btc_data, eth_data], ignore_index=True)
    df = df[["Entity Name", "Entity Type", "Country", "Crypto Asset", "Holdings (Unit)"]]
    df["Holdings (Unit)"] = (
        df["Holdings (Unit)"]
        .astype(str)
        .str.replace(".", "", regex=False)  # remove thousand separators
        .str.replace(",", ".", regex=False)  # convert decimal comma to dot
        .astype(float)
    )

    return df

def attach_usd_values(df_units, btc_price, eth_price):
    df = df_units.copy()
    df["USD Value"] = df.apply(
        lambda x: x["Holdings (Unit)"] * (btc_price if x["Crypto Asset"] == "BTC" else eth_price),
        axis=1,
    )
    return df

# Function to get historic treasury data from master sheets
@st.cache_data(ttl=900, show_spinner=False)
def load_historic_data():
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("master_table_v01")

    historic_btc_data = pd.DataFrame(sheet.worksheet("historic_btc").get_all_records())
    historic_eth_data = pd.DataFrame(sheet.worksheet("historic_eth").get_all_records())

    df = pd.concat([historic_btc_data, historic_eth_data], ignore_index=True)
    df = df[["Year", "Month", "Crypto Asset", "Holdings (Unit)", "USD Value"]]
    
    df["Year"] = df["Year"].astype(int)
    df = df[df["Year"] > 2023]
    df["Month"] = df["Month"].astype(int)
    df['Date'] = pd.to_datetime(df[['Year', 'Month']].assign(DAY=1))

    df["Holdings (Unit)"] = df["Holdings (Unit)"].astype(int)
    df["USD Value"] = df["USD Value"].astype(int)

    return df