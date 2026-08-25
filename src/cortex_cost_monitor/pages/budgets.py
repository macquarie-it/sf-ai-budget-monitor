"""Budgets and alerts page."""

from __future__ import annotations

from dataclasses import replace
from datetime import date

import streamlit as st

from cortex_cost_monitor.components.charts import budget_bar
from cortex_cost_monitor.components.states import render_empty_state
from cortex_cost_monitor.domain.models import BudgetDefinition
from cortex_cost_monitor.services.budget_service import evaluate_budgets


def render() -> None:
    from cortex_cost_monitor.pages.common import load_page_data

    loaded = load_page_data(
        "Budgets & alerts",
        "Track selected-period expenditure against configurable credit limits.",
    )
    if loaded is None:
        return
    context, filters, _, _ = loaded
    month_to_date_filters = replace(
        filters, start_date=date.today().replace(day=1), end_date=date.today()
    )
    try:
        events = context.repository.load_cost_events(month_to_date_filters)
        budgets = context.repository.load_budgets()
    except Exception as exc:
        st.error(f"Budget definitions could not be loaded: {exc}")
        return

    st.caption(
        "Utilization is calculated month-to-date; service, team, and environment filters apply."
    )
    status = evaluate_budgets(budgets, events)
    if status.empty:
        render_empty_state("No budget definitions are configured.")
    else:
        st.plotly_chart(budget_bar(status))
        st.dataframe(
            status,
            width="stretch",
            hide_index=True,
            column_config={
                "monthly_limit_credits": st.column_config.NumberColumn("Limit", format="%.2f cr"),
                "spent_credits": st.column_config.NumberColumn("Spent", format="%.2f cr"),
                "remaining_credits": st.column_config.NumberColumn("Remaining", format="%.2f cr"),
                "utilization": st.column_config.ProgressColumn(
                    "Utilization", min_value=0.0, max_value=1.0, format="percent"
                ),
            },
        )

    with st.expander("Add or update a budget"):
        with st.form("budget_form"):
            budget_name = st.text_input("Budget name")
            scope_type = st.selectbox(
                "Scope type",
                ["Account", "Workload", "Team", "Cost Center", "Environment", "Service"],
            )
            scope_value = st.text_input(
                "Scope value", value="ALL" if scope_type == "Account" else ""
            )
            limit = st.number_input("Monthly limit (credits)", min_value=0.01, value=1000.0)
            warning = st.slider("Warning threshold", 0.10, 0.85, 0.70, 0.05)
            critical = st.slider(
                "Critical threshold", warning + 0.05, 1.00, max(0.90, warning + 0.05), 0.05
            )
            submitted = st.form_submit_button("Save budget", type="primary")
        if submitted:
            if not budget_name.strip() or not scope_value.strip():
                st.error("Budget name and scope value are required.")
            else:
                try:
                    context.repository.upsert_budget(
                        BudgetDefinition(
                            budget_name=budget_name.strip(),
                            scope_type=scope_type,
                            scope_value=scope_value.strip(),
                            monthly_limit_credits=float(limit),
                            warning_threshold=float(warning),
                            critical_threshold=float(critical),
                        )
                    )
                    st.success("Budget saved. Rerun the page to refresh utilization.")
                except Exception as exc:
                    st.error(f"The budget could not be saved: {exc}")
