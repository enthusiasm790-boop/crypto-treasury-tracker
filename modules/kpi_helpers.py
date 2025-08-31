import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, base64


COLORS = {"BTC":"#f7931a","ETH":"#6F6F6F","XRP":"#00a5df","BNB":"#f0b90b","SOL":"#dc1fff", "SUI":"#C0E6FF", "LTC":"#345D9D"}

_THIS = os.path.dirname(os.path.abspath(__file__))
_ASSETS = os.path.join(_THIS, "..", "assets")


def load_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

logo_b64 = load_base64_image("assets/ctt-symbol.svg")
btc_b64 = load_base64_image(os.path.join(_ASSETS, "bitcoin-logo.png"))
eth_b64 = load_base64_image(os.path.join(_ASSETS, "ethereum-logo.png"))
sol_b64 = load_base64_image(os.path.join(_ASSETS, "solana-logo.png"))

def format_change(value):
    if value > 0:
        return f"↗ {value:.1f}%", "green"
    elif value < 0:
        return f"↘ {value:.1f}%", "red"
    else:
        return f"{value:.1f}%", "white"

# Summary KPIs
def render_kpis(df):
    # Compute values
    df = df[(df['USD Value'] > 0) | (df['Holdings (Unit)'] > 0)]

    total_usd = df["USD Value"].sum()

    btc_df = df[df["Crypto Asset"] == "BTC"]
    eth_df = df[df["Crypto Asset"] == "ETH"]
    sol_df = df[df["Crypto Asset"] == "SOL"]

    btc_usd = btc_df["USD Value"].sum()
    eth_usd = eth_df["USD Value"].sum()
    sol_usd = sol_df["USD Value"].sum()

    btc_entities = btc_df["Entity Name"].nunique()
    eth_entities = eth_df["Entity Name"].nunique()
    sol_entities = sol_df["Entity Name"].nunique()
    total_entities = df["Entity Name"].nunique()

    btc_units = btc_df["Holdings (Unit)"].sum()
    eth_units = eth_df["Holdings (Unit)"].sum()
    sol_units = sol_df["Holdings (Unit)"].sum()

    # KPI layout
    col1, col2, col3 = st.columns(3)


    with col1:
        with st.container(border=True):
            st.metric("Total USD Value", f"${total_usd:,.0f}", help="Aggregate USD value of all tracked crypto assets across entities, based on live market pricing.")

            # Custom progress bar styled as BTC (orange) + ETH (blue)
            usd_pct = {
                "BTC": btc_usd / total_usd if total_usd else 0.0,
                "ETH": eth_usd / total_usd if total_usd else 0.0,
                "SOL": sol_usd / total_usd if total_usd else 0.0,
            }

            COLORS = {"BTC": "#f7931a", "ETH": "#6F6F6F", "SOL": "#dc1fff"}

            # Progress bar with hover tooltip

            st.markdown(
                f"""
                <div style='background-color:#1e1e1e;border-radius:8px;height:20px;width:100%;display:flex;overflow:hidden;'>
                    {''.join(
                        f"<div title='{a}: {usd_pct[a]*100:.1f}% (${usd_val/1e9:.1f}B)' "
                        f"style='width:{usd_pct[a]*100:.1f}%;background-color:{COLORS[a]};'></div>"
                        for a, usd_val in [("BTC", btc_usd), ("ETH", eth_usd), ("SOL", sol_usd)]
                        if usd_pct[a] > 0
                    )}
                </div>
                <div style='margin-top:8px;margin-bottom:5px;font-size:16px;color:#aaa;display:flex;gap:12px;align-items:center;'>Dominance:
                    <div style='display:flex;align-items:center;gap:6px;'>
                        <img src="data:image/png;base64,{btc_b64}" width="16" height="16"> {usd_pct["BTC"]*100:.1f}%
                    </div>
                    <div style='display:flex;align-items:center;gap:6px;'>
                        <img src="data:image/png;base64,{eth_b64}" width="16" height="16"> {usd_pct["ETH"]*100:.1f}%
                    </div>
                    <div style='display:flex;align-items:center;gap:6px;'>
                        <img src="data:image/png;base64,{sol_b64}" width="16" height="16"> {usd_pct["SOL"]*100:.1f}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("")


    with col2:
        with st.container(border=True):
            st.metric("Total Unique Entities", f"{total_entities}", help="Entities holding crypto assets directly, excluding ETFs and indirect vehicles. Note: some entities hold multiple crypto assets and are only counted once.")

            ent_pct = {
                "BTC": (btc_entities / total_entities if total_entities else 0.0),
                "ETH": (eth_entities / total_entities if total_entities else 0.0),
                "SOL": (sol_entities / total_entities if total_entities else 0.0),
            }
            ENT_COUNTS = {"BTC": btc_entities, "ETH": eth_entities, "SOL": sol_entities}
            ENT_COLORS = {"BTC": COLORS["BTC"], "ETH": COLORS["ETH"], "SOL": COLORS["SOL"]}

            st.markdown(
                f"""
                <div style='background-color:#1e1e1e;border-radius:8px;height:20px;width:100%;display:flex;overflow:hidden;'>
                    {''.join(
                        f"<div title='{k}: {ENT_COUNTS[k]} ({ent_pct[k]*100:.1f}%)' "
                        f"style='width:{ent_pct[k]*100:.1f}%;background-color:{ENT_COLORS[k]};'></div>"
                        for k in ["BTC","ETH","SOL"] if ent_pct[k] > 0
                    )}
                </div>
                <div style='margin-top:8px;margin-bottom:5px;font-size:16px;color:#aaa;display:flex;gap:12px;align-items:center;'>Adoption:
                    <div style='display:flex;align-items:center;gap:6px;'>
                        <img src="data:image/png;base64,{btc_b64}" width="16" height="16"> {btc_entities}
                    </div>
                    <div style='display:flex;align-items:center;gap:6px;'>
                        <img src="data:image/png;base64,{eth_b64}" width="16" height="16"> {eth_entities}
                    </div>
                    <div style='display:flex;align-items:center;gap:6px;'>
                        <img src="data:image/png;base64,{sol_b64}" width="16" height="16"> {sol_entities}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("")



    with col3:
        with st.container(border=True):
            st.metric("% of Supply", f"", help="Share of total circulating supply held by tracked entities (BTC ≈ 20M, ETH ≈ 120M, SOL ≈ 540M).")

            # compute percentages of supply
            btc_pct_supply = btc_units / 20_000_000
            eth_pct_supply = eth_units / 120_000_000
            sol_pct_supply = sol_units / 540_000_000

            # colors
            COL_HELD = {
                "BTC": "#f7931a",
                "ETH": "#6F6F6F",
                "SOL": "#dc1fff",
            }
            COL_REMAIN = "#2c2c2c"

            # figure and subplots
            fig = make_subplots(
                rows=1, cols=3,
                specs=[[{"type": "domain"}, {"type": "domain"}, {"type": "domain"}]],
                horizontal_spacing=0.08,
            )

            # pies
            fig.add_trace(go.Pie(
                labels=["Held", "Remaining"],
                values=[btc_pct_supply, 1 - btc_pct_supply],
                hole=0.7,
                marker_colors=[COL_HELD["BTC"], COL_REMAIN],
                textinfo="none",
                hoverinfo="skip",
                sort=False
            ), 1, 1)

            fig.add_trace(go.Pie(
                labels=["Held", "Remaining"],
                values=[eth_pct_supply, 1 - eth_pct_supply],
                hole=0.7,
                marker_colors=[COL_HELD["ETH"], COL_REMAIN],
                textinfo="none",
                hoverinfo="skip",
                sort=False
            ), 1, 2)

            fig.add_trace(go.Pie(
                labels=["Held", "Remaining"],
                values=[sol_pct_supply, 1 - sol_pct_supply],
                hole=0.7,
                marker_colors=[COL_HELD["SOL"], COL_REMAIN],
                textinfo="none",
                hoverinfo="skip",
                sort=False
            ), 1, 3)

            # helper to center a logo and its percent for a given pie trace
            def add_logo_and_pct(fig, trace_idx, b64, pct_text, img_scale=0.24, gap=0.25):
                """
                img_scale controls logo size relative to the pie domain
                gap controls vertical spacing between logo and text as a fraction of domain height
                """
                t = fig.data[trace_idx]
                try:
                    x0, x1 = t.domain.x
                    y0, y1 = t.domain.y
                except Exception:
                    x0, x1 = t.domain["x"]
                    y0, y1 = t.domain.get("y", [0, 1])

                cx = (x0 + x1) / 2.0
                cy = (y0 + y1) / 2.0
                dx = (x1 - x0)
                dy = (y1 - y0)

                # logo anchored to pie domain
                fig.add_layout_image(dict(
                    source=f"data:image/png;base64,{b64}",
                    xref="paper", yref="paper",
                    x=cx, y=cy + dy * (gap / 2),
                    sizex=dx * img_scale,
                    sizey=dy * img_scale,
                    xanchor="center", yanchor="middle",
                    sizing="contain",
                    layer="above",
                    opacity=1.0,
                ))

                # percent anchored to the same domain with symmetric offset
                fig.add_annotation(
                    text=pct_text,
                    x=cx, y=cy - dy * (gap / 2),
                    xref="paper", yref="paper",
                    xanchor="center", yanchor="middle",
                    showarrow=False,
                    font=dict(size=16, color="white"),
                    align="center",
                )

            # layout reset
            fig.update_layout(
                height=105,
                margin=dict(t=0, b=0, l=0, r=0),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                annotations=[],
            )

            # place logos and percents
            # assumes btc_b64 eth_b64 sol_b64 already loaded as base64 strings
            add_logo_and_pct(fig, 0, btc_b64, f"{btc_pct_supply:.2%}")
            add_logo_and_pct(fig, 1, eth_b64, f"{eth_pct_supply:.2%}")
            add_logo_and_pct(fig, 2, sol_b64, f"{sol_pct_supply:.2%}")

            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})



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
