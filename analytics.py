# analytics.py
import uuid, json, hashlib
import streamlit as st
from posthog import Posthog
from extra_streamlit_components import CookieManager

# ---- config from secrets ----
PH_API_KEY = st.secrets["posthog"]["api_key"]
PH_HOST    = st.secrets["posthog"]["host"]
APP_VERSION = "1.0.0"

# ---- singletons ----
_posthog = Posthog(PH_API_KEY, host=PH_HOST)

def init_analytics():
    cm = CookieManager(key="ctt_cookies")
    vid = cm.get("ctt_visitor_id")
    if not vid:
        vid = str(uuid.uuid4())
        cm.set("ctt_visitor_id", vid, expires_at=None)

    sid = st.session_state.get("ctt_session_id")
    if not sid:
        sid = str(uuid.uuid4())
        st.session_state["ctt_session_id"] = sid

    st.session_state["ctt_visitor_id"] = vid

def _ids():
    return st.session_state["ctt_visitor_id"], st.session_state["ctt_session_id"]

def set_section(name: str):
    st.session_state["section"] = name

def log_event(event: str, props: dict | None = None):
    vid, sid = _ids()
    base = {
        "session_id": sid,
        "section": st.session_state.get("section", "unknown"),
        "app_version": APP_VERSION,
    }
    if props:
        base.update(props)
    _posthog.capture(distinct_id=vid, event=event, properties=base)

def log_page_once(section_key: str):
    set_section(section_key)
    flag = f"_logged_page_{section_key}"
    if not st.session_state.get(flag):
        log_event("page_view")
        st.session_state[flag] = True

# ---------- filter & chart/table helpers ----------
def _hash_filters(d: dict) -> str:
    return hashlib.sha1(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()

def log_filter_if_changed(section_key: str, filters: dict):
    key = f"_last_filters_{section_key}"
    h = _hash_filters(filters)
    if st.session_state.get(key) != h:
        log_event("filter_apply", {"filters": filters})
        st.session_state[key] = h

def log_chart_view(section_key: str, chart_id: str, rows_rendered: int):
    log_event("chart_view", {"chart_id": chart_id, "rows_rendered": int(rows_rendered)})

def log_table_render(section_key: str, table_id: str, rows_rendered: int):
    log_event("table_render", {"table_id": table_id, "rows_rendered": int(rows_rendered)})
