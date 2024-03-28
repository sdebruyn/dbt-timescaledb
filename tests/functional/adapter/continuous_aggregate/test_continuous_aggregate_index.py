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

    def test_continuous_aggregate(self, project: TestProjInfo) -> None:
        results = run_dbt(["run"])
        assert len(results) == 3
