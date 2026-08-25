"""Repository interfaces and shared result normalization."""

from __future__ import annotations

from typing import Protocol

import pandas as pd

from cortex_cost_monitor.domain.models import BudgetDefinition, CostFilters


class CostRepository(Protocol):
    """Data operations required by the application services."""

    read_only: bool

    def load_cost_events(self, filters: CostFilters, limit: int | None = None) -> pd.DataFrame: ...

    def list_dimensions(self, filters: CostFilters) -> dict[str, list[str]]: ...

    def load_budgets(self) -> pd.DataFrame: ...

    def upsert_budget(self, budget: BudgetDefinition) -> None: ...

    def load_ownership_mappings(self) -> pd.DataFrame: ...


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize Snowflake uppercase result columns for application code."""

    result = frame.copy()
    result.columns = [str(column).lower() for column in result.columns]
    if "event_time" in result:
        result["event_time"] = pd.to_datetime(result["event_time"], utc=True, errors="coerce")
    return result
