"""Loading, empty, stale, and data-source states."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from cortex_cost_monitor.data.container import AppContext


def render_data_source_banner(context: AppContext) -> None:
    if context.data_mode == "demo":
        detail = " Synthetic records are being used for UI development."
        if context.diagnostic:
            detail += " Configure a Snowflake connection or set CORTEX_COST_DATA_MODE=snowflake."
        st.warning(f"Demo data mode.{detail}", icon="⚠️")


def render_last_refresh(events: pd.DataFrame) -> None:
    if events.empty or events["event_time"].isna().all():
        st.caption("No source refresh timestamp is available for the selected filters.")
        return
    refreshed_at = events["event_time"].max()
    st.caption(f"Latest source event in this view: {refreshed_at:%Y-%m-%d %H:%M %Z}")


def render_empty_state(message: str = "No cost events match the selected filters.") -> None:
    st.info(message, icon="ℹ️")


def render_query_error(exc: Exception) -> None:
    st.error(
        "The cost dataset could not be loaded. Verify the curated views, role grants, "
        "warehouse, and selected date range.",
        icon="🚨",
    )
    with st.expander("Diagnostic details"):
        st.code(str(exc))
