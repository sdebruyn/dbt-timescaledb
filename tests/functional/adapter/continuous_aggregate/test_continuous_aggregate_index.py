from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import run_dbt


class TestContinuousAggregateIndex:
    def _model_sql(self, create_group_indexes: bool) -> str:
        return f"""
{{{{
  config(
    materialized = "continuous_aggregate",
    create_group_indexes = {create_group_indexes},
    indexes=[
        {{'columns': ['col_1']}}
    ]
  )
}}}}

select
    count(*) as col_1,
    time_bucket(interval '1 day', time_column) as bucket
from {{{{ ref('base') }}}}
group by 2
"""

    @pytest.fixture(scope="class")
    def project_config_update(self) -> dict[str, Any]:
        return {
            "name": "continuous_aggregate_index_tests",
            "models": {
                "continuous_aggregate_index_tests": {
                    "base": {"+materialized": "hypertable", "+main_dimension": "time_column"},
                }
            },
        }

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "base.sql": "select current_timestamp as time_column",
            "with_default.sql": self._model_sql(True),
            "without_default.sql": self._model_sql(False),
        }

    def find_indexes(self, project: TestProjInfo, unique_schema: str) -> list[tuple[str, str, str]]:
        return project.run_sql(
            f"""
select ca.view_name, i.indexname, i.indexdef
from timescaledb_information.continuous_aggregates ca
join pg_indexes i
on i.schemaname = ca.materialization_hypertable_schema
and i.tablename = ca.materialization_hypertable_name
where ca.view_schema = '{unique_schema}'
order by 1, 2""",
            fetch="all",
        )

    def test_continuous_aggregate(self, project: TestProjInfo, unique_schema: str) -> None:
        results = run_dbt(["run"])
        assert len(results) == 3
        indexes = self.find_indexes(project, unique_schema)
        col_1_indexes = [view_name for view_name, _, definition in indexes if definition.endswith("(col_1)")]
        assert sorted(col_1_indexes) == ["with_default", "without_default"]

        # Rebuilding base would drop the continuous aggregates with it
        results = run_dbt(["run", "--exclude", "base"])
        assert len(results) == 2
        assert self.find_indexes(project, unique_schema) == indexes
