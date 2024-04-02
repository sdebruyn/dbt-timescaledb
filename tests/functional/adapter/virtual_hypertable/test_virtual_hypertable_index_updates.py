from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import run_dbt


class TestVirtualHypertableIndexUpdates:
    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "vht.sql": """
{% if var("add_index", false) %}
    {{ config(indexes=[{'columns': ['col_1']}]) }}
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

    def find_indexes(self, project: TestProjInfo, unique_schema: str) -> list[str]:
        indexes = project.run_sql(
            f"""
select *
from pg_indexes
where tablename = 'vht'
and schemaname = '{unique_schema}'""",
            fetch="all",
        )
        index_names = [job[2] for job in indexes]
        return index_names

    def test_virtual_hypertable_index_updates(self, project: TestProjInfo, unique_schema: str) -> None:
        project.run_sql(f"""
create table {unique_schema}.vht (time_column timestamp, col_1 int);
select create_hypertable('{unique_schema}.vht', by_range('time_column'));""")
        results = run_dbt(["run"])
        assert len(results) == 1
        assert len(self.find_indexes(project, unique_schema)) == 1

        run_enable_results = run_dbt(["run", "--vars", "add_index: true"])
        assert len(run_enable_results) == 1
        assert len(self.find_indexes(project, unique_schema)) == 2

        run_disable_results = run_dbt(["run"])
        assert len(run_disable_results) == 1
        assert len(self.find_indexes(project, unique_schema)) == 1

        run_enable_results = run_dbt(["run", "--vars", "add_index: true"])
        assert len(run_enable_results) == 1
        assert len(self.find_indexes(project, unique_schema)) == 2

        run_disable_results = run_dbt(["run"])
        assert len(run_disable_results) == 1
        assert len(self.find_indexes(project, unique_schema)) == 1
