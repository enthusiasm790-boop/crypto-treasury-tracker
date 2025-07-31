import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64


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


def render_ctt_logo():
    html = f"""
<div style="display: flex; justify-content: flex-end; align-items: center;
            padding: 0.5rem 1rem; background-color: #f8f9fa; border-radius: 0.5rem;
            font-size: 1rem; color: #333;">
    <img src="data:image/svg+xml;base64,{logo_b64}" style="height: 25px; vertical-align: middle;">
</div>
"""
    with st.container(border=False):
        st.markdown(html, unsafe_allow_html=True)

def render_kpis(df):
    # Compute values
    df = df[(df['USD Value'] > 0) | (df['Holdings (Unit)'] > 0)]

    total_usd = df["USD Value"].sum()

    btc_df = df[df["Crypto Asset"] == "BTC"]
    eth_df = df[df["Crypto Asset"] == "ETH"]

    btc_usd = btc_df["USD Value"].sum()
    eth_usd = eth_df["USD Value"].sum()

    btc_entities = btc_df["Entity Name"].nunique()
    eth_entities = eth_df["Entity Name"].nunique()
    total_entities = df["Entity Name"].nunique()

    btc_units = btc_df["Holdings (Unit)"].sum()
    eth_units = eth_df["Holdings (Unit)"].sum()

    # KPI layout
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.metric("Total USD Value", f"${total_usd:,.0f}", help="Aggregate USD value of all tracked crypto reserves across entities, based on live market pricing.")

            # Custom progress bar styled as BTC (orange) + ETH (blue)
            btc_pct = btc_usd / total_usd
            eth_pct = eth_usd / total_usd

            st.markdown(
                f"""
                <div style='background-color: #1e1e1e; border-radius: 8px; height: 20px; width: 100%; display: flex; overflow: hidden;'>
                    <div style='width: {btc_pct*100:.1f}%; background-color: #f7931a;'></div>
                    <div style='width: {eth_pct*100:.1f}%; background-color: #A9A9A9;'></div>
                </div>
                <div style='margin-top: 8px; margin-bottom: 5px; font-size: 16px; color: #aaa;'>
                    BTC: ${btc_usd/1e9:.1f}B | ETH: ${eth_usd/1e9:.1f}B
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("")


    with col2:
        with st.container(border=True):
            st.metric("Total Unique Entities", f"{total_entities}", help="Entities holding BTC, ETH, or both directly, excluding ETFs and indirect vehicles. Note: some entities hold both and are only counted once.")

            # BTC/ETH split bar (same color scheme)
            btc_ent_pct = btc_entities / total_entities
            eth_ent_pct = eth_entities / total_entities

            st.markdown(
                f"""
                <div style='background-color: #1e1e1e; border-radius: 8px; height: 20px; width: 100%; display: flex; overflow: hidden;'>
                    <div style='width: {btc_ent_pct*100:.1f}%; background-color: #f7931a;'></div>
                    <div style='width: {eth_ent_pct*100:.1f}%; background-color: #A9A9A9;'></div>
                </div>
                <div style='margin-top: 8px; margin-bottom: 5px;font-size: 16px; color: #aaa;'>
                    BTC: {btc_entities} | ETH: {eth_entities}
                </div>
                """
                ,
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


def render_historic_kpis(df_filtered):
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)

        if not df_filtered.empty:
            latest_year = df_filtered['Year'].max()
            latest_month = df_filtered[df_filtered['Year'] == latest_year]['Month'].max()
            prev_year, prev_month = (latest_year, latest_month - 1) if latest_month > 1 else (latest_year - 1, 12)

            latest_total = df_filtered[(df_filtered['Year'] == latest_year) & (df_filtered['Month'] == latest_month)]['USD Value'].sum()
            prev_total = df_filtered[(df_filtered['Year'] == prev_year) & (df_filtered['Month'] == prev_month)]['USD Value'].sum()
            monthly_change = ((latest_total - prev_total) / prev_total * 100) if prev_total > 0 else 0

            # YTD Change
            prior_dec_total = df_filtered[(df_filtered['Year'] == latest_year - 1) & (df_filtered['Month'] == 12)]['USD Value'].sum()
            ytd_change = ((latest_total - prior_dec_total) / prior_dec_total * 100) if prior_dec_total > 0 else 0

            # CAGR
            first_year = df_filtered['Year'].min()
            first_month = df_filtered[df_filtered['Year'] == first_year]['Month'].min()
            first_total = df_filtered[(df_filtered['Year'] == first_year) & (df_filtered['Month'] == first_month)]['USD Value'].sum()
            n_months = (latest_year - first_year) * 12 + (latest_month - first_month)
            cagr = (((latest_total / first_total) ** (12 / n_months)) - 1) * 100 if first_total > 0 and n_months > 0 else 0


            # Display metrics
            monthly_text, monthly_color = format_change(monthly_change)
            ytd_text, ytd_color = format_change(ytd_change)
            cagr_text, cagr_color = format_change(cagr)

            col1.metric("Monthly Change", monthly_text, delta_color="normal", help="Percentage change in total crypto reserves (USD value) compared to the previous month’s holdings.")
            col2.metric("YTD Change", ytd_text, delta_color="normal", help="Percentage change in total crypto reserves (USD value) since the end of the previous calendar year.")
            col3.metric("CAGR", cagr_text, delta_color="normal", help="Compound annual growth rate of reserves in total crypto reserves (USD value).")

            # Apply colors via markdown
        else:
            col1.metric("Monthly Change", "N/A")
            col2.metric("YTD Change", "N/A")
            col3.metric("CAGR", "N/A")
