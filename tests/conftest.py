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
        "user": os.getenv("POSTGRES_USER", "timescaledb"),
        "pass": os.getenv("POSTGRES_PASSWORD", "timescaledb"),
        "dbname": os.getenv("POSTGRES_DB", "timescaledb"),
    }


@pytest.fixture(scope="class")
def unique_schema(unique_schema: str) -> str:
    # The schema name must be less than 64 characters long
    return unique_schema[:63]


# dbt-tests-adapter writes project files via project_root.mkdir(), which fails when the
# fixture chain is re-executed for another parametrized variant on the same project_root.
# Depending on project_config_update gives each variant its own project directory.
@pytest.fixture(scope="class")
def project_root(tmpdir_factory: Any, project_config_update: Any) -> Any:
    return tmpdir_factory.mktemp("project")
