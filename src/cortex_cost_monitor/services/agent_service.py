"""Cortex Agent analysis calculations."""

from __future__ import annotations

import pandas as pd

from cortex_cost_monitor.config.constants import SERVICE_AGENT


def agent_events(events: pd.DataFrame) -> pd.DataFrame:
    return events.loc[events["service_type"] == SERVICE_AGENT].copy()


def workload_ranking(events: pd.DataFrame) -> pd.DataFrame:
    frame = agent_events(events)
    if frame.empty:
        return pd.DataFrame(columns=["workload_name", "total_credits", "request_count"])
    return (
        frame.groupby("workload_name", as_index=False)[["total_credits", "request_count"]]
        .sum()
        .sort_values("total_credits", ascending=False)
    )


def workload_efficiency(events: pd.DataFrame) -> pd.DataFrame:
    ranking = workload_ranking(events)
    if ranking.empty:
        ranking["credits_per_request"] = pd.Series(dtype=float)
        return ranking
    ranking["credits_per_request"] = ranking["total_credits"].div(
        ranking["request_count"].where(ranking["request_count"] > 0, 1)
    )
    return ranking
