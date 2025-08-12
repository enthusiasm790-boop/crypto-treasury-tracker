import streamlit as st
import json, os, time, requests, gspread, pandas as pd
from google.oauth2.service_account import Credentials


CENTRAL_FILE = "data/prices.json"
LOCAL_FALLBACK_FILE = "data/last_prices.json"

def ensure_dir_for(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def load_last_prices(filename=None):
    if filename is None:
        filename = LOCAL_FALLBACK_FILE
    ensure_dir_for(filename)
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {"btc": 120_000, "eth": 4_000}

def save_last_prices(btc: int, eth: int, filename=None):
    if filename is None:
        filename = LOCAL_FALLBACK_FILE
    ensure_dir_for(filename)
    with open(filename, "w") as f:
        json.dump({"btc": btc, "eth": eth}, f)

@st.cache_data(ttl=300, show_spinner=False)  # 5 minutes
def read_central_prices_from_sheet() -> dict | None:
    """Read latest BTC/ETH USD from Google Sheet 'prices' worksheet."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        ws = client.open("master_table_v01").worksheet("prices")
        rows = ws.get_all_records(value_render_option="UNFORMATTED_VALUE")  # [{'asset':'BTC','usd':65000.0,'timestamp':...}, ...]
        if not rows:
            return None
        df = pd.DataFrame(rows)
        if df.empty:
            return None
        # latest value per asset by timestamp
        df = df.sort_values("timestamp")
        latest = df.groupby("asset")["usd"].last().to_dict()
        # normalize keys: {"BTC": 65000.0, "ETH": 3500.0}
        return {k.upper(): float(v) for k, v in latest.items()}
    except Exception:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_prices():
    """
    Preferred order for Option 1:
      1) Central Google Sheet (cached 5 min)
      2) CoinGecko API (to refresh local fallback)
      3) last_prices.json (final fallback)
    Returns (btc_price:int, eth_price:int)
    """
    # 1) central sheet
    central = read_central_prices_from_sheet()
    if central and ("BTC" in central and "ETH" in central):
        return int(central["BTC"]), int(central["ETH"])

    # 2) try API to refresh local fallback (useful locally or if sheet is momentarily unavailable)
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum", "vs_currencies": "usd"},
            timeout=8,
        )
        r.raise_for_status()
        js = r.json()
        btc = int(js["bitcoin"]["usd"]); eth = int(js["ethereum"]["usd"])
        save_last_prices(btc, eth)
        return btc, eth
    except Exception:
        pass

    # 3) last saved local file
    last = load_last_prices()
    return int(last.get("btc", 0)), int(last.get("eth", 0))

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