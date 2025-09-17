import streamlit as st
import pandas as pd
import numpy as np
import html

from urllib.parse import quote_plus

from modules.kpi_helpers import render_kpis
from analytics import log_table_render
from modules.ui import btc_b64, eth_b64, sol_b64, sui_b64, ltc_b64, xrp_b64, hype_b64
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
    "HYPE": 270_000_000,
    }

TRUE_DAT_WHITELIST = {
    "BTC": {"Strategy Inc.", "Twenty One Capital (XXI)", "Bitcoin Standard Treasury Company", "Metaplanet Inc.", "ProCap Financial, Inc", "Capital B", "H100 Group", 
            "Bitcoin Treasury Corporation", "Treasury B.V.", "American Bitcoin Corp.", "Parataxis Holdings LLC", "Strive Asset Management", "ArcadiaB", "Cloud Ventures",
            "Stacking Sats, Inc.", "Melanion Digital", "Sequans Communications S.A.", "Semler Scientific, Inc.", "Africa Bitcoin Corporation"}, 
    "ETH": {"BitMine Immersion Technologies, Inc.", "SharpLink Gaming", "The Ether Machine", "ETHZilla Corporation", "FG Nexus", "GameSquare Holdings", "Centaurus Energy Inc."},
    "SOL": {"Forward Industries, Inc.", "Upexi, Inc.", "DeFi Development Corp.", "Sharps Technology, Inc.", "Classover Holdings, Inc.", "Sol Strategies, Inc.", "Sol Treasury Corp."},
    "LTC": {"Lite Strategy, Inc."},
    "XRP": set(),
    "SUI": set(),
    "HYPE": {"Hyperliquid Strategies Inc", "Hyperion DeFi, Inc."},
}


