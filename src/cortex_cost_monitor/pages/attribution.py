"""Cost attribution page."""

from __future__ import annotations

import streamlit as st

from cortex_cost_monitor.components.charts import coverage_line, stacked_cost_bar
from cortex_cost_monitor.components.metrics import render_summary_metrics
from cortex_cost_monitor.components.states import render_empty_state
from cortex_cost_monitor.components.tables import render_event_table
from cortex_cost_monitor.services.attribution_service import (
    coverage_trend,
    direct_vs_compute,
    status_breakdown,
)
from cortex_cost_monitor.services.overview_service import summarize


def render() -> None:
    from cortex_cost_monitor.pages.common import load_page_data

    loaded = load_page_data(
        "Cost attribution",
        "Trace direct Cortex cost to downstream compute and expose attribution gaps.",
    )
    if loaded is None:
        return
    context, _, show_currency, events = loaded
    if events.empty:
        render_empty_state()
        return

    render_summary_metrics(summarize(events), context.settings, show_currency)
    left, right = st.columns([1.35, 1])
    with left:
        st.plotly_chart(stacked_cost_bar(direct_vs_compute(events)))
    with right:
        st.plotly_chart(coverage_line(coverage_trend(events)))

    st.subheader("Attribution quality")
    status = status_breakdown(events)
    status["coverage_share"] = status["credits"] / max(status["credits"].sum(), 1)
    st.dataframe(
        status,
        width="stretch",
        hide_index=True,
        column_config={
            "credits": st.column_config.NumberColumn("Credits", format="%.4f cr"),
            "coverage_share": st.column_config.ProgressColumn(
                "Share", min_value=0.0, max_value=1.0, format="percent"
            ),
        },
    )

    st.subheader("Incomplete attribution details")
    incomplete = events.loc[events["attribution_status"] != "Complete"].sort_values(
        "total_credits", ascending=False
    )
    if incomplete.empty:
        st.success("All selected cost events have complete attribution.")
    else:
        render_event_table(incomplete, key="attribution")
