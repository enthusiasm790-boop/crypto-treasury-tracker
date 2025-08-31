import streamlit as st
import pandas as pd
import numpy as np
from modules.kpi_helpers import render_kpis
from modules.charts import render_world_map, render_rankings
from modules.filters import _opts
from datetime import datetime
from modules.ui import render_plotly
from analytics import log_filter_if_changed, log_chart_view, log_table_render


# Supply column row-wise
supply_caps = {
    "BTC": 20_000_000,  
    "ETH": 120_000_000,
    #"XRP": 60_000_000_000,
    #"BNB": 140_000_000,
    "SOL": 540_000_000,
    #"SUI": 3_500_000_000,
    #"LTC": 76_000_000,
    }

def render_overview():
    df = st.session_state["data_df"]

    # KPIs
    render_kpis(df)

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)

        asset_opts   = st.session_state["opt_assets"]
        type_opts    = st.session_state["opt_entity_types"]
        value_opts   = ["All", "0–100M", "100M–1B", ">1B"]

        # assets
        if "ui_assets_map" not in st.session_state:
            st.session_state["ui_assets_map"] = st.session_state.get("flt_assets", asset_opts)
        sel_assets = c1.multiselect(
            "Select Crypto Asset(s)",
            options=asset_opts,
            key="ui_assets_map"     # no default on reruns
        )
        st.session_state["flt_assets"] = sel_assets

        # entity type
        if "ui_entity_type_map" not in st.session_state:
            st.session_state["ui_entity_type_map"] = st.session_state.get("flt_entity_type", "All")
        sel_et = c2.selectbox(
            "Entity Type",
            options=type_opts,
            key="ui_entity_type_map"   # no index on reruns
        )
        st.session_state["flt_entity_type"] = sel_et

        # value bucket
        if "ui_value_range_map" not in st.session_state:
            st.session_state["ui_value_range_map"] = st.session_state.get("flt_value_range", "All")
        sel_v = c3.selectbox(
            "Value Range (USD)",
            options=value_opts,
            key="ui_value_range_map"   # no index on reruns
        )
        st.session_state["flt_value_range"] = sel_v
    
        # Log filters if changed
        log_filter_if_changed("global_summary", {
            "asset": sel_assets or ["All"],
            "entity_type": sel_et or "All",
            "value_range": sel_v or "All",
        })

    
    # Global Map
    with st.container(border=True):
        st.markdown("#### Global Treasury Map", help="Geographic distribution of crypto reserves, filtered by crypto asset, entity type, and value range.")

        if not sel_assets:
            st.info("Select at least one Crypto Asset to display the map")
        else:
            fig = render_world_map(df, sel_assets, sel_et, sel_v)
            if fig is not None:
                render_plotly(fig, "crypto_reserve_world_map", extra_config={"scrollZoom": False})


    # Top 5 Rankings (BTC + ETH)
    with st.container(border=True):
        st.markdown("#### Top 5 BTC & ETH Holders", help="List of top 5 entities by BTC & ETH holdings, shown in units or USD value.")

        # Toggle between Units and USD
        chart_mode = st.radio("Display mode", ["Units", "USD"], index=0, horizontal=True, label_visibility="collapsed")

        col_btc, col_eth = st.columns([1,1])

        with col_btc:
            render_plotly(render_rankings(df, asset="BTC", by=chart_mode.lower()), "top_5_btc_holders")

        with col_eth:
            render_plotly(render_rankings(df, asset="ETH", by=chart_mode.lower()), "top_5_eth_holders")


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
    sub = table.head(row_count)

    st.dataframe(
        sub,
        column_config={
            "USD Value": st.column_config.NumberColumn("USD Value", format="$%d"),
            "% of Supply": st.column_config.NumberColumn("% of Supply", format="%.2f%%"),
        },
        use_container_width=True
    )
    log_table_render("global_summary", "overview_table", len(sub))

    # CSV download
    csv_bytes = sub.to_csv(index=True).encode("utf-8")
    if st.download_button(
        "Download table as CSV",
        data=csv_bytes,
        file_name=f"crypto_treasury_list_top{len(sub)}.csv",
        mime="text/csv",
        key="dl_overview_table",
    ):
        from analytics import log_event
        log_event("download_click", {
            "target": "table_csv",
            "file_name": f"crypto_treasury_list_top{len(sub)}.csv",
            "rows_exported": int(len(sub)),
        })
 
    # Last update info
    st.caption("*Last treasury data base update: August 31, 2025*")