def pretty_usd(x):
    if pd.isna(x):
        return "-"
    ax = abs(x)
    if ax >= 1e12:  return f"${x/1e12:.2f}T"
    if ax >= 1e9:  return f"${x/1e9:.2f}B"
    if ax >= 1e6:  return f"${x/1e6:.2f}M"
    if ax >= 1e3:  return f"${x/1e3:.2f}K"
    return f"${x:,.0f}"

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

        c1_kpi, c2_kpi, c3_kpi, c4_kpi, c5_kpi = st.columns([1,0.5,0.5,0.5,0.5])

        # all list option
        options = ["All", "DATCOs"] + sorted(table["Crypto Asset"].dropna().unique().tolist())

        with c1_kpi:
            list_choice = st.radio(
                "Select List",
                options=options,
                index=0,
                horizontal=True,
                label_visibility="visible",
                key="tbl_asset_filter",
            )

        # apply selection
        if list_choice == "DATCOs":
            # union whitelist across assets present in the current table
            assets_present = sorted(table["Crypto Asset"].dropna().unique().tolist())
            whitelist_sets = [TRUE_DAT_WHITELIST.get(a, set()) for a in assets_present]
            active_whitelist = set().union(*whitelist_sets) if whitelist_sets else set()

            if "Entity Name" in table.columns:
                names_upper = table["Entity Name"].astype(str)
                table = table[names_upper.isin(active_whitelist)]  # <<< filter TABLE, not df!

            asset_choice = "All"

        else:
            asset_choice = list_choice
            if asset_choice != "All":
                table = table[table["Crypto Asset"] == asset_choice]


        c1, c2, c3, c4 = st.columns(4)

        # --- search by entity name ---
        with c1:
            name_query = st.text_input(
                "Search Entity",
                value="",
                placeholder="Type a company name…",
                key="tbl_search",
                help="Filter the list by entity name."
            )

        if name_query:
            table_search = table[table["Entity Name"].astype(str).str.contains(name_query, case=False, na=False)]
        else:
            table_search = table

        len_table = table_search.shape[0]

        if list_choice == "DATCOs":
            default_rows = len_table  # always show full set
        elif list_choice == "All":
            default_rows = min(100, len_table)
        else:
            default_rows = min(100, len_table)
            
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

        with c4:
            row_count = st.number_input(
                f"Adjust List",
                1, max(1, len_table), default_rows,  # guard: max at least 1
                help="Select number of crypto treasury holders to display, sorted by USD value.",
                key="tbl_rows",
            )

        # apply global filters plus the local asset toggle
        filtered = table_search.copy()

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

        # Aggregate mNAV + TTMCR KPIs
        avg_mnav = valid["mNAV"].median()
        avg_ttmcr = valid["TTMCR"].median()
        valid_true = valid[valid["Entity Name"].isin(active_whitelist)]
        avg_mnav_true = valid_true["mNAV"].median()

        # DATCO
        sub_2 = filtered.head(int(row_count)).copy()

        filtered_count = sub_2.shape[0]
        # recompute DATCO mask on the sliced data
        names_sub = sub_2["Entity Name"].astype(str)
        datco_mask_sub = names_sub.isin(active_whitelist)

        # --- DATCO Adoption (count + % of Crypto-NAV) ---
        tickers_upper = filtered["Entity Name"].astype(str)
        datco_mask    = tickers_upper.isin(active_whitelist)

        # number of DATCO companies in current selection
        datco_count   = tickers_upper[datco_mask].nunique()

        nav_total = float(sub_2["USD Value"].sum())
        nav_datco = float(sub_2.loc[datco_mask_sub, "USD Value"].sum())

        def _fmt(x, pct=False):
            if x is None or (isinstance(x, float) and np.isnan(x)):
                return "-"
            return f"{x:,.2f}%" if pct else f"{x:,.2f}"

        with c2_kpi:
            with st.container(border=True):
                st.metric(
                    "Total Crypto-NAV (selected)",
                    f"{pretty_usd(nav_total)}",
                    help=("Total USD value of selected crypto treasury entities (Crypto-NAV).")
                )

        with c3_kpi:
            with st.container(border=True):
                st.metric(
                    f"Number of Entities (Total: {len_table})",
                    filtered_count,
                    help=("Current number view of selected rows (entities).")
                )

        with c4_kpi:
            with st.container(border=True):
                st.metric(
                    "DATCO mNAV (Median)",
                    f"{_fmt(avg_mnav_true)}×",
                    help="Median market to net asset value (mNAV) filtered for Digital Asset Treasury Companies (DATCO) only, excluding entities that use crypto assets for other strategic or operational purposes (e.g., mining activities). Current DATCOs include the following tickers (where data is publicly available): MSTR, NASDAQ:CEP, BSTR, MTPLF, CCCM, ALCPB, OTCMKTS:HOGPF, BTCT.V, MKBN, ABTC, 288330.KQ, BMNR, SBET, ETHM, ETHZ, FGNX, GAME, CTARF, UPXI, DFDV, STSS, KIDZ, STKE, and LITS."
                )

        with c5_kpi:
            with st.container(border=True):
                st.metric(
                    "TTMCR (Median)",
                    _fmt(avg_ttmcr, pct=True),
                    help="The Treasury-to-Market Cap Ratio (TTMCR) shows the share of a company's value represented by held crypto reserves (unweighted). It is calculated by dividing the crypto treasury (USD value) by the company's current market cap, shown as a percentage. For example, a TTMCR of 5% means that 5% of the company's market cap is backed by crypto assets."
                )

        sub = filtered.head(row_count)
        sub = sub.reset_index(drop=True)
        sub.index = sub.index + 1
        sub.index.name = "Rank"

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
            "HYPE": f"data:image/png;base64,{hype_b64}",
        }
        display["Crypto Asset"] = display["Crypto Asset"].map(lambda a: logo_map.get(a, ""))

        display["Market Cap"] = display["Market Cap"].map(pretty_usd)
        display["USD Value"] = display["USD Value"].map(pretty_usd)

        display = display[[
            "Entity Name", "Ticker", "Entity Type", "Country",                      # Meta data
            "Crypto Asset", "Holdings (Unit)", "% of Supply", "USD Value",                # Crypto data
            "Market Cap", "mNAV_disp", "Premium_disp", "TTMCR_disp"                 # Market data
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

        st.markdown(
            """
            <style>
            /* Right-align selected columns in st.dataframe */
            [data-testid="stDataFrame"] td:nth-child(8),
            [data-testid="stDataFrame"] td:nth-child(9),
            [data-testid="stDataFrame"] td:nth-child(10),
            [data-testid="stDataFrame"] td:nth-child(11),
            [data-testid="stDataFrame"] td:nth-child(12) {
                text-align: right !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.dataframe(
            display,
            width="stretch",
            height=height,
            column_config={
                "Crypto Asset": st.column_config.ImageColumn("Crypto Asset", width="small"),
                #"Market Cap": st.column_config.NumberColumn("Market Cap", format="$%d"),
                "Entity Type": st.column_config.ImageColumn("Entity Type", width="medium"),
                "Holdings (Unit)": st.column_config.NumberColumn("Holdings", format="%d"),
                "% of Supply": st.column_config.ProgressColumn("% of Supply", min_value=0, max_value=100, format="%.2f%%"),
                #"USD Value": st.column_config.NumberColumn("USD Value", format="$%d"),
                "Market Cap": st.column_config.TextColumn("Market Cap", width="small"),
                "USD Value": st.column_config.TextColumn("Crypto-NAV", width="small"),
                "mNAV_disp":    st.column_config.TextColumn("mNAV", width="small"),
                "Premium_disp": st.column_config.TextColumn("Premium", width="small"),
                "TTMCR_disp":   st.column_config.TextColumn("TTMCR", width="small"),
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
    #st.caption("*Last treasury data base update: September 14, 2025*")
