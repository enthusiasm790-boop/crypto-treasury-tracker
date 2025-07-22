import streamlit as st
from modules.data_loader import load_data
from modules.filters import apply_filters
from modules import charts


def render_treasury_breakdown():
    # st.title(" Treasury Breakdown")

    df, last_updated = load_data()
    df_filtered = apply_filters(df)

    # Summary KPIs
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        total_value = df_filtered['USD Value'].sum()
        entity_count = df_filtered['Entity Name'].nunique()
        avg_value = df_filtered.groupby('Entity Name')['USD Value'].sum().mean()

        col1.metric("Total USD Value", f"${total_value:,.0f}")
        col2.metric("'#' of Entities", f"{entity_count}")
        col3.metric("Avg. Value per Entity", f"${avg_value:,.0f}")

    # Charts row
    #row1_col1, row1_col2 = st.columns([2, 1])
    row1_col1, row1_col2, row1_col3 = st.columns([1, 1, 1])

    with row1_col1:
        with st.container(border=True):
            st.markdown("#### Holdings by Entity Type", help="USD value of BTC/ETH holdings by entity category.")
            fig_bar = charts.holdings_by_entity_type_bar(df_filtered)
            st.plotly_chart(fig_bar, use_container_width=True)

    with row1_col2:
        with st.container(border=True):
            st.markdown("#### Entity Type Distribution", help="Share of entities by type.")
            fig_pie = charts.entity_type_distribution_pie(df_filtered)
            st.plotly_chart(fig_pie, use_container_width=True)

    with row1_col3:
        with st.container(border=True):
            st.markdown("#### Top 5 Countries", help="Compare leading countries by number of entities or total USD value, grouped by entity type.")

            display_mode = st.radio("", ["Entity Count", "USD Value"], index=0, horizontal=True)

            if display_mode == "Entity Count":
                fig_country = charts.top_countries_by_entity_count(df_filtered)
            else:
                fig_country = charts.top_countries_by_usd_value(df_filtered)

            st.plotly_chart(fig_country, use_container_width=True)
