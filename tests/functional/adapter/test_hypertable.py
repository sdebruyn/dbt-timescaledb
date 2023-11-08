import pytest

from dbt.tests.util import (
    check_result_nodes_by_name,
    relation_from_name,
    run_dbt,
)


class TestHypertable:
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "name": "hypertable_tests",
            "models": {
                "hypertable_tests": {
                    "test_model": {"+materialized": "hypertable", "+time_column_name": "time_column"}
                }
            },
        }

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "test_model.sql": "select current_timestamp as time_column",
        }

    def test_hypertable(self, project):
        results = run_dbt(["run"])
        assert len(results) == 1
        check_result_nodes_by_name(results, ["test_model"])

        relation = relation_from_name(project.adapter, "test_model")
        result = project.run_sql(f"select count(*) as num_rows from {relation}", fetch="one")
        assert result[0] == 1
