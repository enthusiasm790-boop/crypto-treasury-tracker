import streamlit as st
import pandas as pd
from modules.data_loader import load_data, get_prices
from modules.kpi_helpers import render_kpis
from modules.charts import render_world_map, render_rankings

from datetime import datetime
import base64
import os

def load_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def render_header(BTC_PRICE, ETH_PRICE, last_updated):
    # Resolve absolute paths to asset images
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    btc_icon_path = os.path.join(CURRENT_DIR, "..", "assets", "bitcoin-logo.png")
    eth_icon_path = os.path.join(CURRENT_DIR, "..", "assets", "ethereum-logo.png")
    coingecko_icon_path = os.path.join(CURRENT_DIR, "..", "assets", "coingecko-logo.png")

    # Load and encode images as base64
    btc_icon_b64 = load_base64_image(btc_icon_path)
    eth_icon_b64 = load_base64_image(eth_icon_path)
    coingecko_icon_b64 = load_base64_image(coingecko_icon_path)

    html = f"""
<div style="display: flex; justify-content: space-between; align-items: center;
            padding: 0.5rem 1rem; background-color: #f8f9fa; border-radius: 0.5rem;
            font-size: 1rem; color: #333;">
    <div>
        <img src="data:image/png;base64,{btc_icon_b64}" style="height: 16px; vertical-align: middle; margin-right: 4px;">
        <b>${BTC_PRICE:,.0f}</b>
        &nbsp;&nbsp;
        <img src="data:image/png;base64,{eth_icon_b64}" style="height: 16px; vertical-align: middle; margin-right: 4px;">
        <b>${ETH_PRICE:,.0f}</b>
        &nbsp;&nbsp;
        Powered by 
        <img src="data:image/png;base64,{coingecko_icon_b64}" style="height: 16px; vertical-align: middle; margin-right: 0px;">
        <a href="https://www.coingecko.com/" target="_blank">CoinGecko</a>
    </div>
    <div>Last update: <b>{last_updated}</b></div>
</div>
"""

    with st.container(border=False):
        st.markdown(html, unsafe_allow_html=True)


def render_overview():
    df, last_updated = load_data()
    BTC_PRICE, ETH_PRICE = get_prices()
    
    # Header
    render_header(BTC_PRICE, ETH_PRICE, last_updated)

    # KPIs
    render_kpis(df)

    # ---------------------------
    # Layout: 2 + 1 column structure
    # ---------------------------
    col_main, col_side = st.columns([2, 1])

    # ---------- Left Side: Filters + Map ----------
    with col_main:
        with st.container(border=True):
            st.markdown("#### Global Treasury Map")

            filter_col1, filter_col2, filter_col3 = st.columns(3)
            asset_filter = filter_col1.selectbox("Crypto Asset", ["All", "BTC", "ETH"], index=0)
            type_options = ["All"] + sorted(df["Entity Type"].dropna().unique().tolist())
            type_filter = filter_col2.selectbox("Entity Type", type_options, index=0)
            value_filter = filter_col3.selectbox("Value Range (USD)", ["All", "0–100M", "100M–1B", ">1B"], index=0)

            map_fig = render_world_map(df, asset_filter, type_filter, value_filter)
            st.plotly_chart(map_fig, use_container_width=True)

    # ---------- Right Side: Rankings ----------
    with col_side:
        with st.container(border=True):
            st.markdown("#### Crypto Entity Ranking")

            # Toggle between Units and USD
            chart_mode = st.radio("Display Mode", ["Units", "USD"], index=0, horizontal=True)

            st.plotly_chart(render_rankings(df, asset="BTC", by=chart_mode.lower()), use_container_width=True)
            st.plotly_chart(render_rankings(df, asset="ETH", by=chart_mode.lower()), use_container_width=True)

    #st.markdown("Powered by [CoinGecko](https://www.coingecko.com/)")
