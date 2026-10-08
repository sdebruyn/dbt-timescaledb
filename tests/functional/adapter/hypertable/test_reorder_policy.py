from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import run_dbt
from tests.utils import get_indexes_sql


class TestHypertableReorderPolicy:
    def _model_sql(self, create_index: bool) -> str:
        return f"""
{{{{
  config(
    materialized = "hypertable",
    main_dimension = "time_column",
    create_default_indexes = False,
    indexes = [{{
        "columns": ["time_column", "col_1"]
    }}],
    reorder_policy = {{
      "create_index": {create_index},
      "index": {{ "columns": ["col_1"] if {create_index} else ["time_column", "col_1"] }}
    }},
  )
}}}}

select
    current_timestamp as time_column,
    1 as col_1
"""

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "create_index.sql": self._model_sql(True),
            "sep_index.sql": self._model_sql(False),
        }

    def test_reorder_policy(self, project: TestProjInfo, unique_schema: str) -> None:
        for _ in range(2):
            results = run_dbt(["run"])
            assert len(results) == 2

            create_index_results = project.run_sql(
                get_indexes_sql(unique_schema, "create_index"), fetch="all"
            )
            sep_index_results = project.run_sql(get_indexes_sql(unique_schema, "sep_index"), fetch="all")

            assert len(create_index_results) == 2, "Expected 2 indexes when index should be created"
            assert len(sep_index_results) == 1, "Expected 1 index on separate index creation"

            timescale_jobs = project.run_sql(
                f"""
select hypertable_name, config->>'index_name'
from timescaledb_information.jobs
where application_name like 'Reorder Policy%'
and hypertable_schema = '{unique_schema}'""",
                fetch="all",
            )
            assert len(timescale_jobs) == 2
            assert {table_name for table_name, _ in timescale_jobs} == {"create_index", "sep_index"}
            for table_name, index_name in timescale_jobs:
                assert project.run_sql(
                    f"{get_indexes_sql(unique_schema, table_name)} and indexname = '{index_name}'",
                    fetch="one",
                ), f"Reorder index {index_name} not found on {table_name}"


class TestHypertableReorderPolicyIndexLookup:
    def _model_sql(self, create_index: bool, column: str) -> str:
        return f"""
{{{{
  config(
    materialized = "hypertable",
    main_dimension = "time_column",
    create_default_indexes = False,
    reorder_policy = {{
      "create_index": {create_index},
      "index": {{ "columns": ["{column}"] }}
    }},
  )
}}}}

select
    current_timestamp as time_column,
    1 as col_1
"""

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "upper_case.sql": self._model_sql(True, "COL_1"),
            "missing_index.sql": self._model_sql(False, "col_1"),
        }

    def test_reorder_policy(self, project: TestProjInfo, unique_schema: str) -> None:
        for _ in range(2):
            results = {result.node.name: result for result in run_dbt(["run"], expect_pass=False)}
            assert str(results["upper_case"].status) == "success"
            assert str(results["missing_index"].status) == "error"
            assert "no index on (col_1)" in results["missing_index"].message

            timescale_jobs = project.run_sql(
                f"""
select hypertable_name, config->>'index_name'
from timescaledb_information.jobs
where application_name like 'Reorder Policy%'
and hypertable_schema = '{unique_schema}'""",
                fetch="all",
            )
            assert len(timescale_jobs) == 1
            table_name, index_name = timescale_jobs[0]
            assert table_name == "upper_case"
            assert project.run_sql(
                f"{get_indexes_sql(unique_schema, table_name)} and indexname = '{index_name}'",
                fetch="one",
            )
