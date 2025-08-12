# scripts/dev_read_prices_from_sheet.py
import json, pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone

SHEET_NAME = "master_table_v01"
WS_NAME = "prices"

def read_latest():
    with open("service_account.json", "r") as f:
        info = json.load(f)
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info, scopes=scope)
    client = gspread.authorize(creds)
    ws = client.open(SHEET_NAME).worksheet(WS_NAME)
    rows = ws.get_all_records(value_render_option="UNFORMATTED_VALUE")  # <-- add this
    if not rows:
        return None, None
    df = pd.DataFrame(rows).sort_values("timestamp")
    latest = df.groupby("asset")["usd"].last().to_dict()
    latest = {k.upper(): float(v) for k, v in latest.items()}  # keep full precision
    ts = int(df["timestamp"].max())
    return latest, ts

if __name__ == "__main__":
    latest, ts = read_latest()
    print("Latest:", latest)
    if ts:
        print("As of (UTC):", datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"))
