from typing import Any

import pytest

from dbt.tests.util import (
    check_result_nodes_by_name,
    relation_from_name,
    run_dbt,
)


class TestHypertable:
    @pytest.fixture(
        scope="class",
        params=[
            pytest.param({}, id="default"),
            pytest.param({"+partitioning_column:": "col_1", "+number_partitions": 5}, id="partitioning"),
            pytest.param({"+empty_hypertable": True}, id="empty", marks=pytest.mark.empty),
            pytest.param({"+chunk_time_interval": "interval '24 hours'"}, id="chunk_time_interval"),
            pytest.param({"+create_default_indexes": False}, id="create_default_indexes"),
            pytest.param({"+associated_schema_name": "public"}, id="associated_schema_name"),
            pytest.param({"+associated_table_prefix": "prefix_"}, id="associated_table_prefix"),
        ],
    )
    def model_config(self, request) -> dict[str, Any]:  # noqa: ANN001
        return {
            "+materialized": "hypertable",
            "+time_column_name": "time_column",
        } | request.param

    @pytest.fixture(scope="class")
    def project_config_update(self, model_config: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": "hypertable_tests",
            "models": {
                "hypertable_tests": {
                    "test_model": model_config,
                }
            },
        }

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "test_model.sql": """
select
    current_timestamp as time_column,
    1 as col_1
""",
        }

    def test_hypertable(self, project, unique_schema: str, request) -> None:  # noqa: ANN001
        results = run_dbt(["run"])
        assert len(results) == 1
        check_result_nodes_by_name(results, ["test_model"])
        assert results[0].node.node_info["materialized"] == "hypertable"

        relation = relation_from_name(project.adapter, "test_model")
        result = project.run_sql(f"select count(*) as num_rows from {relation}", fetch="one")
        assert result[0] == (0 if request.node.get_closest_marker("empty") else 1)

        hypertables = project.run_sql(
            f"""
select *
from timescaledb_information.hypertables
where hypertable_name = 'test_model'
and hypertable_schema = '{unique_schema}'""",
            fetch="all",
        )
        assert len(hypertables) == 1
