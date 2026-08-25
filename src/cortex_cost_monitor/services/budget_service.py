"""Budget utilization orchestration."""

from __future__ import annotations

import pandas as pd

from cortex_cost_monitor.domain.budget_rules import calculate_budget_status


def evaluate_budgets(budgets: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    if budgets.empty:
        return pd.DataFrame(
            columns=[
                "budget_name",
                "scope_type",
                "scope_value",
                "monthly_limit_credits",
                "spent_credits",
                "remaining_credits",
                "utilization",
                "state",
            ]
        )

    rows: list[dict[str, object]] = []
    for budget in budgets.to_dict("records"):
        scoped_events = _events_for_scope(
            events, str(budget["scope_type"]), str(budget["scope_value"])
        )
        spent = float(scoped_events["total_credits"].sum()) if not scoped_events.empty else 0.0
        status = calculate_budget_status(
            spent,
            float(budget["monthly_limit_credits"]),
            float(budget.get("warning_threshold", 0.7)),
            float(budget.get("critical_threshold", 0.9)),
        )
        rows.append(
            budget
            | {
                "spent_credits": spent,
                "remaining_credits": status.remaining_credits,
                "utilization": status.utilization,
                "state": status.state,
            }
        )
    return pd.DataFrame(rows).sort_values("utilization", ascending=False)


def _events_for_scope(events: pd.DataFrame, scope_type: str, scope_value: str) -> pd.DataFrame:
    normalized = scope_type.strip().lower()
    if normalized == "account" or scope_value.upper() == "ALL":
        return events
    mapping = {
        "workload": "workload_name",
        "agent": "workload_name",
        "analyst": "workload_name",
        "team": "team",
        "cost center": "cost_center",
        "environment": "environment",
        "service": "service_type",
    }
    column = mapping.get(normalized)
    if column is None:
        return events.iloc[0:0]
    return events.loc[events[column] == scope_value]
