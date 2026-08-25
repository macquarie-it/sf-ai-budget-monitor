"""Reusable KPI rendering."""

from __future__ import annotations

import streamlit as st

from cortex_cost_monitor.config.settings import AppSettings
from cortex_cost_monitor.domain.models import CostSummary
from cortex_cost_monitor.utils.formatting import format_cost


def render_summary_metrics(
    summary: CostSummary, settings: AppSettings, show_currency: bool
) -> None:
    columns = st.columns(5)
    values = (
        ("Total attributed cost", summary.total_credits),
        ("Direct AI cost", summary.direct_ai_credits),
        ("Attributed compute", summary.compute_credits),
    )
    for column, (label, value) in zip(columns, values, strict=False):
        column.metric(
            label, format_cost(value, settings.credit_price, settings.currency, show_currency)
        )
    columns[3].metric("Requests", f"{summary.request_count:,}")
    columns[4].metric("Attribution coverage", f"{summary.attribution_coverage:.1%}")


def render_workload_metrics(
    *,
    total_credits: float,
    request_count: int,
    failed_requests: int,
    max_request_credits: float,
    settings: AppSettings,
    show_currency: bool,
) -> None:
    average = total_credits / request_count if request_count else 0.0
    columns = st.columns(5)
    columns[0].metric(
        "Total cost",
        format_cost(total_credits, settings.credit_price, settings.currency, show_currency),
    )
    columns[1].metric("Requests", f"{request_count:,}")
    columns[2].metric("Failed requests", f"{failed_requests:,}")
    columns[3].metric(
        "Average per request",
        format_cost(average, settings.credit_price, settings.currency, show_currency),
    )
    columns[4].metric(
        "Highest-cost event",
        format_cost(max_request_credits, settings.credit_price, settings.currency, show_currency),
    )
