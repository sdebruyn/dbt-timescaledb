import pytest

from dbt.tests.util import (
    check_result_nodes_by_name,
    relation_from_name,
    run_dbt,
)


class TestContinuousAggregate:
    @pytest.fixture(scope="class")
    def project_config_update(self):
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
    def models(self):
        return {
            "base.sql": "select current_timestamp as time_column",
            "test_model.sql": "select * from {{ ref('base') }}",
        }

    def test_continuous_aggregate(self, project):
        results = run_dbt(["run"])
        assert len(results) == 1
        check_result_nodes_by_name(results, ["test_model"])

        relation = relation_from_name(project.adapter, "test_model")
        result = project.run_sql(f"select count(*) as num_rows from {relation}", fetch="one")
        assert result[0] == 1
