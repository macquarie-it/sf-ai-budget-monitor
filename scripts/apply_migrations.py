"""Apply ordered, idempotent Snowflake SQL migrations with Snowflake CLI."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def migration_files(directory: Path) -> list[Path]:
    files = sorted(directory.glob("*.sql"))
    if not files:
        raise FileNotFoundError(f"No SQL migrations found in {directory}")
    return files


def apply_migrations(connection: str, directory: Path) -> None:
    for migration in migration_files(directory):
        print(f"Applying {migration.name}...")
        subprocess.run(
            [
                "snow",
                "sql",
                "--connection",
                connection,
                "--filename",
                str(migration),
            ],
            cwd=PROJECT_ROOT,
            check=True,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--connection", required=True, help="Snowflake CLI connection name")
    parser.add_argument(
        "--directory",
        type=Path,
        default=PROJECT_ROOT / "sql" / "migrations",
        help="Directory containing ordered .sql migrations",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    apply_migrations(arguments.connection, arguments.directory.resolve())
