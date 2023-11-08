import os

import pytest

pytest_plugins = ["dbt.tests.fixtures.project"]


@pytest.fixture(scope="class")
def dbt_profile_target():
    return {
        "type": "timescaledb",
        "host": os.getenv("POSTGRES_TEST_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_TEST_PORT", "5432")),
        "user": os.getenv("POSTGRES_TEST_USER", "timescaledb"),
        "pass": os.getenv("POSTGRES_TEST_PASS", "timescaledb"),
        "dbname": os.getenv("POSTGRES_TEST_DATABASE", "timescaledb"),
    }
