"""Thin Streamlit host for the pre-built React dashboard."""

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Snowflake AI Credit Control",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

bundle_path = Path(__file__).parent / "streamlit_app" / "frontend" / "index.html"

if not bundle_path.exists():
    st.error(
        "The React bundle is missing. Run `npm run build:streamlit` before "
        "starting or deploying the Streamlit app."
    )
    st.stop()

components.html(bundle_path.read_text(encoding="utf-8"), height=1500, scrolling=True)

