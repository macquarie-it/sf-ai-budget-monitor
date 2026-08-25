from decimal import Decimal

import pytest

from cortex_cost_monitor.domain.cost_rules import (
    attribution_coverage,
    credits_to_currency,
    direct_ai_credits,
    total_credits,
)


def test_total_credits_adds_distinct_components() -> None:
    assert total_credits(2.0, 0.5, 1.25) == 3.75


def test_total_credits_treats_missing_values_as_zero() -> None:
    assert total_credits(2.0, None, None) == 2.0
    assert direct_ai_credits(None, 0.5) == 0.5


def test_currency_conversion_uses_decimal_rounding() -> None:
    assert credits_to_currency(1.005, 3.0) == Decimal("3.02")


def test_currency_conversion_rejects_negative_values() -> None:
    with pytest.raises(ValueError):
        credits_to_currency(-1, 3)


def test_attribution_coverage_is_bounded() -> None:
    assert attribution_coverage(7.5, 10) == 0.75
    assert attribution_coverage(12, 10) == 1.0
    assert attribution_coverage(0, 0) == 1.0
