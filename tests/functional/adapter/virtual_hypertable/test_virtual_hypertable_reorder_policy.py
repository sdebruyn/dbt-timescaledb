from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import run_dbt
from tests.utils import get_indexes_sql


class TestVirtualHypertableReorderPolicy:
    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "vht.sql": """
{% if var("create_reorder_policy", false) %}
    {{
    config(
        reorder_policy = { "index": { "columns": ["col_1"] } }
    )
    }}
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

    def find_reorder_policy_tables(self, project: TestProjInfo, unique_schema: str) -> list[str]:
        timescale_jobs = project.run_sql(
            f"""
select *
from timescaledb_information.jobs
where application_name like 'Reorder Policy%'
and hypertable_schema = '{unique_schema}'""",
            fetch="all",
        )
        table_names = [job[15] for job in timescale_jobs]
        return table_names

    def test_virtual_hypertable_reorder_policy(self, project: TestProjInfo, unique_schema: str) -> None:
        project.run_sql(f"""
create table {unique_schema}.vht (time_column timestamp, col_1 int);
select create_hypertable('{unique_schema}.vht', by_range('time_column'));""")
        results = run_dbt(["run"])
        assert len(results) == 1
        assert all(result.node.config.materialized == "virtual_hypertable" for result in results)

        assert self.find_reorder_policy_tables(project, unique_schema) == []

        run_enable_results = run_dbt(["run", "--vars", "create_reorder_policy: true"])
        assert len(run_enable_results) == 1
        assert all(result.node.config.materialized == "virtual_hypertable" for result in run_enable_results)

        assert self.find_reorder_policy_tables(project, unique_schema) == ["vht"]

        run_disable_results = run_dbt(["run"])
        assert len(run_disable_results) == 1
        assert all(result.node.config.materialized == "virtual_hypertable" for result in run_disable_results)

        assert self.find_reorder_policy_tables(project, unique_schema) == []


class TestVirtualHypertableReorderPolicyOnConfiguredIndex:
    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "vht.sql": """
{{
config(
    materialized = "virtual_hypertable",
    indexes = [{ "columns": ["col_1"] }],
    reorder_policy = {
        "create_index": true,
        "index": { "columns": ["COL_1"] }
    }
)
}}
--
"""
        }

    def test_virtual_hypertable_reorder_policy(self, project: TestProjInfo, unique_schema: str) -> None:
        project.run_sql(f"""
create table {unique_schema}.vht (time_column timestamp, col_1 int);
select create_hypertable('{unique_schema}.vht', by_range('time_column'));""")
        for _ in range(2):
            results = run_dbt(["run"])
            assert len(results) == 1
            assert len(project.run_sql(get_indexes_sql(unique_schema, "vht"), fetch="all")) == 2


class TestVirtualHypertableReorderPolicyKeepsIndex:
    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "vht.sql": """
{% if var("reorder_column", none) %}
    {{
    config(
        reorder_policy = { "index": { "columns": [var("reorder_column"), "time_column"] } }
    )
    }}
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

    def reorder_index_names(self, project: TestProjInfo, unique_schema: str, column: str) -> list[str]:
        rows = project.run_sql(get_indexes_sql(unique_schema, "vht"), fetch="all")
        return [row[2] for row in rows if f"({column}, time_column)" in row[4]]

    def test_reorder_policy_keeps_index(self, project: TestProjInfo, unique_schema: str) -> None:
        project.run_sql(f"""
create table {unique_schema}.vht (time_column timestamp, col_1 int, col_2 int);
select create_hypertable('{unique_schema}.vht', by_range('time_column'));""")

        run_dbt(["run", "--vars", "reorder_column: col_1"])
        names = self.reorder_index_names(project, unique_schema, "col_1")
        assert len(names) == 1

        run_dbt(["run", "--vars", "reorder_column: col_1"])
        assert self.reorder_index_names(project, unique_schema, "col_1") == names

        run_dbt(["run", "--vars", "reorder_column: col_2"])
        assert self.reorder_index_names(project, unique_schema, "col_1") == []
        assert len(self.reorder_index_names(project, unique_schema, "col_2")) == 1

        run_dbt(["run"])
        assert self.reorder_index_names(project, unique_schema, "col_2") == []
