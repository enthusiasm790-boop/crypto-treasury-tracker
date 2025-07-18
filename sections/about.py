import streamlit as st
import pandas as pd


def render_about():
    # Box 1: Project Overview
    with st.container(border=True):
        st.markdown(
            """
            <h4 style="margin-top: 0;">The First Global Tracker of Strategic Crypto Holdings</h4>

            <p><strong>Why</strong>? Crypto reserves held by public, private, and sovereign entities increasingly shape digital asset market structure and institutional narratives. Yet, current trackers are fragmented (or BTC-only). This project addresses that gap with entity-level, multi-asset reserve intelligence.</p>
            
            <p><strong>What</strong>: A purpose-built dashboard that tracks and visualizes verified crypto asset reserves—Bitcoin, Ethereum, and others—held by public companies, private firms, DAOs, nonprofits, and sovereign entities. The tool combines asset-level and entity-level data for cross-sectional and cross-regional analysis of who holds what, and how that evolves over time.</p>

            <p><strong>How it’s different</strong>: Unlike narrow trackers or isolated datasets, this platform unifies fragmented disclosures into a structured analytics layer. It delivers multi-asset, multi-entity coverage with clean visualizations and filtering—designed to provide exclusive, high-signal insights for institutional observers, strategists, and researchers.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    # Box 2: Data Sources & Update Logic
    with st.container(border=True):
        st.markdown(
            """
            <h5 style="margin-top: 0;">Data Sources & Update Frequency</h4>

            <ul>
                <li>Live crypto prices via <a href="https://docs.coingecko.com/reference/simple-price" target="_blank">CoinGecko API</a>, automatically refreshed every hour</li>
                <li>Reserve Disclosures based on external sources, for example: 
                    <ul>
                        <li>BTC: <a href="https://bitcointreasuries.net/" target="_blank">bitcointreasuries.net</a></li>
                        <li>ETH: <a href="https://www.strategicethreserve.xyz/?ref=bankless.ghost.io" target="_blank">strategicethreserve.xyz</a></li>
                    </ul>
                </li>
                <li>Reserve data is verified, aggregated, and updated weekly</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Box 3: Upcoming Features
    with st.container(border=True):
        st.markdown(
            """
            <h5 style="margin-top: 0;">Upcoming & Planned Features</h4>
            <ul>
                <li>Granular insights by entity type and geographic exposure</li>
                <li>Historical crypto reserve holdings development</li>
                <li>More nuanced reserve data: sector, purpose, NAV, % of total treasury, and more</li>
                <li>Inclusion of spot Crypto ETFs, tokenized funds, and DAO treasuries</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Box 4: Support, Attribution & Contact
    with st.container(border=True):
        st.markdown(
            """
            <h5 style="margin-top: 0;">Support & Attribution</h4>

            <p>If you find the Crypto Treasury Tracker useful and want to support its development, crypto contributions are very welcome :)</p>
            <ul style="margin-top: 0; font-size: 0.9rem;">
              <li>BTC: tbd</li>
              <li>ETH: tbd</li>
              <li>USDT: tbd</li>
            </ul>

            When using data, graphs, or insights from the <strong>Crypto Treasury Tracker</strong>, please cite as follows:<br>
            Crypto Treasury Tracker by Benjamin Schellinger, PhD — steramlit.com<br>
            </p>

            <p><strong>Feedback or collaboration?</strong> Connect via <a href="https://www.linkedin.com/in/your-profile" target="_blank">LinkedIn</a>.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("All information is for informational purposes only and does not constitute financial advice.")