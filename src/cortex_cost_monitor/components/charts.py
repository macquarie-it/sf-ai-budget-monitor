"""Shared Plotly chart builders."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

SNOWFLAKE_COLORS = ["#29B5E8", "#7C6EE6", "#F29D49", "#24A37A", "#E35D6A", "#63788A"]


def _style(figure: go.Figure, *, height: int = 360) -> go.Figure:
    figure.update_layout(
        height=height,
        margin=dict(l=16, r=16, t=42, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
        hovermode="x unified",
    )
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(gridcolor="rgba(128,128,128,0.18)", zeroline=False)
    return figure


def daily_cost_chart(daily: pd.DataFrame) -> go.Figure:
    figure = px.line(
        daily,
        x="usage_date",
        y="total_credits",
        color="service_type",
        markers=True,
        color_discrete_sequence=SNOWFLAKE_COLORS,
        labels={"usage_date": "Date", "total_credits": "Credits", "service_type": "Service"},
        title="Daily cost trend",
    )
    return _style(figure)


def composition_donut(composition: pd.DataFrame) -> go.Figure:
    figure = px.pie(
        composition,
        names="cost_type",
        values="credits",
        hole=0.62,
        color_discrete_sequence=SNOWFLAKE_COLORS,
        title="Cost composition",
    )
    figure.update_traces(textposition="inside", textinfo="percent+label")
    return _style(figure)


def contributor_bar(contributors: pd.DataFrame, title: str = "Top cost contributors") -> go.Figure:
    ordered = contributors.sort_values("total_credits", ascending=True)
    figure = px.bar(
        ordered,
        x="total_credits",
        y="workload_name",
        color="service_type" if "service_type" in ordered else None,
        orientation="h",
        color_discrete_sequence=SNOWFLAKE_COLORS,
        labels={"total_credits": "Credits", "workload_name": "Workload"},
        title=title,
    )
    return _style(figure)


def request_cost_histogram(events: pd.DataFrame) -> go.Figure:
    figure = px.histogram(
        events,
        x="total_credits",
        nbins=24,
        color="workload_name",
        color_discrete_sequence=SNOWFLAKE_COLORS,
        labels={"total_credits": "Credits per event", "count": "Events"},
        title="Cost per event distribution",
    )
    return _style(figure)


def efficiency_scatter(efficiency: pd.DataFrame) -> go.Figure:
    figure = px.scatter(
        efficiency,
        x="request_count",
        y="credits_per_request",
        size="total_credits",
        color="workload_name",
        text="workload_name",
        color_discrete_sequence=SNOWFLAKE_COLORS,
        labels={"request_count": "Requests", "credits_per_request": "Credits per request"},
        title="Volume and unit cost",
    )
    figure.update_traces(textposition="top center")
    return _style(figure)


def stacked_cost_bar(costs: pd.DataFrame) -> go.Figure:
    melted = costs.melt(
        id_vars="workload_name",
        value_vars=["Direct AI", "Compute"],
        var_name="cost_type",
        value_name="credits",
    )
    figure = px.bar(
        melted,
        x="workload_name",
        y="credits",
        color="cost_type",
        color_discrete_sequence=SNOWFLAKE_COLORS,
        labels={"workload_name": "Workload", "credits": "Credits"},
        title="Direct and attributed compute cost",
    )
    return _style(figure)


def coverage_line(coverage: pd.DataFrame) -> go.Figure:
    figure = px.line(
        coverage,
        x="usage_date",
        y="coverage",
        markers=True,
        color_discrete_sequence=SNOWFLAKE_COLORS,
        labels={"usage_date": "Date", "coverage": "Coverage"},
        title="Attribution coverage trend",
    )
    figure.update_yaxes(tickformat=".0%", range=[0, 1.05])
    return _style(figure)


def budget_bar(budgets: pd.DataFrame) -> go.Figure:
    frame = budgets.copy()
    frame["utilization_percent"] = frame["utilization"] * 100
    figure = px.bar(
        frame,
        x="budget_name",
        y="utilization_percent",
        color="state",
        color_discrete_map={
            "On track": "#24A37A",
            "Warning": "#F29D49",
            "Critical": "#E35D6A",
            "Exceeded": "#B73A48",
        },
        labels={"budget_name": "Budget", "utilization_percent": "Utilization (%)"},
        title="Budget utilization",
    )
    figure.add_hline(y=100, line_dash="dash", line_color="#E35D6A")
    return _style(figure)
