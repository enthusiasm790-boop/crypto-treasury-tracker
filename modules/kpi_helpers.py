import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64
from modules.ui import COLORS 
from modules.data_loader import ASSETS


def load_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

logo_b64 = load_base64_image("assets/ctt-symbol.svg")


def format_change(value):
    if value > 0:
        return f"↗ {value:.1f}%", "green"
    elif value < 0:
        return f"↘ {value:.1f}%", "red"
    else:
        return f"{value:.1f}%", "white"

# Summary KPIs
def render_kpis(df):

    df = df[(df["USD Value"] > 0) | (df["Holdings (Unit)"] > 0)]

    agg = (
        df.groupby("Crypto Asset")
        .agg(usd=("USD Value","sum"),
            entities=("Entity Name","nunique"),
            units=("Holdings (Unit)","sum"))
        .reindex(ASSETS, fill_value=0)
    )

    total_usd = agg["usd"].sum()
    btc_usd, eth_usd = agg.at["BTC","usd"], agg.at["ETH","usd"]
    other_usd = agg.loc[~agg.index.isin(["BTC","ETH"]), "usd"].sum()

    total_entities = df["Entity Name"].nunique()
    btc_entities, eth_entities = agg.at["BTC","entities"], agg.at["ETH","entities"]
    other_entities = df[df["Crypto Asset"].isin([a for a in ASSETS if a not in ["BTC","ETH"]])]["Entity Name"].nunique()

    btc_units, eth_units = agg.at["BTC","units"], agg.at["ETH","units"]
    xrp_units, bnb_units, sol_units = agg.at["XRP","units"], agg.at["BNB","units"], agg.at["SOL","units"]

    # percentages for USD stacked bar
    usd_pct = {a: (agg.at[a,"usd"] / total_usd if total_usd else 0.0) for a in ASSETS}


    # KPI layout
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.metric("Total USD Value", f"${total_usd:,.0f}", help="Aggregate USD value of all tracked crypto reserves across entities, based on live market pricing.")

            btc_pct = btc_usd / total_usd
            eth_pct = eth_usd / total_usd

            st.markdown(
                f"""
                <div style='background-color:#1e1e1e;border-radius:8px;height:20px;width:100%;display:flex;overflow:hidden;'>
                    {''.join(
                        f"<div title='{a} ${agg.at[a,'usd']/1e9:.1f}B: ({usd_pct[a]*100:.1f}%)' "
                        f"style='width:{usd_pct[a]*100:.1f}%;background-color:{COLORS[a]};'></div>"
                        for a in ASSETS if usd_pct[a] > 0
                    )}
                </div>
                <div style='margin-top:8px;margin-bottom:5px;font-size:16px;color:#aaa;'>
                    BTC: ${btc_usd/1e9:.1f}B | ETH: ${eth_usd/1e9:.1f}B | Other: ${other_usd/1e9:.1f}B
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("")


    with col2:
        with st.container(border=True):
            st.metric("Total Unique Entities", f"{total_entities}", help="Entities holding crypto assets directly, excluding ETFs and indirect vehicles. Note: some entities hold both and are only counted once.")

            ent_pct = {
                "BTC": (btc_entities / total_entities if total_entities else 0.0),
                "ETH": (eth_entities / total_entities if total_entities else 0.0),
                # collapse all non‑BTC/ETH into one segment for readability
                "Other": ((other_entities / total_entities) if total_entities else 0.0),
            }
            ENT_COUNTS = {"BTC": btc_entities, "ETH": eth_entities, "Other": other_entities}
            ENT_COLORS = {"BTC": COLORS["BTC"], "ETH": COLORS["ETH"], "Other": "white"}

            st.markdown(
                f"""
                <div style='background-color:#1e1e1e;border-radius:8px;height:20px;width:100%;display:flex;overflow:hidden;'>
                    {''.join(
                        f"<div title='{k}: {ENT_COUNTS[k]} ({ent_pct[k]*100:.1f}%)' "
                        f"style='width:{ent_pct[k]*100:.1f}%;background-color:{ENT_COLORS[k]};'></div>"
                        for k in ["BTC","ETH","Other"] if ent_pct[k] > 0
                    )}
                </div>
                <div style='margin-top:8px;margin-bottom:5px;font-size:16px;color:#aaa;'>
                    BTC: {btc_entities} | ETH: {eth_entities} | Other: {other_entities}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("")


    with col3:
        with st.container(border=True):
            st.metric("% of Supply", f"", help="Share of total circulating supply held by tracked entities (BTC ≈ 20M, ETH ≈ 120M).")

            btc_pct = btc_units / 20_000_000
            eth_pct = eth_units / 120_000_000

            # BTC Donut
            fig_btc = go.Figure(data=[go.Pie(
                labels=["Held", "Remaining"],
                values=[btc_pct, 1 - btc_pct],
                hole=0.7,
                marker_colors=["#f7931a", "#2c2c2c"],
                textinfo="none",
                hoverinfo="skip",
                sort=False
            )])
            fig_btc.update_layout(
                width=100, height=105,
                margin=dict(t=0, b=0, l=0, r=0),
                showlegend=False,
                annotations=[dict(
                    text=f"<b>BTC</b><br>{btc_pct:.2%}",
                    x=0.5, y=0.5, font_size=17,
                    showarrow=False, font_color="white"
                )]
            )

            # ETH Donut
            fig_eth = go.Figure(data=[go.Pie(
                labels=["Held", "Remaining"],
                values=[eth_pct, 1 - eth_pct],
                hole=0.7,
                marker_colors=["#A9A9A9", "#2c2c2c"],
                textinfo="none",
                hoverinfo="skip",
                sort=False
            )])
            fig_eth.update_layout(
                width=100, height=105,
                margin=dict(t=0, b=0, l=0, r=0),
                showlegend=False,
                annotations=[dict(
                    text=f"<b>ETH</b><br>{eth_pct:.2%}",
                    x=0.5, y=0.5, font_size=17,
                    showarrow=False, font_color="white"
                )]
            )

            # Donuts side-by-side without resizing parent box
            donut_col1, donut_col2 = st.columns([1, 1])
            with donut_col1:
                st.plotly_chart(fig_btc)
            with donut_col2:
                st.plotly_chart(fig_eth)

# Historic KPIs
def _latest_and_prev_dates(dates: pd.Series):
    """Return (latest_date, previous_available_date) from a series of pd.Timestamp."""
    uniq = sorted(dates.dropna().unique())
    if not uniq:
        return None, None
    if len(uniq) == 1:
        return uniq[-1], None
    return uniq[-1], uniq[-2]

def _year_end_total(df: pd.DataFrame, year: int, value_col: str):
    """Total at year-end (December of `year`) if present, else None."""
    if df.empty:
        return None
    ydf = df[(df["Year"] == year) & (df["Month"] == 12)]
    if ydf.empty:
        return None
    return float(ydf[value_col].sum())

def _fmt_change(x: float):
    sign = "▲" if x > 0 else ("▼" if x < 0 else "—")
    return f"{x:+.1f}% {sign}"

def _pct_change(old, new):
    """Return float % change or None if invalid baseline."""
    if old is None or old <= 0:
        return None
    return (new - old) / old * 100.0

def _fmt_delta(x: float) -> str:
    """Format a % for st.metric(delta=...) or return None."""
    if x is None:
        return None
    return f"{x:+.1f}%"

def _fmt_pct_value(x, na="N/A"):
    """Render a percentage or N/A if baseline missing."""
    return f"{x:.1f}%" if (x is not None and np.isfinite(x)) else na
    
def _compute_current_vs_last(df_current: pd.DataFrame, df_hist: pd.DataFrame, assets: list[str]):
    """
    Returns:
      current_usd, last_usd, usd_delta_pct,
      current_units (if single asset), last_units, units_delta_pct
    """
    # current snapshot (already priced via attach_usd_values)
    cur = df_current[df_current["Crypto Asset"].isin(assets)]
    current_usd = float(cur["USD Value"].sum())

    current_units = None
    if len(assets) == 1:
        a = assets[0]
        current_units = float(cur.loc[cur["Crypto Asset"] == a, "Holdings (Unit)"].sum())

    # last stored month in historic
    hist = df_hist[df_hist["Crypto Asset"].isin(assets)]
    if hist.empty:
        return current_usd, None, None, current_units, None, None

    last_date = pd.to_datetime(hist["Date"]).max()
    last_month = hist[pd.to_datetime(hist["Date"]) == last_date]

    last_usd = float(last_month["USD Value"].sum())

    last_units = None
    units_delta_pct = None
    if len(assets) == 1:
        a = assets[0]
        last_units = float(last_month.loc[last_month["Crypto Asset"] == a, "Holdings (Unit)"].sum())
        if last_units and last_units > 0 and current_units is not None:
            units_delta_pct = (current_units - last_units) / last_units * 100.0

    usd_delta_pct = (current_usd - last_usd) / last_usd * 100.0 if (last_usd is not None and last_usd > 0) else None

    return current_usd, last_usd, usd_delta_pct, current_units, last_units, units_delta_pct


def render_historic_kpis(df_filtered: pd.DataFrame):
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)

        if df_filtered.empty:
            col1.metric("Monthly Change (USD)", "N/A")
            col2.metric("YTD Change (USD)", "N/A")
            col3.metric("CAGR (USD)", "N/A")
            #st.write("")  # spacer
            c1, c2, c3 = st.columns(3)
            c1.metric("Monthly Change (units)", "N/A")
            c2.metric("YTD Change (units)", "N/A")
            c3.metric("CAGR (units)", "N/A")
            return

        # Working frames
        dfw = df_filtered.copy()  # respects current UI filters
        df_full = st.session_state.get("historic_df", dfw)  # for prior Dec baselines
        
        # ensure datetime (no-op if already)
        dfw["Date"] = pd.to_datetime(dfw["Date"])
        df_full["Date"] = pd.to_datetime(df_full["Date"])

        # Dates
        latest_date, prev_date = _latest_and_prev_dates(dfw["Date"])
        assets_in_scope = sorted(dfw["Crypto Asset"].dropna().unique().tolist())

        # --- NEW: Current snapshot vs last stored month (USD), consistent across sections
        cur_usd, last_usd, cur_vs_last_usd_pct, cur_units, last_units, cur_vs_last_units_pct = _compute_current_vs_last(
            st.session_state["data_df"],   # current priced snapshot
            st.session_state["historic_df"],  # full historic
            assets_in_scope
        )

        # --- Aggregate USD KPIs (always shown) ---
        latest_total_usd = float(dfw.loc[dfw["Date"] == latest_date, "USD Value"].sum()) if latest_date is not None else 0.0
        prev_total_usd   = float(dfw.loc[dfw["Date"] == prev_date,   "USD Value"].sum()) if prev_date   is not None else None

        # Monthly % (USD)
        monthly_change_usd = _pct_change(prev_total_usd, latest_total_usd)

        # YTD % (USD) vs prior Dec (use full history but same asset scope)
        latest_year = int(pd.to_datetime(latest_date).year) if latest_date is not None else None
        ytd_base = df_full[df_full["Crypto Asset"].isin(assets_in_scope)] if assets_in_scope else df_full
        prior_dec_total_usd = _year_end_total(ytd_base, latest_year - 1, "USD Value") if latest_year else None
        ytd_change_usd = _pct_change(prior_dec_total_usd, latest_total_usd)


        # --- CAGR window from full history (not the UI-filtered window) ---
        df_cagr_base = df_full[df_full["Crypto Asset"].isin(assets_in_scope)] if assets_in_scope else df_full

        months = pd.to_datetime(df_cagr_base["Date"]).dt.to_period("M").sort_values().unique()
        if len(months) == 0:
            # ultra-guard: no months found
            start_period = end_period = None
            first_total_usd_cagr = latest_total_usd_cagr = 0.0
            n_months_cagr = 0
            cagr_usd = None
        else:
            if len(months) >= 12:
                start_period = months[-12]
                end_period   = months[-1]
            else:
                start_period = months[0]
                end_period   = months[-1]

            start_mask = df_cagr_base["Date"].dt.to_period("M") == start_period
            end_mask   = df_cagr_base["Date"].dt.to_period("M") == end_period

            first_total_usd_cagr  = float(df_cagr_base.loc[start_mask, "USD Value"].sum())
            latest_total_usd_cagr = float(df_cagr_base.loc[end_mask,   "USD Value"].sum())
            n_months_cagr = (end_period.year - start_period.year) * 12 + (end_period.month - start_period.month)
            cagr_usd = (((latest_total_usd_cagr / first_total_usd_cagr) ** (12 / n_months_cagr)) - 1) * 100.0 \
                if (first_total_usd_cagr is not None and first_total_usd_cagr > 0 and n_months_cagr > 0) else None

        col1.metric(
            "Current Value (USD) vs Last Month",
            value=f"${cur_usd:,.0f}",
            delta=(f"{cur_vs_last_usd_pct:+.1f}%" if cur_vs_last_usd_pct is not None else None),
            delta_color="normal",
            help="Current total USD value under the selected filters, with % change vs the last month. Note: Adjustment of −91,331 BTC applied for historical consistency with latest reported holdings due to data source inconsistencies."
        )

        col2.metric(
            "YTD Change (USD)",
            value=_fmt_pct_value(ytd_change_usd),
            delta_color="normal",
            help="Change since prior year‑end (Dec), based on USD value."
        )

        col3.metric(
            "CAGR (USD)",
            value=_fmt_pct_value(cagr_usd),
            help=("Compound annual growth rate based on USD value. "
                "Uses last 12 months if available, otherwise all available data.")
        )


        # --- Units KPIs only when exactly ONE asset is selected ---

        single_asset = assets_in_scope[0] if len(assets_in_scope) == 1 else None

        with st.expander("Unit KPIs (single asset)", expanded = (single_asset is not None)):

            if single_asset:
                dfw_asset = dfw[dfw["Crypto Asset"] == single_asset]

                latest_units = float(dfw_asset.loc[dfw_asset["Date"] == latest_date, "Holdings (Unit)"].sum()) if latest_date is not None else 0.0
                prev_units   = float(dfw_asset.loc[dfw_asset["Date"] == prev_date,   "Holdings (Unit)"].sum()) if prev_date   is not None else None

                monthly_change_units = _pct_change(prev_units, latest_units)

                ytd_base_asset = ytd_base[ytd_base["Crypto Asset"] == single_asset]
                prior_dec_units = _year_end_total(ytd_base_asset, latest_year - 1, "Holdings (Unit)") if latest_year else None
                ytd_change_units = _pct_change(prior_dec_units, latest_units)

                # Units CAGR uses SAME window as USD CAGR but restricted to the single asset
                if start_period is not None and n_months_cagr > 0:
                    df_cagr_asset = df_cagr_base[df_cagr_base["Crypto Asset"] == single_asset]
                    first_units_cagr  = float(df_cagr_asset.loc[df_cagr_asset["Date"].dt.to_period("M") == start_period, "Holdings (Unit)"].sum())
                    latest_units_cagr = float(df_cagr_asset.loc[df_cagr_asset["Date"].dt.to_period("M") == end_period,   "Holdings (Unit)"].sum())
                    cagr_units = (((latest_units_cagr / first_units_cagr) ** (12 / n_months_cagr)) - 1) * 100.0 \
                        if (first_units_cagr and first_units_cagr > 0) else None
                else:
                    cagr_units = None

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    f"Current ({single_asset} units) vs Last Month",
                    value=(f"{int(cur_units):,}" if cur_units is not None and cur_units >= 1 else f"{(cur_units or 0):,.2f}"),
                    delta=(f"{cur_vs_last_units_pct:+.1f}%" if cur_vs_last_units_pct is not None else None),
                    delta_color="normal",
                    help=f"Current {single_asset} units under the selected filters, with % change vs the last month. Note: Adjustment of −91,331 BTC applied for historical consistency with latest reported holdings due to data source inconsistencies."
                )

                c2.metric(
                    f"YTD ({single_asset} units)",
                    value=_fmt_pct_value(ytd_change_units),
                    delta_color="normal",
                    help=f"Change since prior year‑end (Dec), in {single_asset} units. "
                )
                c3.metric(
                    f"CAGR ({single_asset} units)",
                    value=_fmt_pct_value(cagr_units),
                    help=(f"Compound annual growth rate in {single_asset} units. "
                        "Uses last 12 months if available, otherwise all available data.")
                )

            else:
                st.caption("Select a single asset to view unit‑based KPIs.")
