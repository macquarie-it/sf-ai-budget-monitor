"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass

from cortex_cost_monitor.config.constants import DEFAULT_CREDIT_PRICE, DEFAULT_CURRENCY


@dataclass(frozen=True)
class AppSettings:
    app_name: str = "Cortex Cost Monitor"
    data_mode: str = "auto"
    currency: str = DEFAULT_CURRENCY
    credit_price: float = DEFAULT_CREDIT_PRICE
    cost_view: str = "CORTEX_COST_MONITOR.V_COST_EVENTS"
    budget_table: str = "CORTEX_COST_MONITOR.BUDGETS"
    ownership_table: str = "CORTEX_COST_MONITOR.OWNERSHIP_MAPPINGS"


def load_settings() -> AppSettings:
    """Load settings without reading or persisting secrets."""

    data_mode = os.getenv("CORTEX_COST_DATA_MODE", "auto").strip().lower()
    if data_mode not in {"auto", "demo", "snowflake"}:
        raise ValueError("CORTEX_COST_DATA_MODE must be auto, demo, or snowflake")

    return AppSettings(
        data_mode=data_mode,
        currency=os.getenv("CORTEX_COST_CURRENCY", DEFAULT_CURRENCY).upper(),
        credit_price=float(os.getenv("CORTEX_CREDIT_PRICE", str(DEFAULT_CREDIT_PRICE))),
        cost_view=os.getenv("CORTEX_COST_VIEW", "CORTEX_COST_MONITOR.V_COST_EVENTS"),
        budget_table=os.getenv("CORTEX_BUDGET_TABLE", "CORTEX_COST_MONITOR.BUDGETS"),
        ownership_table=os.getenv(
            "CORTEX_OWNERSHIP_TABLE", "CORTEX_COST_MONITOR.OWNERSHIP_MAPPINGS"
        ),
    )
