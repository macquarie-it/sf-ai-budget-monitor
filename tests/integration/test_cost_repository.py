from datetime import date

from cortex_cost_monitor.data.demo_repository import DemoCostRepository
from cortex_cost_monitor.domain.models import CostFilters


def test_demo_repository_honors_service_filter() -> None:
    repository = DemoCostRepository()
    filters = CostFilters(
        start_date=date.today().replace(day=1),
        end_date=date.today(),
        services=("Cortex Agent",),
    )
    events = repository.load_cost_events(filters)
    assert not events.empty
    assert set(events["service_type"]) == {"Cortex Agent"}


def test_demo_repository_budget_round_trip() -> None:
    from cortex_cost_monitor.domain.models import BudgetDefinition

    repository = DemoCostRepository()
    repository.upsert_budget(BudgetDefinition("Test", "Account", "ALL", 50))
    budgets = repository.load_budgets()
    assert "Test" in set(budgets["budget_name"])
