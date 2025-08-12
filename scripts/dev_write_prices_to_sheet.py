# scripts/dev_write_prices_to_sheet.py
import time, json
import gspread
from google.oauth2.service_account import Credentials

SHEET_NAME = "master_table_v01"
WS_NAME = "prices"
HEADERS = ["asset", "usd", "timestamp"]

def _client():
    with open("service_account.json", "r") as f:
        info = json.load(f)
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info, scopes=scope)
    return gspread.authorize(creds)

def _ensure_ws(gc):
    ss = gc.open(SHEET_NAME)
    try:
        ws = ss.worksheet(WS_NAME)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=WS_NAME, rows=50, cols=5)
        ws.update("A1:C1", [HEADERS])
    # ensure headers
    first = ws.get_values("A1:C1")
    if not first or first[0] != HEADERS:
        ws.update("A1:C1", [HEADERS])
    return ws

def upsert(ws, asset, usd, ts):
    rows = ws.get_all_records()  # [{'asset':..., 'usd':..., 'timestamp':...}, ...]
    index = {r["asset"]: i for i, r in enumerate(rows, start=2)}
    row = [asset, float(usd), int(ts)]
    if asset in index:
        ws.update(f"A{index[asset]}:C{index[asset]}", [row])
    else:
        ws.append_row(row, value_input_option="RAW")

if __name__ == "__main__":
    gc = _client()
    ws = _ensure_ws(gc)
    now = int(time.time())
    # Write obvious test values
    upsert(ws, "BTC", 65432.0, now)
    upsert(ws, "ETH", 3456.0,  now)
    print("Wrote test prices at", now)
