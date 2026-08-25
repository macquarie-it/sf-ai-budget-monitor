"""Cortex Analyst page."""

from __future__ import annotations

from dataclasses import replace

import plotly.express as px
import streamlit as st

from cortex_cost_monitor.components.charts import (
    SNOWFLAKE_COLORS,
    contributor_bar,
    daily_cost_chart,
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
from cortex_cost_monitor.config.constants import SERVICE_ANALYST
from cortex_cost_monitor.services.analyst_service import (
    analyst_events,
    warehouse_breakdown,
    workload_ranking,
)
from cortex_cost_monitor.services.overview_service import daily_cost


def render() -> None:
    st.title("Cortex Analyst")
    st.caption("Standalone Analyst usage, generated-query compute, and consumer breakdowns.")
    context = st.session_state.app_context
    render_data_source_banner(context)
    filters, show_currency = render_global_filters(context)
    filters = replace(filters, services=(SERVICE_ANALYST,))
    try:
        events = analyst_events(context.repository.load_cost_events(filters))
    except Exception as exc:
        render_query_error(exc)
        return
    render_last_refresh(events)
    if events.empty:
        render_empty_state("No Cortex Analyst events match the selected filters.")
        return

    render_workload_metrics(
        total_credits=float(events["total_credits"].sum()),
        request_count=int(events["request_count"].sum()),
        failed_requests=int(events.loc[events["outcome"] == "Failed", "request_count"].sum()),
        max_request_credits=float(events["total_credits"].max()),
        settings=context.settings,
        show_currency=show_currency,
    )
    ranking = workload_ranking(events).assign(service_type=SERVICE_ANALYST)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(contributor_bar(ranking, "Analyst workload cost ranking"))
    with right:
        warehouse = warehouse_breakdown(events)
        warehouse_figure = px.bar(
            warehouse,
            x="warehouse_name",
            y="compute_credits",
            color="warehouse_name",
            color_discrete_sequence=SNOWFLAKE_COLORS,
            labels={"warehouse_name": "Warehouse", "compute_credits": "Compute credits"},
            title="Attributed warehouse cost",
        )
        warehouse_figure.update_layout(showlegend=False, height=360)
        st.plotly_chart(warehouse_figure)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(daily_cost_chart(daily_cost(events)))
    with right:
        st.plotly_chart(request_cost_histogram(events))

    st.info(
        "The Snowflake standalone Analyst usage view is hourly and does not expose semantic-model "
        "or generated-query identifiers. Those dimensions require application request logging or "
        "an approved lineage source."
    )
    st.subheader("Highest-cost Analyst activity")
    render_event_table(events.nlargest(100, "total_credits"), key="analyst")
