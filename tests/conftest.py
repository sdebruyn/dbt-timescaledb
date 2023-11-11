import os
from typing import Any

import pytest

pytest_plugins: list[str] = ["dbt.tests.fixtures.project"]


@pytest.fixture(scope="class")
def dbt_profile_target() -> dict[str, Any]:
    return {
        "type": "timescaledb",
        "host": os.getenv("TIMESCALEDB_TEST_HOST", "localhost"),
        "port": int(os.getenv("TIMESCALEDB_TEST_PORT", "5432")),
        "user": os.getenv("TIMESCALEDB_TEST_USER", "timescaledb"),
        "pass": os.getenv("TIMESCALEDB_TEST_PASS", "timescaledb"),
        "dbname": os.getenv("TIMESCALEDB_TEST_DATABASE", "timescaledb"),
    }
