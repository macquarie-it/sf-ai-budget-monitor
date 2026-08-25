"""Snowflake Cortex Cost Monitor entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

SOURCE_ROOT = Path(__file__).parent / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from cortex_cost_monitor.data.container import build_app_context  # noqa: E402
from cortex_cost_monitor.navigation import build_navigation  # noqa: E402

st.set_page_config(
    page_title="Cortex Cost Monitor",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "app_context" not in st.session_state:
    st.session_state.app_context = build_app_context()

navigation = build_navigation()
navigation.run()
