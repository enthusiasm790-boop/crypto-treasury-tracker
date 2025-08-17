import streamlit as st
import json, os, time, requests, gspread, pandas as pd
from google.oauth2.service_account import Credentials


CENTRAL_FILE = "data/prices.json"
LOCAL_FALLBACK_FILE = "data/last_prices.json"

ASSETS = ["BTC", "ETH", "XRP", "BNB", "SOL", "SUI", "LTC"]
COINGECKO_IDS = {"BTC":"bitcoin", "ETH":"ethereum", "XRP":"ripple", "BNB":"binancecoin", "SOL":"solana", "SUI": "sui", "LTC":"litecoin"}

DEFAULT_PRICES = {"BTC":120_000,"ETH":4_000,"XRP":3.50,"BNB":700.00,"SOL":150.00, "SUI":3.50, "LTC":120.00}

# Supply column row-wise (retrieved from Coingecko)
SUPPLY_CAPS = {
    "BTC": 20_000_000,  
    "ETH": 120_000_000,
    "XRP": 60_000_000_000,
    "BNB": 140_000_000,
    "SOL": 540_000_000,
    "LTC": 76_000_000,
    "LTC": 3_500_000_000,
}

def ensure_dir_for(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def load_last_prices(filename=None):
    filename = filename or LOCAL_FALLBACK_FILE
    ensure_dir_for(filename)
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
            return {k.upper(): float(v) for k, v in data.items()}
    return DEFAULT_PRICES.copy()


def save_last_prices(prices: dict, filename=None):
    filename = filename or LOCAL_FALLBACK_FILE
    ensure_dir_for(filename)
    out = {k.lower(): float(v) for k, v in prices.items() if k.upper() in ASSETS}
    with open(filename, "w") as f:
        json.dump(out, f)


@st.cache_data(ttl=300, show_spinner=False)  # 5 minutes
def read_central_prices_from_sheet() -> dict | None:
    """Read latest USD prices from Google 'prices' worksheet."""
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
        return {k.upper(): float(v) for k, v in latest.items() if pd.notna(v)}
            
    except Exception:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_prices():
    # 1 central sheet
    central = read_central_prices_from_sheet()  # returns keys like BTC ETH
    if central and all(a in central for a in ASSETS):
        return tuple(float(central[a]) for a in ASSETS)

    # 2 CoinGecko API then persist to local
    try:
        ids = ",".join(COINGECKO_IDS[a] for a in ASSETS)
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": ids, "vs_currencies": "usd"},
            timeout=8,
        )
        r.raise_for_status()
        js = r.json()
        prices = {a: float(js[COINGECKO_IDS[a]]["usd"]) for a in ASSETS}
        save_last_prices(prices)
        return tuple(prices[a] for a in ASSETS)
    except Exception:
        pass

    # 3 local fallback
    last = load_last_prices()
    return tuple(float(last.get(a, 0.0)) for a in ASSETS)


# Function to get raw treasury data from master sheets
# replaces load_units for a scalable sheet loop
def load_units():
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("master_table_v01")

    dfs = []
    for a in ASSETS:
        ws_name = f"aggregated_{a.lower()}_data"
        df_a = pd.DataFrame(sheet.worksheet(ws_name).get_all_records())
        dfs.append(df_a)

    df = pd.concat(dfs, ignore_index=True)
    df = df[["Entity Name","Entity Type","Country","Crypto Asset","Holdings (Unit)"]]
    df["Holdings (Unit)"] = (
        df["Holdings (Unit)"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    return df


def attach_usd_values(df_units: pd.DataFrame, prices_input):
    # accept either tuple in ASSETS order or dict keyed by symbols
    if isinstance(prices_input, tuple) or isinstance(prices_input, list):
        price_map = dict(zip(ASSETS, map(float, prices_input)))
    else:
        price_map = {k.upper(): float(v) for k, v in prices_input.items()}

    df = df_units.copy()
    df["USD Value"] = df["Crypto Asset"].map(price_map).fillna(0.0) * df["Holdings (Unit)"]
    return df


# Function to get historic treasury data from master sheets
@st.cache_data(ttl=900, show_spinner=False)
def load_historic_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("master_table_v01")

    dfs = []
    for a in ASSETS:  # e.g. ["BTC","ETH","XRP","BNB","SOL"]
        ws_name = f"historic_{a.lower()}"
        try:
            df_a = pd.DataFrame(sheet.worksheet(ws_name).get_all_records())
            if not df_a.empty:
                dfs.append(df_a)
        except gspread.WorksheetNotFound:
            continue

    if not dfs:
        return pd.DataFrame(columns=["Year","Month","Crypto Asset","Holdings (Unit)","USD Value","Date"])

    df = pd.concat(dfs, ignore_index=True)

    # keep standard columns
    cols = ["Year","Month","Crypto Asset","Holdings (Unit)","USD Value"]
    df = df[cols]

    # normalize asset codes
    df["Crypto Asset"] = df["Crypto Asset"].astype(str).str.upper()

    # numeric cleaning
    df["Year"]  = pd.to_numeric(df["Year"], errors="coerce")
    df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
    df = df[df["Year"] > 2023].dropna(subset=["Year","Month"])
    df["Year"]  = df["Year"].astype(int)
    df["Month"] = df["Month"].astype(int)

    # parse unit values with EU-style separators
    df["Holdings (Unit)"] = pd.to_numeric(
        df["Holdings (Unit)"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce"
    )
    df["USD Value"] = pd.to_numeric(df["USD Value"], errors="coerce")

    # month start date
    df["Date"] = pd.to_datetime({"year": df["Year"], "month": df["Month"], "day": 1}, errors="coerce")
    df = df.dropna(subset=["Date"])

    return df
