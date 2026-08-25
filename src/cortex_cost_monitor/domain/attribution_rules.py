"""Rules for classifying cost attribution quality."""

from __future__ import annotations

from cortex_cost_monitor.config.constants import (
    ATTRIBUTION_COMPLETE,
    ATTRIBUTION_PARTIAL,
    ATTRIBUTION_UNATTRIBUTED,
)


def classify_attribution(
    *, workload_name: str | None, user_name: str | None, compute_credits: float | None
) -> str:
    """Classify whether an event has enough ownership and compute context."""

    if not workload_name and not user_name:
        return ATTRIBUTION_UNATTRIBUTED
    if compute_credits is None:
        return ATTRIBUTION_PARTIAL
    return ATTRIBUTION_COMPLETE
