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
            {},
            {"+partitioning_column:": "col_1", "+number_partitions": 5},
            {"+chunk_time_interval": "interval '24 hours'"},
            {"+create_default_indexes": False},
            {"+associated_schema_name": "public"},
            {"+associated_table_prefix": "prefix_"},
            {"+compression": {}},
            {"+compression": {"orderby": "col_1 asc"}},
            {"+compression": {"segmentby": ["col_1"]}},
            {"+compression": {"chunk_time_interval": "24 hours"}},
        ],
        ids=[
            "default",
            "partitioning",
            "chunk_time_interval",
            "create_default_indexes",
            "associated_schema_name",
            "associated_table_prefix",
            "compression_default",
            "compression_orderby",
            "compression_segmentby",
            "compression_chunk_time_interval",
        ],
    )
    def model_config(self, request):
        return {
            "+materialized": "hypertable",
            "+time_column_name": "time_column",
        } | request.param

    @pytest.fixture(scope="class")
    def project_config_update(self, model_config):
        return {
            "name": "hypertable_tests",
            "models": {
                "hypertable_tests": {
                    "test_model": model_config,
                }
            },
        }

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "test_model.sql": """
select
    current_timestamp as time_column,
    1 as col_1
""",
        }

    def test_hypertable(self, project, unique_schema):
        results = run_dbt(["run"])
        assert len(results) == 1
        check_result_nodes_by_name(results, ["test_model"])
        assert results[0].node.node_info["materialized"] == "hypertable"

        relation = relation_from_name(project.adapter, "test_model")
        result = project.run_sql(f"select count(*) as num_rows from {relation}", fetch="one")
        assert result[0] == 1

        hypertables = project.run_sql(
            f"""
select *
from timescaledb_information.hypertables
where hypertable_name = 'test_model'
and hypertable_schema = '{unique_schema}'""",
            fetch="all",
        )
        assert len(hypertables) == 1
