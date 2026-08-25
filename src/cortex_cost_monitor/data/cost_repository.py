"""Snowflake implementation of the cost repository."""

from __future__ import annotations

import re
from datetime import timedelta
from typing import Any

import pandas as pd

from cortex_cost_monitor.data.repositories import normalize_columns
from cortex_cost_monitor.domain.models import BudgetDefinition, CostFilters

_IDENTIFIER = re.compile(
    r'^(?:"[^"]+"|[A-Za-z_][A-Za-z0-9_$]*)(?:\.(?:"[^"]+"|[A-Za-z_][A-Za-z0-9_$]*))*$'
)


def _validated_identifier(value: str) -> str:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"Unsafe Snowflake identifier: {value!r}")
    return value


class SnowflakeCostRepository:
    """Query curated application views through an existing Snowpark session."""

    read_only = False

    def __init__(self, session: Any, *, cost_view: str, budget_table: str, ownership_table: str):
        self._session = session
        self._cost_view = _validated_identifier(cost_view)
        self._budget_table = _validated_identifier(budget_table)
        self._ownership_table = _validated_identifier(ownership_table)

    def load_cost_events(self, filters: CostFilters, limit: int | None = None) -> pd.DataFrame:
        clauses = ["EVENT_TIME >= ?", "EVENT_TIME < ?"]
        params: list[Any] = [filters.start_date, filters.end_date + timedelta(days=1)]
        self._append_in_filter(clauses, params, "SERVICE_TYPE", filters.services)
        self._append_in_filter(clauses, params, "TEAM", filters.teams)
        self._append_in_filter(clauses, params, "ENVIRONMENT", filters.environments)
        limit_sql = "" if limit is None else f" LIMIT {max(1, int(limit))}"
        query = f"""
            SELECT *
            FROM {self._cost_view}
            WHERE {" AND ".join(clauses)}
            ORDER BY EVENT_TIME DESC
            {limit_sql}
        """
        return normalize_columns(self._session.sql(query, params=params).to_pandas())

    def list_dimensions(self, filters: CostFilters) -> dict[str, list[str]]:
        query = f"""
            SELECT
                ARRAY_AGG(DISTINCT SERVICE_TYPE) WITHIN GROUP (ORDER BY SERVICE_TYPE) AS SERVICES,
                ARRAY_AGG(DISTINCT TEAM) WITHIN GROUP (ORDER BY TEAM) AS TEAMS,
                ARRAY_AGG(DISTINCT ENVIRONMENT) WITHIN GROUP (ORDER BY ENVIRONMENT) AS ENVIRONMENTS
            FROM {self._cost_view}
            WHERE EVENT_TIME >= ? AND EVENT_TIME < ?
        """
        rows = self._session.sql(
            query, params=[filters.start_date, filters.end_date + timedelta(days=1)]
        ).collect()
        if not rows:
            return {"services": [], "teams": [], "environments": []}
        row = rows[0]
        return {
            "services": list(row["SERVICES"] or []),
            "teams": list(row["TEAMS"] or []),
            "environments": list(row["ENVIRONMENTS"] or []),
        }

    def load_budgets(self) -> pd.DataFrame:
        query = f"SELECT * FROM {self._budget_table} WHERE ENABLED ORDER BY BUDGET_NAME"
        return normalize_columns(self._session.sql(query).to_pandas())

    def upsert_budget(self, budget: BudgetDefinition) -> None:
        query = f"""
            MERGE INTO {self._budget_table} target
            USING (
                SELECT ? AS BUDGET_NAME, ? AS SCOPE_TYPE, ? AS SCOPE_VALUE,
                       ? AS MONTHLY_LIMIT_CREDITS, ? AS WARNING_THRESHOLD,
                       ? AS CRITICAL_THRESHOLD
            ) source
            ON target.BUDGET_NAME = source.BUDGET_NAME
            WHEN MATCHED THEN UPDATE SET
                SCOPE_TYPE = source.SCOPE_TYPE,
                SCOPE_VALUE = source.SCOPE_VALUE,
                MONTHLY_LIMIT_CREDITS = source.MONTHLY_LIMIT_CREDITS,
                WARNING_THRESHOLD = source.WARNING_THRESHOLD,
                CRITICAL_THRESHOLD = source.CRITICAL_THRESHOLD,
                ENABLED = TRUE,
                UPDATED_AT = CURRENT_TIMESTAMP(),
                UPDATED_BY = CURRENT_USER()
            WHEN NOT MATCHED THEN INSERT (
                BUDGET_NAME, SCOPE_TYPE, SCOPE_VALUE, MONTHLY_LIMIT_CREDITS,
                WARNING_THRESHOLD, CRITICAL_THRESHOLD, ENABLED, UPDATED_AT, UPDATED_BY
            ) VALUES (
                source.BUDGET_NAME, source.SCOPE_TYPE, source.SCOPE_VALUE,
                source.MONTHLY_LIMIT_CREDITS, source.WARNING_THRESHOLD,
                source.CRITICAL_THRESHOLD, TRUE, CURRENT_TIMESTAMP(), CURRENT_USER()
            )
        """
        self._session.sql(
            query,
            params=[
                budget.budget_name,
                budget.scope_type,
                budget.scope_value,
                budget.monthly_limit_credits,
                budget.warning_threshold,
                budget.critical_threshold,
            ],
        ).collect()

    def load_ownership_mappings(self) -> pd.DataFrame:
        query = (
            f"SELECT * FROM {self._ownership_table} "
            "WHERE ENABLED ORDER BY SERVICE_TYPE, WORKLOAD_NAME"
        )
        return normalize_columns(self._session.sql(query).to_pandas())

    @staticmethod
    def _append_in_filter(
        clauses: list[str], params: list[Any], column: str, values: tuple[str, ...]
    ) -> None:
        if not values:
            return
        placeholders = ", ".join("?" for _ in values)
        clauses.append(f"{column} IN ({placeholders})")
        params.extend(values)
