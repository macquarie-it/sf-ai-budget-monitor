"""Budget state and utilization rules."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BudgetStatus:
    utilization: float
    remaining_credits: float
    state: str


def calculate_budget_status(
    spent_credits: float,
    limit_credits: float,
    warning_threshold: float = 0.7,
    critical_threshold: float = 0.9,
) -> BudgetStatus:
    """Calculate utilization and a stable state label."""

    if limit_credits <= 0:
        raise ValueError("limit_credits must be positive")
    if not 0 < warning_threshold < critical_threshold <= 1:
        raise ValueError("thresholds must satisfy 0 < warning < critical <= 1")

    utilization = max(0.0, spent_credits / limit_credits)
    if utilization >= 1:
        state = "Exceeded"
    elif utilization >= critical_threshold:
        state = "Critical"
    elif utilization >= warning_threshold:
        state = "Warning"
    else:
        state = "On track"

    return BudgetStatus(
        utilization=utilization,
        remaining_credits=max(0.0, limit_credits - spent_credits),
        state=state,
    )
