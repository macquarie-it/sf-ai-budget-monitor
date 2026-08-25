"""Administrative settings and data-source status page."""

from __future__ import annotations

import streamlit as st

from cortex_cost_monitor.components.states import render_data_source_banner


def render() -> None:
    st.title("Settings")
    st.caption("Runtime configuration, ownership mappings, and data-source readiness.")
    context = st.session_state.app_context
    render_data_source_banner(context)

    st.subheader("Runtime configuration")
    st.json(
        {
            "data_mode": context.data_mode,
            "currency": context.settings.currency,
            "credit_price_estimate": context.settings.credit_price,
            "cost_view": context.settings.cost_view,
            "budget_table": context.settings.budget_table,
            "ownership_table": context.settings.ownership_table,
        },
        expanded=True,
    )
    st.caption("Credential and secret values are never displayed by this application.")

    st.subheader("Ownership mappings")
    try:
        mappings = context.repository.load_ownership_mappings()
    except Exception as exc:
        st.error(f"Ownership mappings could not be loaded: {exc}")
    else:
        st.dataframe(mappings, width="stretch", hide_index=True)

    st.subheader("Snowflake source expectations")
    st.markdown(
        """
        - `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENT_USAGE_HISTORY` supplies Agent request, token,
          model, role, and attributed SQL credit data.
        - `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE_HISTORY` supplies hourly standalone
          Analyst message and credit totals.
        - Agent request data can lag by approximately one hour; SQL credit attribution can lag
          by up to approximately eight hours.
        - The curated `V_COST_EVENTS` view is the application contract and prevents the UI from
          querying raw Account Usage views directly.
        """
    )
