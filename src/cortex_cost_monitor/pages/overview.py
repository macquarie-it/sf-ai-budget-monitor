"""Overview dashboard page."""

from __future__ import annotations

import streamlit as st

from cortex_cost_monitor.components.charts import (
    composition_donut,
    contributor_bar,
    daily_cost_chart,
)
from cortex_cost_monitor.components.metrics import render_summary_metrics
from cortex_cost_monitor.components.states import render_empty_state
from cortex_cost_monitor.services.budget_service import evaluate_budgets
from cortex_cost_monitor.services.overview_service import (
    anomaly_candidates,
    cost_composition,
    daily_cost,
    summarize,
    top_contributors,
)
from cortex_cost_monitor.utils.formatting import format_cost


def render() -> None:
    from cortex_cost_monitor.pages.common import load_page_data

    loaded = load_page_data(
        "Cost overview",
        "Cortex AI and attributed downstream compute expenditure.",
    )
    if loaded is None:
        return
    context, _, show_currency, events = loaded
    if events.empty:
        render_empty_state()
        return

    summary = summarize(events)
    render_summary_metrics(summary, context.settings, show_currency)

    left, right = st.columns([1.7, 1])
    with left:
        st.plotly_chart(daily_cost_chart(daily_cost(events)))
    with right:
        st.plotly_chart(composition_donut(cost_composition(events)))

    left, right = st.columns([1.45, 1])
    contributors = top_contributors(events)
    with left:
        st.plotly_chart(contributor_bar(contributors))
    with right:
        st.subheader("Attention required")
        try:
            budget_status = evaluate_budgets(context.repository.load_budgets(), events)
        except Exception:
            budget_status = None
        if budget_status is not None and not budget_status.empty:
            for row in budget_status.loc[budget_status["state"] != "On track"].head(3).itertuples():
                st.warning(
                    f"**{row.budget_name}** — {row.state} at {row.utilization:.0%} utilization"
                )
        unattributed = events.loc[events["attribution_status"] != "Complete", "total_credits"].sum()
        if unattributed > 0:
            unattributed_label = format_cost(
                float(unattributed),
                context.settings.credit_price,
                context.settings.currency,
                show_currency,
            )
            st.info(f"**Attribution review** — {unattributed_label} is partial or unattributed.")
        anomalies = anomaly_candidates(events, limit=3)
        for row in anomalies.itertuples():
            cost_label = format_cost(
                row.total_credits,
                context.settings.credit_price,
                context.settings.currency,
                show_currency,
            )
            st.error(f"**High-cost event** — {row.workload_name}: {cost_label}")

    st.subheader("Top contributor details")
    st.dataframe(contributors, width="stretch", hide_index=True)
