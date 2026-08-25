"""Resolve a Snowpark session in deployed and local environments."""

from __future__ import annotations

from typing import Any


def try_get_session() -> tuple[Any | None, str | None]:
    """Return the active Snowpark session or a diagnostic message."""

    try:
        from snowflake.snowpark.context import get_active_session

        session = get_active_session()
        if session is not None:
            return session, None
    except Exception as exc:  # Snowflake raises when no deployed session exists.
        active_session_error = str(exc)
    else:
        active_session_error = "No active Snowpark session was found."

    try:
        import streamlit as st

        return st.connection("snowflake").session(), None
    except Exception as exc:
        return None, f"{active_session_error} Local connection failed: {exc}"
