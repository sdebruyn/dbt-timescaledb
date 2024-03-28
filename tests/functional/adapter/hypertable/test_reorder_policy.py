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
        results = run_dbt(["run"])
        assert len(results) == 2

        create_index_results = project.run_sql(get_indexes_sql(unique_schema, "create_index"), fetch="all")
        sep_index_results = project.run_sql(get_indexes_sql(unique_schema, "sep_index"), fetch="all")

        assert len(create_index_results) == 2, "Expected 2 indexes when index should be created"
        assert len(sep_index_results) == 1, "Expected 1 index on separate index creation"

        timescale_jobs = project.run_sql(
            f"""
select *
from timescaledb_information.jobs
where application_name like 'Reorder Policy%'
and hypertable_schema = '{unique_schema}'""",
            fetch="all",
        )
        assert len(timescale_jobs) == 2
        table_names = [job[15] for job in timescale_jobs]
        assert set(table_names) == {"create_index", "sep_index"}
