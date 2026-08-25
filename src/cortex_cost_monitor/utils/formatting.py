"""Display formatting helpers."""

from __future__ import annotations

from cortex_cost_monitor.domain.cost_rules import credits_to_currency


def format_credits(value: float) -> str:
    return f"{value:,.2f} cr"


def format_money(value: float, currency: str) -> str:
    return f"{currency} {value:,.2f}"


def format_cost(value: float, credit_price: float, currency: str, show_currency: bool) -> str:
    if show_currency:
        return format_money(float(credits_to_currency(value, credit_price)), currency)
    return format_credits(value)
