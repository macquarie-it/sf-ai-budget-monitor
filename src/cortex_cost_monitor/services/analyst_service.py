"""Cortex Analyst analysis calculations."""

from __future__ import annotations

import pandas as pd

from cortex_cost_monitor.config.constants import SERVICE_ANALYST


def analyst_events(events: pd.DataFrame) -> pd.DataFrame:
    return events.loc[events["service_type"] == SERVICE_ANALYST].copy()


def workload_ranking(events: pd.DataFrame) -> pd.DataFrame:
    frame = analyst_events(events)
    if frame.empty:
        return pd.DataFrame(columns=["workload_name", "total_credits", "request_count"])
    return (
        frame.groupby("workload_name", as_index=False)[["total_credits", "request_count"]]
        .sum()
        .sort_values("total_credits", ascending=False)
    )


def warehouse_breakdown(events: pd.DataFrame) -> pd.DataFrame:
    frame = analyst_events(events)
    if frame.empty:
        return pd.DataFrame(columns=["warehouse_name", "compute_credits"])
    frame["warehouse_name"] = frame["warehouse_name"].replace("", "Not attributed")
    return (
        frame.groupby("warehouse_name", as_index=False)["compute_credits"]
        .sum()
        .sort_values("compute_credits", ascending=False)
    )
