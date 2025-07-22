import streamlit as st
import pandas as pd


def render_about():
    # Box 1: Project Overview
    with st.container(border=True):
        st.markdown(
            """
            <h4 style="margin-top: 0;">The First Global Tracker of Strategic Crypto Holdings</h4>
            
            <p>Crypto reserves held by public, private, and sovereign entities are increasingly shaping digital asset market structure and institutional narratives. Yet existing trackers remain fragmented—most cover only Bitcoin or a narrow subset.</p>

            <p>The <strong>Crypto Treasury Tracker</strong> maps and visualizes crypto reserves held by public companies, private firms, DAOs, nonprofits, and sovereigns.</p>

            <p>Instead of isolated datasets or single-asset trackers, this app merges asset-level and entity-level data into a unified analytics layer—multi-asset, multi-entity, and built for interaction. It enables cross-sectional and regional analysis of strategic crypto holdings with dynamic filters and interactive visuals, delivering actionable insights for institutional investors, finance professionals, and strategic observers.</p>

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
                <li>Reserve data is updated weekly and based on external sources, for example: 
                    <ul>
                        <li>BTC: <a href="https://bitcointreasuries.net/" target="_blank">bitcointreasuries.net</a></li>
                        <li>ETH: <a href="https://www.strategicethreserve.xyz/?ref=bankless.ghost.io" target="_blank">strategicethreserve.xyz</a></li>
                    </ul>
                </li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Box 3: Upcoming Features
    with st.container(border=True):
        st.markdown(
            """
            <h5 style="margin-top: 0;">Upcoming Features</h4>
            <ul>
                <li>Entity-lelvel ranking of crypto asset holders</li>
                <li>Historic development of crypto reserve holdings</li>
                <li>More nuanced reserve data: sector, purpose, NAV, % of total treasury, and more</li>
                <li>Inclusion of new crypto assets, spot digital asset ETFs, DeFi & smart contract holders.</li>
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
              <li>BTC: bc1pujcv929agye4w7fmppkt94rnxf6zfv3c7zpc25lurv7rdtupprrsxzs5g6</li>
              <li>ETH: 0xe1b0Ae7b8496450ea09e60b110C2665ba0CB888f</li>
              <li>SOL: 3JWdqYuy2cvMVdRbvXrQnZvtXJStBV5ooQ3QdqemtScQ</li>
              <li>Prefer fiat? You can do so via <a href="https://buymeacoffee.com/cryptotreasurytracker" target="_blank">Buy Me a Coffee</a>.</li>
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