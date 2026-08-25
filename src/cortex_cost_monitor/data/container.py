"""Application dependency assembly."""

from __future__ import annotations

from dataclasses import dataclass

from cortex_cost_monitor.config.settings import AppSettings, load_settings
from cortex_cost_monitor.data.cost_repository import SnowflakeCostRepository
from cortex_cost_monitor.data.demo_repository import DemoCostRepository
from cortex_cost_monitor.data.repositories import CostRepository
from cortex_cost_monitor.data.session import try_get_session


@dataclass(frozen=True)
class AppContext:
    settings: AppSettings
    repository: CostRepository
    data_mode: str
    diagnostic: str | None = None


def build_app_context() -> AppContext:
    settings = load_settings()
    if settings.data_mode == "demo":
        return AppContext(settings, DemoCostRepository(), "demo")

    session, diagnostic = try_get_session()
    if session is not None:
        repository = SnowflakeCostRepository(
            session,
            cost_view=settings.cost_view,
            budget_table=settings.budget_table,
            ownership_table=settings.ownership_table,
        )
        return AppContext(settings, repository, "snowflake")

    if settings.data_mode == "snowflake":
        raise RuntimeError(
            f"Snowflake mode was requested but no session is available. {diagnostic}"
        )

    return AppContext(settings, DemoCostRepository(), "demo", diagnostic)
