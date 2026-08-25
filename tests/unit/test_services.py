import pandas as pd
from tests.fixtures.sample_usage_records import sample_events

from cortex_cost_monitor.services.attribution_service import coverage_trend
from cortex_cost_monitor.services.audit_service import search_events
from cortex_cost_monitor.services.overview_service import summarize


def test_summary_separates_direct_and_compute_cost() -> None:
    summary = summarize(sample_events())
    assert summary.direct_ai_credits == 6.5
    assert summary.compute_credits == 1.0
    assert summary.total_credits == 7.5
    assert summary.request_count == 6


def test_search_is_case_insensitive_and_literal() -> None:
    result = search_events(sample_events(), "finance_agent")
    assert len(result) == 1
    assert result.iloc[0]["request_id"] == "req-1"


def test_coverage_trend_returns_bounded_ratios() -> None:
    result = coverage_trend(sample_events())
    assert isinstance(result, pd.DataFrame)
    assert result["coverage"].between(0, 1).all()
