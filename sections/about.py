import streamlit as st
import pandas as pd
from modules.kpi_helpers import render_ctt_logo


def render_about():

    render_ctt_logo()
    
    # Box 1: Project Overview
    with st.container(border=True):
        st.markdown(
            """
            <h4 style="margin-top: 0;">First Multi-Asset Crypto Treasury Tracker</h4>
            
            <p>Crypto reserves held by public, private, and sovereign entities are increasingly shaping digital asset market structure and institutional narratives. Yet existing trackers remain fragmented—most cover only Bitcoin or a narrow subset.</p>

            <p>The <strong>Crypto Treasury Tracker</strong> maps and visualizes <strong>ALL</strong> crypto reserves held by public companies, private firms, DAOs, nonprofits, and sovereigns.</p>

            <p>Instead of single-asset databases, this app merges asset-level and entity-level crypto treasury data into a unified analytics layer. It enables cross-sectional and regional analysis of strategic crypto holdings with dynamic filters and interactive visuals. The <strong>Crypto Treasury Tracker</strong> is designed to deliver actionable insights for institutional investors, finance professionals, and strategic observers.</p>

            </div>
            """,
            unsafe_allow_html=True
        )
    # Box 2: Data Sources & Update Logic
    with st.container(border=True):
        st.markdown(
            """
            <h5 style="margin-top: 0;">Data Sources</h4>

            <ul>
                <li>Live crypto prices via <a href="https://docs.coingecko.com/reference/simple-price" target="_blank">CoinGecko API</a>, automatically refreshed every hour</li>
                <li>Reserve data is updated weekly and based on external sources, for example, <a href="https://bitcointreasuries.net/" target="_blank">bitcointreasuries.net</a> and <a href="https://www.strategicethreserve.xyz/?ref=bankless.ghost.io" target="_blank">strategicethreserve.xyz</a></li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Box 3: Upcoming Features
    with st.container(border=True):
        st.markdown(
            """
            <h5 style="margin-top: 0;">Planned Features</h4>
            <ul>
                <li>Historic development of crypto reserve holdings</li>
                <li>More nuanced reserve data: sector, purpose, NAV, % of total treasury, and more</li>
                <li>Inclusion of new crypto assets, spot digital asset ETFs, and DeFi or smart contract-based treasuries</li>
                <li>News and treasury announcements to track strategic moves in real time</li>
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

            <p>If you like the <strong>Crypto Treasury Tracker</strong> and want to keep it going, feel free to chip in and support the project :)</p>
            <ul style="margin-top: 0; font-size: 0.9rem;">
              <li>BTC: bc1pujcv929agye4w7fmppkt94rnxf6zfv3c7zpc25lurv7rdtupprrsxzs5g6</li>
              <li>ETH: 0xe1b0Ae7b8496450ea09e60b110C2665ba0CB888f</li>
              <li>SOL: 3JWdqYuy2cvMVdRbvXrQnZvtXJStBV5ooQ3QdqemtScQ</li>
              <li>Prefer fiat? <a href="https://buymeacoffee.com/cryptotreasurytracker" target="_blank">Buy Me a Coffee</a>.</li>
            </ul>

            When using data, graphs, or insights from the <strong>Crypto Treasury Tracker</strong>, please cite as follows:<br>
            Crypto Treasury Tracker by Benjamin Schellinger, PhD (2025), url: https://crypto-treasury-tracker.streamlit.app</br>
            </p>

            <p><strong>Feedback or collaboration?</strong> Connect via <a href="https://www.linkedin.com/in/benjaminschellinger/" target="_blank">LinkedIn</a>.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("All information is for informational purposes only and does not constitute financial advice.")