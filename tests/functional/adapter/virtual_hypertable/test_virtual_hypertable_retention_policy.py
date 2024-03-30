from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import run_dbt


class TestVirtualHypertableRetentionPolicy:
    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "vht.sql": """
{% if var("create_retention_policy", false) %}
    {{ config(retention_policy = {"drop_after": "interval '1 day'"}) }}
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

    def find_retention_policy_tables(self, project: TestProjInfo, unique_schema: str) -> list[str]:
        timescale_jobs = project.run_sql(
            f"""
select *
from timescaledb_information.jobs
where proc_name = 'policy_retention'
and hypertable_schema = '{unique_schema}'""",
            fetch="all",
        )
        table_names = [job[15] for job in timescale_jobs]
        return table_names

    def test_virtual_hypertable_retention_policy(self, project: TestProjInfo, unique_schema: str) -> None:
        project.run_sql(f"""
create table {unique_schema}.vht (time_column timestamp, col_1 int);
select create_hypertable('{unique_schema}.vht', by_range('time_column'));""")
        results = run_dbt(["run"])
        assert len(results) == 1
        assert all(result.node.config.materialized == "virtual_hypertable" for result in results)

        assert self.find_retention_policy_tables(project, unique_schema) == []

        run_enable_results = run_dbt(["run", "--vars", "create_retention_policy: true"])
        assert len(run_enable_results) == 1
        assert all(result.node.config.materialized == "virtual_hypertable" for result in run_enable_results)

        assert self.find_retention_policy_tables(project, unique_schema) == ["vht"]

        run_disable_results = run_dbt(["run"])
        assert len(run_disable_results) == 1
        assert all(result.node.config.materialized == "virtual_hypertable" for result in run_disable_results)

        assert self.find_retention_policy_tables(project, unique_schema) == []
