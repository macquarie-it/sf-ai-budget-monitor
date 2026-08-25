"""Run lightweight post-deployment checks through Snowflake CLI."""

from __future__ import annotations

import argparse
import subprocess


def run(connection: str, entity: str) -> None:
    subprocess.run(["snow", "streamlit", "get-url", entity, "--connection", connection], check=True)
    subprocess.run(
        [
            "snow",
            "sql",
            "--connection",
            connection,
            "--query",
            "SELECT COUNT(*) AS EVENT_COUNT, MAX(EVENT_TIME) AS LATEST_EVENT FROM V_COST_EVENTS",
        ],
        check=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--connection", required=True)
    parser.add_argument("--entity", default="cortex_cost_monitor")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run(arguments.connection, arguments.entity)
