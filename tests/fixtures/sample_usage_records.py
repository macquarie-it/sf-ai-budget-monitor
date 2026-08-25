"""Small deterministic event dataset for service tests."""

from __future__ import annotations

import pandas as pd


def sample_events() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "event_time": pd.Timestamp("2026-08-01T01:00:00Z"),
                "service_type": "Cortex Agent",
                "workload_name": "FINANCE_AGENT",
                "user_name": "ALICE",
                "role_name": "ANALYST",
                "team": "Finance",
                "cost_center": "CC-100",
                "environment": "Production",
                "warehouse_name": "AI_QUERY_XS",
                "request_id": "req-1",
                "query_id": "query-1",
                "token_credits": 2.0,
                "ai_function_credits": 0.5,
                "direct_ai_credits": 2.5,
                "compute_credits": 1.0,
                "total_credits": 3.5,
                "tokens": 1200,
                "request_count": 1,
                "outcome": "Succeeded",
                "attribution_status": "Complete",
            },
            {
                "event_time": pd.Timestamp("2026-08-02T01:00:00Z"),
                "service_type": "Cortex Analyst",
                "workload_name": "Standalone Cortex Analyst",
                "user_name": "BEN",
                "role_name": "Unassigned",
                "team": "Revenue",
                "cost_center": "CC-120",
                "environment": "Production",
                "warehouse_name": "",
                "request_id": "analyst-hour-1",
                "query_id": "",
                "token_credits": 4.0,
                "ai_function_credits": 0.0,
                "direct_ai_credits": 4.0,
                "compute_credits": 0.0,
                "total_credits": 4.0,
                "tokens": 0,
                "request_count": 5,
                "outcome": "Succeeded",
                "attribution_status": "Partial",
            },
        ]
    )
