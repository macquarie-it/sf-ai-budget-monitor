"""Offline verification for the deployed dashboard SQL runtime."""

import json
from pathlib import Path
import re
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dashboard_runtime import execute_dashboard_sql, parse_dashboard_sql  # noqa: E402


class FakeRow:
    def __init__(self, data):
        self.data = data

    def as_dict(self):
        return {_upper_snake(key): value for key, value in self.data.items()}


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows

    def collect(self):
        return [FakeRow(row) for row in self.rows]


class FakeSession:
    def __init__(self, data_by_component, component_order):
        self.data_by_component = data_by_component
        self.component_order = component_order
        self.index = 0

    def sql(self, _query):
        component_id = self.component_order[self.index]
        self.index += 1
        component_data = self.data_by_component[component_id]["data"]
        rows = component_data if isinstance(component_data, list) else [component_data]
        return FakeQuery(rows)


class DashboardRuntimeTest(unittest.TestCase):
    def test_deployed_runtime_builds_the_same_component_data(self):
        config_path = PROJECT_ROOT / "config" / "dashboard.sql"
        generated_path = PROJECT_ROOT / "src" / "generated" / "dashboard-data.json"
        expected = json.loads(generated_path.read_text(encoding="utf-8"))
        parsed = parse_dashboard_sql(config_path)
        component_order = [component["id"] for component in parsed]
        session = FakeSession(expected["components"], component_order)

        actual = execute_dashboard_sql(session, config_path)

        self.assertEqual(actual["components"], expected["components"])
        self.assertEqual(session.index, len(component_order))


def _upper_snake(value):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).upper()


if __name__ == "__main__":
    unittest.main()
