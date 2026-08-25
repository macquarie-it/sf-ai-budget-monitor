"""Shared page orchestration."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from cortex_cost_monitor.components.filters import render_global_filters
from cortex_cost_monitor.components.states import (
    render_data_source_banner,
    render_last_refresh,
    render_query_error,
)
from cortex_cost_monitor.data.container import AppContext
from cortex_cost_monitor.domain.models import CostFilters


def load_page_data(
    title: str, description: str, *, filters_override: CostFilters | None = None
) -> tuple[AppContext, CostFilters, bool, pd.DataFrame] | None:
    st.title(title)
    st.caption(description)
    context: AppContext = st.session_state.app_context
    render_data_source_banner(context)
    selected_filters, show_currency = render_global_filters(context)
    filters = filters_override or selected_filters
    try:
        events = context.repository.load_cost_events(filters)
    except Exception as exc:
        render_query_error(exc)
        return None
    render_last_refresh(events)
    return context, filters, show_currency, events
