"""Cortex Agents page."""

from __future__ import annotations

from dataclasses import replace

import streamlit as st

from cortex_cost_monitor.components.charts import (
    contributor_bar,
    daily_cost_chart,
    efficiency_scatter,
    request_cost_histogram,
)
from cortex_cost_monitor.components.filters import render_global_filters
from cortex_cost_monitor.components.metrics import render_workload_metrics
from cortex_cost_monitor.components.states import (
    render_data_source_banner,
    render_empty_state,
    render_last_refresh,
    render_query_error,
)
from cortex_cost_monitor.components.tables import render_event_table
from cortex_cost_monitor.config.constants import SERVICE_AGENT
from cortex_cost_monitor.services.agent_service import (
    agent_events,
    workload_efficiency,
    workload_ranking,
)
from cortex_cost_monitor.services.overview_service import daily_cost


def render() -> None:
    st.title("Cortex Agents")
    st.caption("Agent costs, request volume, unit economics, ownership, and expensive requests.")
    context = st.session_state.app_context
    render_data_source_banner(context)
    filters, show_currency = render_global_filters(context)
    filters = replace(filters, services=(SERVICE_AGENT,))
    try:
        events = agent_events(context.repository.load_cost_events(filters))
    except Exception as exc:
        render_query_error(exc)
        return
    render_last_refresh(events)
    if events.empty:
        render_empty_state("No Cortex Agent events match the selected filters.")
        return

    render_workload_metrics(
        total_credits=float(events["total_credits"].sum()),
        request_count=int(events["request_count"].sum()),
        failed_requests=int(events.loc[events["outcome"] == "Failed", "request_count"].sum()),
        max_request_credits=float(events["total_credits"].max()),
        settings=context.settings,
        show_currency=show_currency,
    )
    ranking = workload_ranking(events)
    ranking_for_chart = ranking.assign(service_type=SERVICE_AGENT)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(contributor_bar(ranking_for_chart, "Agent cost ranking"))
    with right:
        st.plotly_chart(efficiency_scatter(workload_efficiency(events)))
    left, right = st.columns(2)
    with left:
        st.plotly_chart(daily_cost_chart(daily_cost(events)))
    with right:
        st.plotly_chart(request_cost_histogram(events))

    st.subheader("Highest-cost Agent requests")
    render_event_table(events.nlargest(100, "total_credits"), key="agents")
