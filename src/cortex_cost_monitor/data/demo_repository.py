"""Deterministic demonstration data for local UI development."""

from __future__ import annotations

import random
from dataclasses import asdict
from datetime import UTC, datetime, timedelta

import pandas as pd

from cortex_cost_monitor.config.constants import SERVICE_AGENT, SERVICE_ANALYST
from cortex_cost_monitor.domain.models import BudgetDefinition, CostFilters


class DemoCostRepository:
    """In-memory repository with explicit demo-only semantics."""

    read_only = False

    def __init__(self) -> None:
        self._events = _build_demo_events()
        self._budgets = pd.DataFrame(
            [
                {
                    "budget_name": "All Cortex Monthly",
                    "scope_type": "Account",
                    "scope_value": "ALL",
                    "monthly_limit_credits": 1850.0,
                    "warning_threshold": 0.70,
                    "critical_threshold": 0.90,
                    "enabled": True,
                    "updated_at": datetime.now(UTC),
                },
                {
                    "budget_name": "Finance Agent",
                    "scope_type": "Workload",
                    "scope_value": "FINANCE_AGENT",
                    "monthly_limit_credits": 650.0,
                    "warning_threshold": 0.75,
                    "critical_threshold": 0.90,
                    "enabled": True,
                    "updated_at": datetime.now(UTC),
                },
            ]
        )

    def load_cost_events(self, filters: CostFilters, limit: int | None = None) -> pd.DataFrame:
        frame = self._events
        event_dates = frame["event_time"].dt.date
        mask = (event_dates >= filters.start_date) & (event_dates <= filters.end_date)
        if filters.services:
            mask &= frame["service_type"].isin(filters.services)
        if filters.teams:
            mask &= frame["team"].isin(filters.teams)
        if filters.environments:
            mask &= frame["environment"].isin(filters.environments)
        result = frame.loc[mask].sort_values("event_time", ascending=False)
        if limit is not None:
            result = result.head(limit)
        return result.reset_index(drop=True).copy()

    def list_dimensions(self, filters: CostFilters) -> dict[str, list[str]]:
        unfiltered = CostFilters(filters.start_date, filters.end_date)
        frame = self.load_cost_events(unfiltered)
        return {
            "services": sorted(frame["service_type"].dropna().unique().tolist()),
            "teams": sorted(frame["team"].dropna().unique().tolist()),
            "environments": sorted(frame["environment"].dropna().unique().tolist()),
        }

    def load_budgets(self) -> pd.DataFrame:
        return self._budgets.copy()

    def upsert_budget(self, budget: BudgetDefinition) -> None:
        values = asdict(budget) | {"enabled": True, "updated_at": datetime.now(UTC)}
        matches = self._budgets["budget_name"] == budget.budget_name
        if matches.any():
            for key, value in values.items():
                self._budgets.loc[matches, key] = value
        else:
            self._budgets = pd.concat([self._budgets, pd.DataFrame([values])], ignore_index=True)

    def load_ownership_mappings(self) -> pd.DataFrame:
        columns = ["service_type", "workload_name", "team", "cost_center", "environment"]
        return self._events.loc[:, columns].drop_duplicates().sort_values(columns[:2])


def _build_demo_events() -> pd.DataFrame:
    randomizer = random.Random(8147)
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    agents = (
        ("FINANCE_AGENT", "Finance", "CC-100"),
        ("SUPPORT_AGENT", "Customer Success", "CC-220"),
        ("DATA_QUALITY_AGENT", "Data Platform", "CC-310"),
    )
    analysts = (
        ("REVENUE_ANALYST", "Revenue", "CC-120"),
        ("FINANCE_ANALYST", "Finance", "CC-100"),
        ("SUPPORT_ANALYST", "Customer Success", "CC-220"),
    )
    users = ("ALICE", "BEN", "CHEN", "DIEGO", "EMMA", "FATIMA")
    roles = ("ANALYST", "DATA_ENGINEER", "FINOPS", "APP_SERVICE")
    warehouses = ("AI_QUERY_XS", "ANALYTICS_S", "REPORTING_XS")
    rows: list[dict[str, object]] = []

    for index in range(420):
        age_hours = randomizer.randint(0, 24 * 59)
        event_time = now - timedelta(hours=age_hours)
        is_agent = randomizer.random() < 0.63
        workload, team, cost_center = randomizer.choice(agents if is_agent else analysts)
        service_type = SERVICE_AGENT if is_agent else SERVICE_ANALYST
        request_count = 1 if is_agent else randomizer.randint(1, 5)
        token_credits = randomizer.uniform(0.15, 6.4) * request_count
        ai_function_credits = randomizer.uniform(0, 0.8) if is_agent else 0.0
        compute_credits: float | None
        if randomizer.random() < 0.11:
            compute_credits = None
            attribution_status = "Partial"
        else:
            compute_credits = randomizer.uniform(0.02, 3.2) * request_count
            attribution_status = "Complete"
        if randomizer.random() < 0.035:
            workload = ""
            team = "Unassigned"
            cost_center = "Unassigned"
            attribution_status = "Unattributed"
        direct_ai = token_credits + ai_function_credits
        total = direct_ai + float(compute_credits or 0.0)
        outcome = "Failed" if randomizer.random() < 0.07 else "Succeeded"
        request_id = f"demo-req-{index:05d}"
        rows.append(
            {
                "event_time": event_time,
                "service_type": service_type,
                "workload_name": workload or "Unassigned",
                "user_name": randomizer.choice(users),
                "role_name": randomizer.choice(roles),
                "team": team,
                "cost_center": cost_center,
                "environment": "Production" if randomizer.random() < 0.82 else "Development",
                "warehouse_name": randomizer.choice(warehouses) if compute_credits else "",
                "request_id": request_id,
                "query_id": f"demo-query-{index:05d}" if compute_credits else "",
                "token_credits": round(token_credits, 6),
                "ai_function_credits": round(ai_function_credits, 6),
                "direct_ai_credits": round(direct_ai, 6),
                "compute_credits": round(float(compute_credits or 0.0), 6),
                "total_credits": round(total, 6),
                "tokens": randomizer.randint(350, 18000) * request_count,
                "request_count": request_count,
                "outcome": outcome,
                "attribution_status": attribution_status,
            }
        )

    return pd.DataFrame(rows)
