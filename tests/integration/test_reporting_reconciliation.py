from datetime import date, timedelta

from cortex_cost_monitor.data.demo_repository import DemoCostRepository
from cortex_cost_monitor.domain.models import CostFilters
from cortex_cost_monitor.services.overview_service import daily_cost, summarize


def test_daily_totals_reconcile_to_event_summary() -> None:
    repository = DemoCostRepository()
    filters = CostFilters(date.today() - timedelta(days=29), date.today())
    events = repository.load_cost_events(filters)
    daily = daily_cost(events)
    summary = summarize(events)
    assert abs(float(daily["total_credits"].sum()) - summary.total_credits) < 0.000001
