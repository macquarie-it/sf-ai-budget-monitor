"""Application navigation and global styling."""

from __future__ import annotations

import streamlit as st

from cortex_cost_monitor.pages import (
    agents,
    analyst,
    attribution,
    audit,
    budgets,
    overview,
    settings,
)


def build_navigation():
    st.markdown(
        """
        <style>
        [data-testid="stMetric"] {
            background: color-mix(in srgb, var(--secondary-background-color) 94%, #29B5E8 6%);
            border: 1px solid rgba(128, 128, 128, 0.20);
            padding: 0.85rem 1rem;
            border-radius: 0.65rem;
        }
        [data-testid="stMetricLabel"] { font-weight: 600; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    return st.navigation(
        {
            "Monitor": [
                st.Page(
                    overview.render,
                    title="Overview",
                    icon="📊",
                    url_path="overview",
                    default=True,
                ),
                st.Page(agents.render, title="Cortex Agents", icon="🤖", url_path="agents"),
                st.Page(analyst.render, title="Cortex Analyst", icon="🔎", url_path="analyst"),
                st.Page(
                    attribution.render,
                    title="Cost Attribution",
                    icon="🔗",
                    url_path="attribution",
                ),
            ],
            "Control": [
                st.Page(
                    budgets.render,
                    title="Budgets & Alerts",
                    icon="🎯",
                    url_path="budgets",
                ),
                st.Page(audit.render, title="Audit Details", icon="🧾", url_path="audit"),
                st.Page(settings.render, title="Settings", icon="⚙️", url_path="settings"),
            ],
        }
    )
