"""Streamlit host that executes dashboard.sql inside deployed Snowflake."""

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from dashboard_runtime import execute_dashboard_sql


st.set_page_config(
    page_title="Snowflake AI Credit Control",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

app_root = Path(__file__).parent
bundle_path = app_root / "streamlit_app" / "frontend" / "index.html"
sql_config_path = app_root / "config" / "dashboard.sql"

if not bundle_path.exists():
    st.error(
        "The React bundle is missing. Run `npm run build:streamlit` before "
        "starting or deploying the Streamlit app."
    )
    st.stop()

if not sql_config_path.exists():
    st.error("The SQL dashboard config is missing: config/dashboard.sql")
    st.stop()


def _active_snowflake_session():
    try:
        from snowflake.snowpark.context import get_active_session

        return get_active_session()
    except (ImportError, RuntimeError):
        return None


html = bundle_path.read_text(encoding="utf-8")
session = _active_snowflake_session()

if session is not None:
    try:
        live_data = execute_dashboard_sql(session, sql_config_path)
    except Exception as error:
        st.error(str(error))
        st.exception(error)
        st.stop()

    encoded_data = (
        json.dumps(live_data, ensure_ascii=False, separators=(",", ":"))
        .replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    bootstrap = f"<script>window.__DASHBOARD_DATA__={encoded_data};</script>"
    html = html.replace("<head>", f"<head>{bootstrap}", 1)

components.html(html, height=2050, scrolling=True)
