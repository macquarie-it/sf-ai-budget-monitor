"""Stable labels shared across the application."""

SERVICE_AGENT = "Cortex Agent"
SERVICE_ANALYST = "Cortex Analyst"
SERVICE_TYPES = (SERVICE_AGENT, SERVICE_ANALYST)

ATTRIBUTION_COMPLETE = "Complete"
ATTRIBUTION_PARTIAL = "Partial"
ATTRIBUTION_UNATTRIBUTED = "Unattributed"
ATTRIBUTION_EXCLUDED = "Excluded"
ATTRIBUTION_STATUSES = (
    ATTRIBUTION_COMPLETE,
    ATTRIBUTION_PARTIAL,
    ATTRIBUTION_UNATTRIBUTED,
    ATTRIBUTION_EXCLUDED,
)

DEFAULT_CURRENCY = "USD"
DEFAULT_CREDIT_PRICE = 3.0
DEFAULT_LOOKBACK_DAYS = 30
MAX_LOOKBACK_DAYS = 365

COST_EVENT_COLUMNS = (
    "event_time",
    "service_type",
    "workload_name",
    "user_name",
    "role_name",
    "team",
    "cost_center",
    "environment",
    "warehouse_name",
    "request_id",
    "query_id",
    "token_credits",
    "ai_function_credits",
    "direct_ai_credits",
    "compute_credits",
    "total_credits",
    "tokens",
    "request_count",
    "outcome",
    "attribution_status",
)
