import streamlit as st
import pandas as pd
import numpy as np
from modules.data_loader import load_data, get_prices
from modules.kpi_helpers import render_kpis
from modules.charts import render_world_map, render_rankings

from datetime import datetime
import base64
import os

def load_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

logo_b64 = load_base64_image("assets/ctt-symbol.svg")

# Supply column row-wise
supply_caps = {
    "BTC": 20_000_000,  
    "ETH": 120_000_000
}

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
    <!-- Left side: BTC, ETH, CoinGecko -->
    <div>
        <img src="data:image/png;base64,{btc_icon_b64}" style="height: 20px; vertical-align: middle; margin-top: -3px; margin-right: 2px;">
        <b>${BTC_PRICE:,.0f}</b>
        &nbsp;&nbsp;
        <img src="data:image/png;base64,{eth_icon_b64}" style="height: 20px; vertical-align: middle; margin-top: -3px; margin-right: 2px;">
        <b>${ETH_PRICE:,.0f}</b>
        &nbsp;&nbsp;
        Powered by
        <img src="data:image/png;base64,{coingecko_icon_b64}" style="height: 20px; vertical-align: middle; margin-top: -3px; margin-left: 2px;; margin-right: 0px;">
        <a href="https://www.coingecko.com/" target="_blank" style="text-decoration: none; color: inherit;">CoinGecko</a>
    </div>
    <!-- Right side: CTT logo -->
    <div>
        <img src="data:image/svg+xml;base64,{logo_b64}" style="height: 25px; vertical-align: middle;">
    </div>
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

    # Global Map
    with st.container(border=True):
        st.markdown("#### Global Treasury Map", help="Geographic distribution of crypto reserves, filtered by crypto asset, entity type, and value range.")

        filter_col1, filter_col2, filter_col3 = st.columns(3)
        asset_filter = filter_col1.selectbox("Crypto Asset", ["All", "BTC", "ETH"], index=0)
        type_options = ["All"] + sorted(df["Entity Type"].dropna().unique().tolist())
        type_filter = filter_col2.selectbox("Entity Type", type_options, index=0)
        value_filter = filter_col3.selectbox("Value Range (USD)", ["All", "0–100M", "100M–1B", ">1B"], index=0)

        map_fig = render_world_map(df, asset_filter, type_filter, value_filter)
        st.plotly_chart(map_fig, use_container_width=True, config={"scrollZoom": False})

    # Top 5 Rankings (BTC + ETH)
    with st.container(border=True):
        st.markdown("#### Top 5 Crypto Holders", help="List of top 5 entities by crypto holdings, shown in units or USD value.")

        # Toggle between Units and USD
        chart_mode = st.radio("", ["Units", "USD"], index=0, horizontal=True)

        col_btc, col_eth = st.columns([1,1])

        with col_btc:
            st.plotly_chart(render_rankings(df, asset="BTC", by=chart_mode.lower()), use_container_width=True)

        with col_eth:
            st.plotly_chart(render_rankings(df, asset="ETH", by=chart_mode.lower()), use_container_width=True)


    # Table
    table = df.copy()
    table = table.sort_values("USD Value", ascending=False)

    table = table.reset_index(drop=True)
    table.index = table.index + 1
    table.index.name = "Rank"

    table["Holdings (Unit)"] = table["Holdings (Unit)"].round(0)
    table["USD Value"] = table["USD Value"].round(0)

    # Add % of Supply Column
    table["% of Supply"] = table.apply(lambda row: row["Holdings (Unit)"] / supply_caps.get(row["Crypto Asset"], 1) * 100, axis=1)
    table["% of Supply"] = table["% of Supply"].round(2)

    # Reorder columns: put "% of Supply" right after "Holdings (Unit)"
    cols = list(table.columns)

    if "Holdings (Unit)" in cols and "% of Supply" in cols:
        # Remove "% of Supply" and reinsert it after "Holdings (Unit)"
        cols.remove("% of Supply")
        insert_pos = cols.index("Holdings (Unit)") + 1
        cols.insert(insert_pos, "% of Supply")
        table = table[cols]

    row_count = st.selectbox("Rows to display", options=[5, 10, 25, 50, 100], index=1)

    # Display as interactive dataframe (sortable, scrollable)
    st.dataframe(table.head(row_count),
        column_config={
            "USD Value": st.column_config.NumberColumn("USD Value",format="$%d"),
            "% of Supply": st.column_config.NumberColumn("% of Supply", format="%.2f%%"),
        },
        use_container_width=True
    )
 
    # Last update info
    st.caption("*Last treasury data base update: July 23, 2025*")