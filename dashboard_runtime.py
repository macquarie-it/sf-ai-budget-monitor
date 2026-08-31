"""Read the DBA-owned SQL registry and build data for the React dashboard."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import re
from typing import Any


SINGLE_RESULT_COMPONENTS = {
    "dashboard_shell",
    "monitoring_status",
    "credits_consumed",
    "projected_month",
    "active_identities",
    "dashboard_footer",
}

EXPECTED_RENDERERS = {
    "dashboard_shell": "shell",
    "monitoring_status": "status",
    "credits_consumed": "metric",
    "projected_month": "metric",
    "active_identities": "metric",
    "chart_menu": "radio_group",
    "agent_bar_chart": "bar_chart",
    "credit_burn": "line_chart",
    "usage_scatter": "scatter_plot",
    "service_pie_chart": "pie_chart",
    "activity_heatmap": "heatmap",
    "dashboard_footer": "footer",
}

REQUIRED_FIELDS = {
    "dashboard_shell": {"brandTitle", "brandSubtitle", "environmentLabel", "accountName", "pageOverline", "titleLine1", "titleEmphasis", "lede"},
    "monitoring_status": {"message"},
    "credits_consumed": {"eyebrow", "value", "suffix", "trend", "note", "tone"},
    "projected_month": {"eyebrow", "value", "suffix", "trend", "note", "tone"},
    "active_identities": {"eyebrow", "value", "suffix", "trend", "note", "tone"},
    "chart_menu": {"chartId", "label", "description", "displayOrder"},
    "agent_bar_chart": {"label", "sublabel", "value", "changePercent", "kicker", "title", "description"},
    "credit_burn": {"rangeLabel", "position", "value", "kicker", "title", "description"},
    "usage_scatter": {"label", "xValue", "yValue", "size", "color", "kicker", "title", "description"},
    "service_pie_chart": {"label", "value", "credits", "color", "kicker", "title", "description"},
    "activity_heatmap": {"rowLabel", "columnLabel", "value", "kicker", "title", "description"},
    "dashboard_footer": {"leftText", "rightText"},
}


def parse_dashboard_sql(config_path: Path) -> list[dict[str, str]]:
    """Split dashboard.sql into independently executable component queries."""

    components: list[dict[str, str]] = []
    current: dict[str, Any] | None = None

    for line_number, line in enumerate(config_path.read_text(encoding="utf-8").splitlines(), 1):
        component_match = re.match(
            r"^\s*--\s*@component\s+([a-z][a-z0-9_]*)\s*$", line, re.IGNORECASE
        )
        if component_match:
            if current:
                raise ValueError(f"A new component starts before {current['id']} ends (line {line_number}).")
            current = {"id": component_match.group(1).lower(), "renderer": "", "sql_lines": []}
            continue

        if current is None:
            continue

        if re.match(r"^\s*--\s*@end-component\s*$", line, re.IGNORECASE):
            sql = "\n".join(current.pop("sql_lines")).strip()
            if not sql:
                raise ValueError(f"{current['id']} does not contain a SQL query.")
            current["sql"] = sql
            components.append(current)
            current = None
            continue

        renderer_match = re.match(
            r"^\s*--\s*@renderer\s+([a-z][a-z0-9_]*)\s*$", line, re.IGNORECASE
        )
        if renderer_match:
            current["renderer"] = renderer_match.group(1).lower()
        current["sql_lines"].append(line)

    if current:
        raise ValueError(f"{current['id']} is missing its @end-component line.")
    if not components:
        raise ValueError("No dashboard components were found in dashboard.sql.")

    component_ids = [component["id"] for component in components]
    duplicate_ids = {component_id for component_id in component_ids if component_ids.count(component_id) > 1}
    if duplicate_ids:
        raise ValueError(f"Duplicate dashboard components: {', '.join(sorted(duplicate_ids))}")

    missing_components = set(EXPECTED_RENDERERS) - set(component_ids)
    if missing_components:
        raise ValueError(f"dashboard.sql is missing: {', '.join(sorted(missing_components))}")
    unknown_components = set(component_ids) - set(EXPECTED_RENDERERS)
    if unknown_components:
        raise ValueError(f"dashboard.sql contains unsupported components: {', '.join(sorted(unknown_components))}")
    for component in components:
        expected_renderer = EXPECTED_RENDERERS[component["id"]]
        if component["renderer"] != expected_renderer:
            raise ValueError(
                f"Keep the renderer for '{component['id']}' as '@renderer {expected_renderer}'."
            )
    return components


def execute_dashboard_sql(session: Any, config_path: Path) -> dict[str, Any]:
    """Execute every component query with the active Snowflake session."""

    result: dict[str, Any] = {
        "version": 1,
        "generatedAt": datetime.now().astimezone().isoformat(),
        "components": {},
    }

    for component in parse_dashboard_sql(config_path):
        try:
            snowflake_rows = session.sql(component["sql"]).collect()
        except Exception as error:
            raise RuntimeError(
                f"The SQL for '{component['id']}' could not run. "
                "Open config/dashboard.sql and check that component's SELECT statement."
            ) from error

        rows = [_normalise_row(row.as_dict()) for row in snowflake_rows]
        component_id = component["id"]
        for row_number, row in enumerate(rows, 1):
            missing_fields = REQUIRED_FIELDS[component_id] - set(row)
            if missing_fields:
                readable_fields = ", ".join(sorted(missing_fields))
                raise ValueError(
                    f"The SQL for '{component_id}' is missing these output columns: {readable_fields}. "
                    "Copy the column names from its EXAMPLE RESULT in config/dashboard.sql."
                )
        if component_id in SINGLE_RESULT_COMPONENTS:
            if len(rows) != 1:
                raise ValueError(
                    f"'{component_id}' is a summary component. Its SQL returned {len(rows)} results. "
                    "Use SUM(), COUNT(), MAX(), or another summary calculation so it returns one result."
                )
            data: Any = rows[0]
        else:
            if not rows:
                raise ValueError(f"'{component_id}' has nothing to display because its SQL returned no data.")
            data = rows

        result["components"][component_id] = {
            "renderer": component["renderer"],
            "data": data,
        }

    return result


def _normalise_row(row: dict[str, Any]) -> dict[str, Any]:
    return {_camel_case(key): _json_value(value) for key, value in row.items()}


def _camel_case(value: str) -> str:
    words = value.lower().split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value
