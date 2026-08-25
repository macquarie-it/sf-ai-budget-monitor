"""Reconcile daily summaries with the request-level cost contract."""

from __future__ import annotations

import argparse
import subprocess

RECONCILIATION_SQL = """
WITH DETAIL AS (
    SELECT DATE_TRUNC('DAY', EVENT_TIME) AS USAGE_DATE, SUM(TOTAL_CREDITS) AS CREDITS
    FROM V_COST_EVENTS
    WHERE EVENT_TIME >= DATEADD('DAY', -30, CURRENT_TIMESTAMP())
    GROUP BY 1
),
SUMMARY AS (
    SELECT USAGE_DATE, SUM(TOTAL_CREDITS) AS CREDITS
    FROM V_DAILY_COST
    WHERE USAGE_DATE >= DATEADD('DAY', -30, CURRENT_DATE())
    GROUP BY 1
)
SELECT
    COALESCE(D.USAGE_DATE, S.USAGE_DATE) AS USAGE_DATE,
    COALESCE(D.CREDITS, 0) AS DETAIL_CREDITS,
    COALESCE(S.CREDITS, 0) AS SUMMARY_CREDITS,
    ABS(COALESCE(D.CREDITS, 0) - COALESCE(S.CREDITS, 0)) AS DIFFERENCE
FROM DETAIL D
FULL OUTER JOIN SUMMARY S USING (USAGE_DATE)
WHERE DIFFERENCE > 0.000001
ORDER BY USAGE_DATE;
"""


def run(connection: str) -> None:
    subprocess.run(
        ["snow", "sql", "--connection", connection, "--query", RECONCILIATION_SQL],
        check=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--connection", required=True)
    run(parser.parse_args().connection)
