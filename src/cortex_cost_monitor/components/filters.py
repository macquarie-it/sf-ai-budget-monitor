"""Shared application filters."""

from __future__ import annotations

from datetime import date

import streamlit as st

from cortex_cost_monitor.data.container import AppContext
from cortex_cost_monitor.domain.models import CostFilters
from cortex_cost_monitor.utils.dates import default_date_range


def render_global_filters(context: AppContext) -> tuple[CostFilters, bool]:
    """Render stable sidebar filters and return the selected state."""

    st.sidebar.markdown("### Filters")
    default_start, default_end = default_date_range()
    selected_range = st.sidebar.date_input(
        "Reporting period",
        value=(default_start, default_end),
        max_value=date.today(),
        key="global_reporting_period",
    )
    if isinstance(selected_range, tuple) and len(selected_range) == 2:
        start_date, end_date = selected_range
    else:
        start_date = end_date = selected_range

    dimension_filters = CostFilters(start_date=start_date, end_date=end_date)
    try:
        dimensions = context.repository.list_dimensions(dimension_filters)
    except Exception:
        dimensions = {"services": [], "teams": [], "environments": []}

    services = st.sidebar.multiselect(
        "Service",
        options=dimensions["services"],
        default=dimensions["services"],
        key="global_services",
    )
    teams = st.sidebar.multiselect(
        "Team",
        options=dimensions["teams"],
        default=dimensions["teams"],
        key="global_teams",
    )
    environments = st.sidebar.multiselect(
        "Environment",
        options=dimensions["environments"],
        default=dimensions["environments"],
        key="global_environments",
    )
    show_currency = st.sidebar.toggle(
        f"Show estimated {context.settings.currency}",
        value=False,
        help="Currency values use the configured contract estimate per Snowflake credit.",
        key="global_show_currency",
    )
    st.sidebar.caption(
        f"Currency estimate: {context.settings.currency} "
        f"{context.settings.credit_price:,.2f} per credit"
    )
    return (
        CostFilters(
            start_date=start_date,
            end_date=end_date,
            services=tuple(services),
            teams=tuple(teams),
            environments=tuple(environments),
        ),
        show_currency,
    )
