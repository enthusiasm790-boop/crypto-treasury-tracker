import streamlit as st
from modules.filters import apply_filters_historic
from modules.charts import historic_chart
from modules.kpi_helpers import render_historic_kpis
from modules.ui import render_plotly


def render_historic_holdings():
    df = st.session_state["historic_df"]
    df_filtered = apply_filters_historic(df)

    if df_filtered.empty:
        st.info("No data for the current filters")
        return

    render_historic_kpis(df_filtered)

    with st.container(border=True):
        st.markdown("#### Historic Crypto Treasury Holdings", help="Shows the historic development of aggregated and individual crypto asset holdings across all entities")

        metric = st.radio("Display mode", ["USD Value", "Unit Count"], index=0, horizontal=True, label_visibility="collapsed")
        by = "USD" if metric == "USD Value" else "Holdings (Unit)"

        render_plotly(historic_chart(df_filtered, by=by), "historic_crypto_reserves")
