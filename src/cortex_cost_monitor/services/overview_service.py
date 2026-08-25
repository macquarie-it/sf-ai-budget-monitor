"""Overview dashboard calculations."""

from __future__ import annotations

import pandas as pd

from cortex_cost_monitor.config.constants import ATTRIBUTION_COMPLETE, ATTRIBUTION_EXCLUDED
from cortex_cost_monitor.domain.models import CostSummary


def summarize(events: pd.DataFrame) -> CostSummary:
    if events.empty:
        return CostSummary(0.0, 0.0, 0.0, 0, 1.0)

    total = float(events["total_credits"].sum())
    attributed_mask = events["attribution_status"].isin(
        [ATTRIBUTION_COMPLETE, ATTRIBUTION_EXCLUDED]
    )
    attributed = float(events.loc[attributed_mask, "total_credits"].sum())
    coverage = 1.0 if total <= 0 else attributed / total
    return CostSummary(
        direct_ai_credits=float(events["direct_ai_credits"].sum()),
        compute_credits=float(events["compute_credits"].sum()),
        total_credits=total,
        request_count=int(events["request_count"].sum()),
        attribution_coverage=max(0.0, min(1.0, coverage)),
    )


def daily_cost(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(
            columns=[
                "usage_date",
                "service_type",
                "direct_ai_credits",
                "compute_credits",
                "total_credits",
            ]
        )
    frame = events.copy()
    frame["usage_date"] = frame["event_time"].dt.date
    return (
        frame.groupby(["usage_date", "service_type"], as_index=False)[
            ["direct_ai_credits", "compute_credits", "total_credits"]
        ]
        .sum()
        .sort_values("usage_date")
    )


def cost_composition(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(columns=["cost_type", "credits"])
    direct = float(events["direct_ai_credits"].sum())
    compute = float(events["compute_credits"].sum())
    return pd.DataFrame(
        [
            {"cost_type": "Direct AI", "credits": direct},
            {"cost_type": "Attributed compute", "credits": compute},
        ]
    )


def top_contributors(events: pd.DataFrame, limit: int = 8) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(columns=["workload_name", "service_type", "team", "total_credits"])
    return (
        events.groupby(["workload_name", "service_type", "team"], as_index=False)["total_credits"]
        .sum()
        .sort_values("total_credits", ascending=False)
        .head(limit)
    )


def anomaly_candidates(events: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    """Surface simple deterministic candidates until a forecast model is introduced."""

    if events.empty:
        return pd.DataFrame(columns=events.columns)
    threshold = events["total_credits"].quantile(0.97)
    return events.loc[events["total_credits"] >= threshold].nlargest(limit, "total_credits")
