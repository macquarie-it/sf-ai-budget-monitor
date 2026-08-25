import pytest

from cortex_cost_monitor.domain.budget_rules import calculate_budget_status
from cortex_cost_monitor.domain.models import BudgetDefinition


@pytest.mark.parametrize(
    ("spent", "expected"),
    [(50, "On track"), (75, "Warning"), (95, "Critical"), (100, "Exceeded")],
)
def test_budget_states(spent: float, expected: str) -> None:
    assert calculate_budget_status(spent, 100).state == expected


def test_budget_remaining_never_becomes_negative() -> None:
    assert calculate_budget_status(120, 100).remaining_credits == 0


def test_budget_definition_validates_threshold_order() -> None:
    with pytest.raises(ValueError):
        BudgetDefinition("Bad", "Account", "ALL", 100, 0.9, 0.8)
