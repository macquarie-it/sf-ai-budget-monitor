"""Cost composition and monetary conversion rules."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def total_credits(
    token_credits: float | None,
    ai_function_credits: float | None,
    compute_credits: float | None,
) -> float:
    """Add distinct cost components while treating unavailable values as zero."""

    return sum(
        float(value or 0.0) for value in (token_credits, ai_function_credits, compute_credits)
    )


def direct_ai_credits(token_credits: float | None, ai_function_credits: float | None) -> float:
    """Return the direct AI portion of a request."""

    return float(token_credits or 0.0) + float(ai_function_credits or 0.0)


def credits_to_currency(credits: float, price_per_credit: float) -> Decimal:
    """Convert credits using the configured contract estimate."""

    if credits < 0 or price_per_credit < 0:
        raise ValueError("credits and price_per_credit must be non-negative")
    value = Decimal(str(credits)) * Decimal(str(price_per_credit))
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def attribution_coverage(attributed_credits: float, total_cost_credits: float) -> float:
    """Return a bounded coverage ratio."""

    if total_cost_credits <= 0:
        return 1.0
    return max(0.0, min(1.0, attributed_credits / total_cost_credits))
