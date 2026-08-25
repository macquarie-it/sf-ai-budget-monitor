"""Shared dataframe display and export controls."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from cortex_cost_monitor.services.audit_service import csv_bytes


def render_event_table(events: pd.DataFrame, *, key: str, max_rows: int = 500) -> None:
    display_columns = [
        "event_time",
        "service_type",
        "workload_name",
        "user_name",
        "team",
        "warehouse_name",
        "request_id",
        "query_id",
        "direct_ai_credits",
        "compute_credits",
        "total_credits",
        "outcome",
        "attribution_status",
    ]
    available = [column for column in display_columns if column in events]
    st.dataframe(
        events.loc[:, available].head(max_rows),
        width="stretch",
        hide_index=True,
        column_config={
            "direct_ai_credits": st.column_config.NumberColumn("Direct AI", format="%.4f cr"),
            "compute_credits": st.column_config.NumberColumn("Compute", format="%.4f cr"),
            "total_credits": st.column_config.NumberColumn("Total", format="%.4f cr"),
            "event_time": st.column_config.DatetimeColumn("Event time", format="YYYY-MM-DD HH:mm"),
        },
    )
    st.download_button(
        "Download filtered CSV",
        data=csv_bytes(events.loc[:, available]),
        file_name="cortex_cost_events.csv",
        mime="text/csv",
        key=f"{key}_download",
    )
