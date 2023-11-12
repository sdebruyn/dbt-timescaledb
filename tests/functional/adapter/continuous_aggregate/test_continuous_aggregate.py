from typing import Any

import pytest

from dbt.tests.util import (
    check_result_nodes_by_name,
    run_dbt,
)


class TestContinuousAggregate:
    @pytest.fixture(scope="class")
    def project_config_update(self) -> dict[str, Any]:
        return {
            "name": "continuous_aggregate_tests",
            "models": {
                "continuous_aggregate_tests": {
                    "base": {"+materialized": "hypertable", "+time_column_name": "time_column"},
                    "test_model": {"+materialized": "continuous_aggregate"},
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

    def test_continuous_aggregate(self, project) -> None:  # noqa: ANN001
        results = run_dbt(["run"])
        assert len(results) == 2  # noqa
        check_result_nodes_by_name(results, ["base", "test_model"])
        nodes = [r.node for r in results]
        test_model = next(n for n in nodes if n.name == "test_model")
        assert test_model.node_info["materialized"] == "continuous_aggregate"
