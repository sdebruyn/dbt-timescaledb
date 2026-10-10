from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import run_dbt
from tests.utils import get_jobs_sql


class TestVirtualHypertableCompression:
    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "vht.sql": """
{% if var("enable_compression", false) %}
    {{ config(compression={"after": "interval '1 day'"}) }}
{% endif %}
--
"""
        }

    @pytest.fixture(scope="class")
    def project_config_update(self) -> dict[str, Any]:
        return {
            "name": "virtual_hypertable_tests",
            "models": {"virtual_hypertable_tests": {"vht": {"+materialized": "virtual_hypertable"}}},
        }

    def compression_enabled(self, project: TestProjInfo, unique_schema: str) -> bool:
        return project.run_sql(
            f"""
select compression_enabled
from timescaledb_information.hypertables
where hypertable_name = 'vht'
and hypertable_schema = '{unique_schema}'""",
            fetch="one",
        )[0]

    def count_compression_jobs(self, project: TestProjInfo, unique_schema: str) -> int:
        return len(project.run_sql(get_jobs_sql(unique_schema, "vht", "policy_compression"), fetch="all"))

    def test_virtual_hypertable_compression(self, project: TestProjInfo, unique_schema: str) -> None:
        project.run_sql(f"""
create table {unique_schema}.vht (time_column timestamp, col_1 int);
select create_hypertable('{unique_schema}.vht', by_range('time_column'));""")
        results = run_dbt(["run"])
        assert len(results) == 1

        assert not self.compression_enabled(project, unique_schema)
        assert self.count_compression_jobs(project, unique_schema) == 0

        run_enable_results = run_dbt(["run", "--vars", "enable_compression: true"])
        assert len(run_enable_results) == 1

        assert self.compression_enabled(project, unique_schema)
        assert self.count_compression_jobs(project, unique_schema) == 1

        run_disable_results = run_dbt(["run"])
        assert len(run_disable_results) == 1

        assert not self.compression_enabled(project, unique_schema)
        assert self.count_compression_jobs(project, unique_schema) == 0
