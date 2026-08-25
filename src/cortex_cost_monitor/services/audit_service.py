"""Audit detail filtering and export preparation."""

from __future__ import annotations

import pandas as pd


def search_events(events: pd.DataFrame, search_term: str) -> pd.DataFrame:
    term = search_term.strip()
    if not term or events.empty:
        return events
    searchable = [
        "request_id",
        "query_id",
        "user_name",
        "workload_name",
        "team",
        "warehouse_name",
    ]
    mask = pd.Series(False, index=events.index)
    for column in searchable:
        mask |= events[column].astype(str).str.contains(term, case=False, na=False, regex=False)
    return events.loc[mask]


def csv_bytes(events: pd.DataFrame) -> bytes:
    return events.to_csv(index=False).encode("utf-8")
