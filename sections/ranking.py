import streamlit as st
from modules.data_loader import load_data
from modules.filters import apply_filters
from modules.charts import entity_ranking


def render_entity_ranking():
    df, last_updated = load_data()
    df_filtered = apply_filters(df)

    with st.container(border=True):
        st.markdown("#### Top Entities by Crypto Treasuries", help="Rank leading entities by total crypto holdings (USD value) or number of units held.")

        col_toggle, col_n, _ = st.columns([1, 1, 1])
        metric = col_toggle.radio("", ["USD Value", "Unit Count"], index=0, horizontal=True)
        top_n = col_n.number_input("Max. Entities Displayed", min_value=1, max_value=100, value=10, step=1)

        by = "USD" if metric == "USD Value" else "units"
        fig = entity_ranking(df_filtered, by=by, top_n=top_n)
        st.plotly_chart(fig, use_container_width=True)


