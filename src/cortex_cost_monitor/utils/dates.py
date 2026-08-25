"""Date helpers."""

from __future__ import annotations

from datetime import date, timedelta

from cortex_cost_monitor.config.constants import DEFAULT_LOOKBACK_DAYS


def default_date_range(today: date | None = None) -> tuple[date, date]:
    end_date = today or date.today()
    return end_date - timedelta(days=DEFAULT_LOOKBACK_DAYS - 1), end_date
