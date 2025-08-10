import os, base64
import streamlit as st

def load_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# preload logos once
_THIS = os.path.dirname(os.path.abspath(__file__))
_ASSETS = os.path.join(_THIS, "..", "assets")
btc_b64 = load_base64_image(os.path.join(_ASSETS, "bitcoin-logo.png"))
eth_b64 = load_base64_image(os.path.join(_ASSETS, "ethereum-logo.png"))
cg_b64  = load_base64_image(os.path.join(_ASSETS, "coingecko-logo.png"))
logo_b64 = load_base64_image(os.path.join(_ASSETS, "ctt-symbol.svg"))

CTA_URL = "https://digitalfinancebriefing.substack.com/?utm_source=ctt_app&utm_medium=sidebar_cta&utm_campaign=subscribe"
SUPPORT_URL = "https://buymeacoffee.com/cryptotreasurytracker"
def render_header():
    btc = st.session_state["prices"][0]
    eth = st.session_state["prices"][1]

    st.markdown(
        """
        """,
        unsafe_allow_html=True
    )
    html = f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
                padding:0.5rem 1rem;background-color:#f8f9fa;border-radius:0.5rem;
                font-size:1.2rem;color:#333;">
      <div>
        <img src="data:image/png;base64,{btc_b64}" style="height:20px;vertical-align:middle;margin-top:-3px;margin-right:4px;">
        <b>${btc:,.0f}</b>
        &nbsp;&nbsp;
        <img src="data:image/png;base64,{eth_b64}" style="height:20px;vertical-align:middle;margin-top:-3px;margin-right:4px;">
        <b>${eth:,.0f}</b>
        &nbsp;&nbsp;
        Powered by
        <img src="data:image/png;base64,{cg_b64}" style="height:20px;vertical-align:middle;margin-top:-3px;margin-left:4px;margin-right:0px;">
        <a href="https://www.coingecko.com/" target="_blank" style="text-decoration:none;color:inherit;">CoinGecko</a>
      </div>
      <div>
        <img src="data:image/svg+xml;base64,{logo_b64}" style="height:35px;vertical-align:middle;">
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_subscribe_cta():
    st.sidebar.write(" ")
    st.sidebar.link_button(
        "📥  Sign up for the monthly Crypto Treasury Report",
        CTA_URL,
        type="secondary",
        use_container_width=True,
        help="Click here to sign up for the monthly Crypto Treasury Report."
    )
    st.sidebar.write(" ")

def render_support():
    st.sidebar.markdown("---")
    st.sidebar.subheader("Support This Project ❤️")
    
    st.sidebar.link_button(
        "Click here to help keeping the Tracker running & updated.",
        SUPPORT_URL,
        type="secondary",
        use_container_width=True,
        help="Click here to support."
    )

    st.sidebar.write("")
    st.sidebar.write("")


def show_global_loader(msg="Loading data"):
    placeholder = st.empty()
    placeholder.markdown(
        f"""
        <div id="ctt-loader"
             style="
               position:fixed; inset:0; z-index:9999;
               display:flex; align-items:center; justify-content:center;
               background:rgba(0,0,0,0.55); backdrop-filter:saturate(140%) blur(2px);
               ">
          <div style="display:flex; flex-direction:column; align-items:center; gap:14px;
                      padding:18px 22px; border-radius:14px; background:#111; color:#fff;">
            <div class="spinner" style="
                  width:34px; height:34px; border-radius:50%;
                  border:3px solid #444; border-top-color:#fff;
                  animation:spin 0.9s linear infinite;"></div>
            <div style="font-size:0.95rem; opacity:0.9;">{msg}</div>
          </div>
        </div>
        <style>
          @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    return placeholder
