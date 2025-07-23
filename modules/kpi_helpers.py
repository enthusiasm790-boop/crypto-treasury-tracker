import streamlit as st
import plotly.graph_objects as go


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
            #st.markdown("Total USD Value", help="Aggregate USD value of all tracked crypto reserves across entities, based on live market pricing.")

            # Modern large-font formatting with tighter vertical space
            #st.markdown(
            #    f"<h2 style='margin-bottom: 0; font-size: 2.5rem; color: white;'>${total_usd:,.0f}</h2>",
            #    unsafe_allow_html=True
            #)

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

            # Clean modern headline number
            #st.markdown(
            #    f"<h2 style='margin-bottom: 0; font-size: 2.5rem; color: white;'>{total_entities}</h2>",
            #    unsafe_allow_html=True
            #)

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
            #st.markdown("#### % of Supply", help="Share of total circulating supply held by tracked entities (BTC ≈ 20M, ETH ≈ 120M).")

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
