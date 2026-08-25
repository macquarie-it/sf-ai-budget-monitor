"""Request-level audit page."""

from __future__ import annotations

import streamlit as st

from cortex_cost_monitor.components.states import render_empty_state
from cortex_cost_monitor.components.tables import render_event_table
from cortex_cost_monitor.services.audit_service import search_events


def render() -> None:
    from cortex_cost_monitor.pages.common import load_page_data

    loaded = load_page_data(
        "Audit details",
        "Search, inspect, and export request-level cost evidence.",
    )
    if loaded is None:
        return
    _, _, _, events = loaded
    search_term = st.text_input(
        "Search",
        placeholder="Request ID, query ID, user, workload, team, or warehouse",
    )
    filtered = search_events(events, search_term)
    if filtered.empty:
        render_empty_state("No audit records match the selected filters and search term.")
        return
    st.metric("Matching events", f"{len(filtered):,}")
    render_event_table(filtered, key="audit", max_rows=1000)
