"""Cost attribution quality calculations."""

from __future__ import annotations

import pandas as pd

from cortex_cost_monitor.config.constants import ATTRIBUTION_COMPLETE, ATTRIBUTION_EXCLUDED


def status_breakdown(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(columns=["attribution_status", "credits", "request_count"])
    return (
        events.groupby("attribution_status", as_index=False)
        .agg(credits=("total_credits", "sum"), request_count=("request_count", "sum"))
        .sort_values("credits", ascending=False)
    )


def coverage_trend(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(columns=["usage_date", "coverage"])
    frame = events.copy()
    frame["usage_date"] = frame["event_time"].dt.date
    frame["attributed_credits"] = frame["total_credits"].where(
        frame["attribution_status"].isin([ATTRIBUTION_COMPLETE, ATTRIBUTION_EXCLUDED]), 0.0
    )
    daily = frame.groupby("usage_date", as_index=False)[
        ["total_credits", "attributed_credits"]
    ].sum()
    daily["coverage"] = daily["attributed_credits"].div(
        daily["total_credits"].where(daily["total_credits"] > 0, 1)
    )
    return daily


def direct_vs_compute(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(columns=["workload_name", "Direct AI", "Compute"])
    result = events.groupby("workload_name", as_index=False)[
        ["direct_ai_credits", "compute_credits"]
    ].sum()
    return result.rename(
        columns={"direct_ai_credits": "Direct AI", "compute_credits": "Compute"}
    ).sort_values(["Direct AI", "Compute"], ascending=False)
