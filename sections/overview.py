import streamlit as st
import pandas as pd
import numpy as np
import html

from urllib.parse import quote_plus

from modules.kpi_helpers import render_kpis
from analytics import log_table_render
from modules.ui import btc_b64, eth_b64, sol_b64, sui_b64, ltc_b64, xrp_b64
from modules.pdf_helper import _table_pdf_bytes

# Supply column row-wise
supply_caps = {
    "BTC": 20_000_000,  
    "ETH": 120_000_000,
    "XRP": 60_000_000_000,
    "BNB": 140_000_000,
    "SOL": 540_000_000,
    "SUI": 3_500_000_000,
    "LTC": 76_000_000,
    }

TRUE_DAT_WHITELIST = {
    "BTC": {"MSTR", "CEP", "BSTR", "MTPLF", "CCCM", "ALCPB", "OTCMKTS:HOGPF", "BTCT.V", "MKBN", "ABTC", "KOSDAQ:288330"},
    "ETH": {"BMNR", "SBET", "ETHM", "ETHZ", "FGNX", "GAME", "CTARF"},
    "SOL": {"UPXI", "DFDV", "STSS", "KIDZ", "STKE"},
    "LTC": {"LITS"},
    #"XRP": {},
    #"SUI": {},
}

def _df_auto_height(n_rows: int, row_px: int = 35) -> int:
    # header ≈ one row + thin borders
    return int((n_rows + 1) * row_px + 3)

# requires: pip install pillow
def _best_text_on(bg_rgb: tuple[int,int,int]) -> tuple[int,int,int]:
    r, g, b = [c/255.0 for c in bg_rgb]
    def _lin(c): return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
    L = 0.2126*_lin(r) + 0.7152*_lin(g) + 0.0722*_lin(b)
    contrast_white = (1.0 + 0.05) / (L + 0.05)
    contrast_black = (L + 0.05) / 0.05
    return (255,255,255) if contrast_white >= contrast_black else (0,0,0)


def _badge_svg_uri(text: str,
                   bg_rgb: tuple[int,int,int],
                   h: int = 18,
                   pad_x: int = 5,
                   radius: int = 7) -> str:
    """Return a data:image/svg+xml;utf8 URI for a rounded, vector 'pill'."""
    # rough text width estimate (keeps sizing stable without font metrics)
    font_size = 12  # looks good for h≈18
    est_tw = max(12, int(len(text) * font_size * 0.60))
    w = est_tw + 2 * pad_x

    tr, tg, tb = _best_text_on(bg_rgb)
    r, g, b = bg_rgb
    txt = html.escape(text)

    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>"
        f"<rect x='0' y='0' width='{w}' height='{h}' rx='{radius}' ry='{radius}' "
        f"fill='rgb({r},{g},{b})'/>"
        f"<text x='{w/2}' y='{h/2}' dominant-baseline='middle' text-anchor='middle' "
        f"fill='rgb({tr},{tg},{tb})' font-family='-apple-system,system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif' "
        f"font-size='{font_size}' font-weight='600'>{txt}</text>"
        f"</svg>"
    )
    return "data:image/svg+xml;utf8," + svg


