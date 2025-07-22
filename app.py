import streamlit as st
from sections import overview, treasury_breakdown, about

st.set_page_config(page_title="Crypto Treasury Tracker", layout="wide")

# Sidebar with logo and navigation
st.sidebar.image("assets/logo2.png", width=200)
st.sidebar.title("Crypto Treasury Tracker")
#st.sidebar.caption("Your Digital Assets Holdings Monitor")

section = st.sidebar.radio(" ", ["Global Summary", "Treasury Breakdown", "Reserve Database", "News", "About"])

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


if section == "Global Summary":
    overview.render_overview()
if section == "Treasury Breakdown":
    treasury_breakdown.render_treasury_breakdown()
if section == "About":
    about.render_about()


# Support
st.sidebar.markdown("---")
st.sidebar.markdown("Support this Project")
#st.sidebar.image("assets/qrcode_test.png", width=100)
st.sidebar.markdown(
    "<p style='font-size: 0.7rem; color: white;'>"
    "BTC: tbd"
    "</p>", unsafe_allow_html=True)

st.sidebar.markdown(
    "<p style='font-size: 0.7rem; color: white;'>"
    "ETH: tbd"
    "</p>", unsafe_allow_html=True)

st.sidebar.markdown(
    "<p style='font-size: 0.7rem; color: white;'>"
    "USDT: tbd"
    "</p>", unsafe_allow_html=True)


# External Links / Contact
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='font-size: 0.85rem; color: white;'>"
    #"<a href='https://x.com/yourhandle' target='_blank'>X</a> • "
    "<a href='https://www.linkedin.com/in/benjaminschellinger/' target='_blank'>LinkedIn</a> • "
    "<a href='https://digitalfinancebriefing.substack.com/' target='_blank'>Blog</a>"
    "</p>", unsafe_allow_html=True)


# Version and brand footer (light gray, small font)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='font-size: 0.75rem; color: gray;'>"
    "v0.1 • © 2025 Crypto Treasury Tracker"
    "</p>", unsafe_allow_html=True
)
