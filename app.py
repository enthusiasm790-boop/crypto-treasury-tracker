import streamlit as st
from sections import overview, historic, ranking, treasury_breakdown, about

st.set_page_config(page_title="Crypto Treasury Tracker", layout="wide")
st.sidebar.image("assets/ctt-logo.svg", width=200)

# Sidebar with logo and navigation
st.sidebar.subheader("_Track Strategic Crypto Reserves—All in One Place!_")
#st.sidebar.markdown("---")

section = st.sidebar.radio("Explore The Tracker", ["🌎 Global Overview", "📊 Historic Holdings", "🥇 Entity Ranking", "🔍 Treasury Breakdown", "ℹ️ About"])

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2.8rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)


if section == "🌎 Global Overview":
    overview.render_overview()
if section == "📊 Historic Holdings":
    historic.render_historic_holdings()
if section == "🥇 Entity Ranking":
    ranking.render_entity_ranking()
if section == "🔍 Treasury Breakdown":
    treasury_breakdown.render_treasury_breakdown()
if section == "ℹ️ About":
    about.render_about()


# Support
st.sidebar.markdown("---")
st.sidebar.subheader("Support this project ❤️")

st.sidebar.markdown(
    "<p style='font-size: 0.7rem; color: white;'>"
    "Help keeping the Tracker running & updated."
    "</p>", unsafe_allow_html=True)

st.sidebar.markdown(
    "<p style='font-size: 0.7rem; color: white;'>"
    "BTC: bc1pujcv929agye4w7fmppkt94rnxf6zfv3c7zpc25lurv7rdtupprrsxzs5g6"
    "</p>", unsafe_allow_html=True)

st.sidebar.markdown(
    "<p style='font-size: 0.7rem; color: white;'>"
    "ETH: 0xe1b0Ae7b8496450ea09e60b110C2665ba0CB888f"
    "</p>", unsafe_allow_html=True)

st.sidebar.markdown(
    "<p style='font-size: 0.7rem; color: white;'>"
    "SOL: 3JWdqYuy2cvMVdRbvXrQnZvtXJStBV5ooQ3QdqemtScQ"
    "</p>", unsafe_allow_html=True)

st.sidebar.markdown(
    """
    <p style='font-size: 0.7rem; color: white;'>
    Prefer fiat? <a href="https://buymeacoffee.com/cryptotreasurytracker" target="_blank">Buy Me a Coffee</a>
    </p>
    """, 
unsafe_allow_html=True)


# External Links / Contact
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='font-size: 0.85rem; color: white;'>"
    "<a href='https://www.linkedin.com/in/benjaminschellinger/' target='_blank'>LinkedIn</a> | "
    "<a href='https://digitalfinancebriefing.substack.com/' target='_blank'>Blog</a>"
    "</p>", unsafe_allow_html=True)

# Version and brand footer
#st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='font-size: 0.75rem; color: gray;'>"
    "v0.1 • © 2025 Crypto Treasury Tracker"
    "</p>", unsafe_allow_html=True
)
