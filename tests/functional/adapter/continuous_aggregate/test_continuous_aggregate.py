from typing import Any

import pytest

from dbt.tests.util import (
    check_result_nodes_by_name,
    run_dbt,
)


class TestContinuousAggregate:
    @pytest.fixture(
        scope="class",
        params=[
            pytest.param({"+refresh_now": False}, id="refresh_now_false"),
            pytest.param({"+refresh_now": True}, id="refresh_now_true"),
            pytest.param({"materialized_only": False}, id="materialized_only_false"),
            pytest.param({"materialized_only": True}, id="materialized_only_true"),
        ],
    )
    def project_config_update(self, request) -> dict[str, Any]:  # noqa: ANN001
        return {
            "name": "continuous_aggregate_tests",
            "models": {
                "continuous_aggregate_tests": {
                    "base": {"+materialized": "hypertable", "+time_column_name": "time_column"},
                    "test_model": {"+materialized": "continuous_aggregate"} | request.param,
                }
            },
        }

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "base.sql": "select current_timestamp as time_column",
            "test_model.sql": """
select
    count(*),
    time_bucket(interval '1 day', time_column) as bucket
from {{ ref('base') }}
group by 2
""",
        }

    def test_continuous_aggregate(self, project, unique_schema: str) -> None:  # noqa: ANN001
        results = run_dbt(["run"])
        assert len(results) == 2  # noqa
        check_result_nodes_by_name(results, ["base", "test_model"])
        nodes = [r.node for r in results]
        test_model = next(n for n in nodes if n.name == "test_model")
        assert test_model.node_info["materialized"] == "continuous_aggregate"

        continuous_aggregate_results = project.run_sql(
            f"""
select *
from timescaledb_information.continuous_aggregates
where view_schema = '{unique_schema}'
and view_name = 'test_model'""",
            fetch="all",
        )
        assert len(continuous_aggregate_results) == 1
