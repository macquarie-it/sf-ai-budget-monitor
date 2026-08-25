"""Typed domain models shared by services and repositories."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CostFilters:
    start_date: date
    end_date: date
    services: tuple[str, ...] = ()
    teams: tuple[str, ...] = ()
    environments: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")


@dataclass(frozen=True)
class CostSummary:
    direct_ai_credits: float
    compute_credits: float
    total_credits: float
    request_count: int
    attribution_coverage: float

    @property
    def average_credits_per_request(self) -> float:
        if self.request_count <= 0:
            return 0.0
        return self.total_credits / self.request_count


@dataclass(frozen=True)
class BudgetDefinition:
    budget_name: str
    scope_type: str
    scope_value: str
    monthly_limit_credits: float
    warning_threshold: float = 0.7
    critical_threshold: float = 0.9

    def __post_init__(self) -> None:
        if self.monthly_limit_credits <= 0:
            raise ValueError("monthly_limit_credits must be positive")
        if not 0 < self.warning_threshold < self.critical_threshold <= 1:
            raise ValueError("budget thresholds must satisfy 0 < warning < critical <= 1")
