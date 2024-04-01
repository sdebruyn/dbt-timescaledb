from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import run_dbt


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

    def count_compression_settings(self, project: TestProjInfo, unique_schema: str) -> int:
        compression_settings = project.run_sql(
            f"""
select *
from timescaledb_information.compression_settings
where hypertable_name = 'vht'
and hypertable_schema = '{unique_schema}'""",
            fetch="all",
        )
        return len(compression_settings)

    def test_virtual_hypertable_compression(self, project: TestProjInfo, unique_schema: str) -> None:
        project.run_sql(f"""
create table {unique_schema}.vht (time_column timestamp, col_1 int);
select create_hypertable('{unique_schema}.vht', by_range('time_column'));""")
        results = run_dbt(["run"])
        assert len(results) == 1

        assert self.count_compression_settings(project, unique_schema) == 0

        run_enable_results = run_dbt(["run", "--vars", "enable_compression: true"])
        assert len(run_enable_results) == 1

        assert self.count_compression_settings(project, unique_schema) == 1

        run_disable_results = run_dbt(["run"])
        assert len(run_disable_results) == 1

        assert self.count_compression_settings(project, unique_schema) == 0
