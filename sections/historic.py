import streamlit as st
from modules.data_loader import load_historic_data
from modules.filters import apply_filters_historic
from modules.charts import historic_chart
from modules.kpi_helpers import render_ctt_logo, render_historic_kpis

def render_historic_holdings():
    
    render_ctt_logo()

    df = load_historic_data()
    df_filtered = apply_filters_historic(df)

    # Summary KPIs
    render_historic_kpis(df_filtered)

    # Historic Holding Chart    
    with st.container(border=True):
        st.markdown("#### Historic Crypto Treasury Holdings", help="Shows the historic development of aggregated and individual crypto asset holdings across all entities (data available from January 2024).")

        metric = st.radio("", ["USD Value", "Unit Count"], index=0, horizontal=True)

        by = "USD" if metric == "USD Value" else "Holdings (Unit)"
        fig = historic_chart(df_filtered, by=by)

        st.plotly_chart(fig, use_container_width=True)