def render_overview():
    df = st.session_state["data_df"]

    # KPIs
    render_kpis(df)


    with st.container(border=True):
        st.markdown("#### Crypto Treasury Ranking", help="Ranked view of entities by digital asset treasury holdings.")

        table = df.copy()
        table = table.sort_values("USD Value", ascending=False).reset_index(drop=True)
        table.index = table.index + 1
        table.index.name = "Rank"

        table["Holdings (Unit)"] = table["Holdings (Unit)"].round(0)
        table["USD Value"] = table["USD Value"].round(0)

        table["% of Supply"] = table.apply(
            lambda row: row["Holdings (Unit)"] / supply_caps.get(row["Crypto Asset"], 1) * 100,
            axis=1
        ).round(2)

        cols = list(table.columns)
        if "Holdings (Unit)" in cols and "% of Supply" in cols:
            cols.remove("% of Supply")
            insert_pos = cols.index("Holdings (Unit)") + 1
            cols.insert(insert_pos, "% of Supply")
            table = table[cols]

        # asset toggle
        options = ["All"] + sorted(table["Crypto Asset"].unique().tolist())
        c1_kpi, c2_kpi, c3_kpi, c4_kpi = st.columns([1,0.5,0.5,1])
        
        with c1_kpi:
            asset_choice = st.radio("Select Asset List", options=options, index=0, horizontal=True, label_visibility="visible", key="tbl_asset_filter")

        c1, c2, c3 = st.columns(3)

        with c1:
            row_count = st.selectbox(
                "Select Rows to Display",
                options=[5, 10, 20, 25, 50, 100],
                index=2,
                key="tbl_rows",
            )
            
        with c2:
            if "ui_entity_type" not in st.session_state:
                st.session_state["ui_entity_type"] = st.session_state.get("flt_entity_type", "All")
            sel_et = st.selectbox(
                "Select Entity Type",
                options=st.session_state["opt_entity_types"],
                key="ui_entity_type",
            )
            st.session_state["flt_entity_type"] = sel_et

        with c3:
            if "ui_country" not in st.session_state:
                st.session_state["ui_country"] = st.session_state.get("flt_country", "All")
            sel_co = st.selectbox(
                "Select Country/Region",
                options=st.session_state["opt_countries"],
                key="ui_country",
            )
            st.session_state["flt_country"] = sel_co

        # apply global filters plus the local asset toggle
        filtered = table.copy()

        assets_sel = [asset_choice] if asset_choice != "All" else st.session_state.get("flt_assets", st.session_state["opt_assets"])
        filtered = filtered[filtered["Crypto Asset"].isin(assets_sel)]


        et = st.session_state.get("flt_entity_type", "All")
        if et != "All":
            filtered = filtered[filtered["Entity Type"] == et]

        co = st.session_state.get("flt_country", "All")
        if co != "All":
            filtered = filtered[filtered["Country"] == co]

        filtered = filtered[filtered["USD Value"] > 0]

        # ensure uppercase tickers for matching
        filtered["Ticker"] = filtered["Ticker"].astype(str).str.upper()

        # build the active whitelist based on current asset selection
        if asset_choice != "All":
            active_whitelist = set().union(*(TRUE_DAT_WHITELIST.get(a, set()) for a in [asset_choice]))
        else:
            active_assets = st.session_state.get("flt_assets", st.session_state["opt_assets"])
            active_whitelist = set().union(*(TRUE_DAT_WHITELIST.get(a, set()) for a in active_assets))

        # valid rows for averages
        valid = filtered.replace([np.inf, -np.inf], np.nan)
        valid = valid[(valid["mNAV"] > 0) & (valid["TTMCR"] > 0)]

        # existing KPIs
        avg_mnav = valid["mNAV"].mean()
        avg_ttmcr = valid["TTMCR"].mean()

        # new KPI for true DATCOs only
        valid_true = valid[valid["Ticker"].isin(active_whitelist)]
        avg_mnav_true = valid_true["mNAV"].mean()

        with c2_kpi:
            st.metric(
                "Avg. mNAV",
                f"{avg_mnav:,.2f}",
                help="Average market-to-NAV multiple across the current selection. mNAV is calculated by dividing the current market cap by crypto net asset value (NAV) in USD. A value above 1 means the equity trades at a premium to the underlying crypto NAV, while below 1 signals a discount. For example, an mNAV of 1.20 represents a 20% premium."
            )

        with c3_kpi:
            st.metric(
                "Avg. DATCO-only mNAV",
                f"{avg_mnav_true:,.2f}",
                help="Average mNAV filtered for Digital Asset Treasury (DAT) vehicles only, excluding companies that use crypto assets for operational or other functional purposes (e.g., mining activities). Current DATs include the following tickers (where data is publicly available): MSTR, CEP, BSTR, MTPLF, CCCM, ALCPB, HOGPF, BTCT.V, MKBN, ABTC, 288330.KQ, BMNR, SBET, ETHM, ETHZ, FGNX, GAME, CTARF, UPXI, DFDV, STSS, KIDZ, STKE, and LITS."
            )

        with c4_kpi:
            st.metric(
                "Avg. Treasury to Market Cap Ratio (TTMCR)",
                f"{avg_ttmcr:,.2f}%",
                help="The Treasury-to-Market Cap Ratio (TTMCR) shows the share of a company's value represented by held crypto reserves. It is calculated by dividing the crypto treasury (USD value) by the company's current market cap, shown as a percentage. For example, a TTMCR of 5% means that 5% of the company's market cap is backed by crypto assets."
            )

        sub = filtered.head(row_count)

        display = sub.copy()

        # show dashes for missing values
        display["Ticker"] = display["Ticker"].replace({"": "-"}).astype("string").fillna("-")

        # mark rows with no market cap or no ticker for display-only fallbacks
        _no_metrics = display["Market Cap"].isna() | display["Ticker"].isna()

        # display-only formatted metrics with dashes when not available
        display["mNAV_disp"]    = np.where(_no_metrics, "-", display["mNAV"].map(lambda v: f"{v:.2f}" if pd.notna(v) else "-"))
        display["Premium_disp"] = np.where(_no_metrics, "-", display["Premium"].map(lambda v: f"{v:.2f}%" if pd.notna(v) else "-"))
        display["TTMCR_disp"]   = np.where(_no_metrics, "-", display["TTMCR"].map(lambda v: f"{v:.2f}%" if pd.notna(v) else "-"))

        logo_map = {
            "BTC": f"data:image/png;base64,{btc_b64}",
            "ETH": f"data:image/png;base64,{eth_b64}",
            "SOL": f"data:image/png;base64,{sol_b64}",
            "XRP": f"data:image/png;base64,{xrp_b64}",
            "SUI": f"data:image/png;base64,{sui_b64}",
            "LTC": f"data:image/png;base64,{ltc_b64}",
        }
        display["Crypto Asset"] = display["Crypto Asset"].map(lambda a: logo_map.get(a, ""))

        def pretty_usd(x):
            if pd.isna(x):
                return "-"
            ax = abs(x)
            if ax >= 1e12:  return f"${x/1e12:.2f}T"
            if ax >= 1e9:  return f"${x/1e9:.2f}B"
            if ax >= 1e6:  return f"${x/1e6:.2f}M"
            if ax >= 1e3:  return f"${x/1e3:.2f}K"
            return f"${x:,.0f}"

        display["Market Cap"] = display["Market Cap"].map(pretty_usd)
        display["USD Value"] = display["USD Value"].map(pretty_usd)

        display = display[[
            "Crypto Asset","Entity Name","Ticker","Market Cap","Entity Type","Country",
            "Holdings (Unit)","USD Value","mNAV_disp","Premium_disp","TTMCR_disp","% of Supply"
        ]]


        _type_palette = {"Public Company": (123, 197, 237), # blue 
                        "Private Company": (232, 118, 226), # rose 
                        "DAO": (237, 247, 94), # amber 
                        "Foundation": (34, 197, 94), # green 
                        "Government": (245, 184, 122), # slate 
                        "Other": (250, 250, 250), # white
                        }

        _badge_map = {k: _badge_svg_uri(k, v, h=28) for k, v in _type_palette.items()}

        display["Entity Type"] = display["Entity Type"].map(
            lambda t: _badge_map.get(t, _badge_map["Other"])
        )

        rows = min(row_count, len(display))
        height = _df_auto_height(rows)  # no vertical scrollbar for selected rows


        st.dataframe(
            display,
            use_container_width=True,
            height=height,
            column_config={
                "Crypto Asset": st.column_config.ImageColumn("Crypto Asset", width="small"),
                #"Market Cap": st.column_config.NumberColumn("Market Cap", format="$%d"),
                "Market Cap": st.column_config.TextColumn("Market Cap", width="small"),    # compact view
                "Entity Type": st.column_config.ImageColumn("Entity Type", width="medium"),
                "Holdings (Unit)": st.column_config.NumberColumn("Holdings (Unit)", format="%d"),
                #"USD Value": st.column_config.NumberColumn("USD Value", format="$%d"),
                "USD Value": st.column_config.TextColumn("USD Value", width="small"),    # compact view
                "mNAV_disp":    st.column_config.TextColumn("mNAV", width="small"),
                "Premium_disp": st.column_config.TextColumn("Premium", width="small"),
                "TTMCR_disp":   st.column_config.TextColumn("TTMCR", width="small"),
                "% of Supply": st.column_config.ProgressColumn("% of Supply", min_value=0, max_value=100, format="%.2f%%"),
            },
        )

        log_table_render("global_summary", "overview_table", len(display))

        # PDF download of the filtered view
        fname_asset = "all" if asset_choice == "All" else asset_choice.lower()
        pdf_bytes = _table_pdf_bytes(
            sub, logo_map, title=f"Crypto Treasury Top {len(sub)} Ranking - {fname_asset.upper()}"
        )

        if st.download_button(
            "Download List as PDF",
            data=pdf_bytes,
            type="primary",
            file_name=f"crypto_treasury_list_{fname_asset}_top{len(sub)}.pdf",
            mime="application/pdf",
            key="dl_overview_table_pdf",
        ):
            from analytics import log_event
            log_event("download_click", {
                "target": "table_pdf",
                "file_name": f"crypto_treasury_list_{fname_asset}_top{len(sub)}.pdf",
                "rows_exported": int(len(sub)),
            })


    # Last update info
    st.caption("*Last treasury data base update: September 12, 2025*")
