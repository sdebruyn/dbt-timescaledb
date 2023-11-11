from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
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
        ],
        ids=[
            "default",
            "partitioning",
            "chunk_time_interval",
            "create_default_indexes",
            "associated_schema_name",
            "associated_table_prefix",
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

    def test_hypertable(self, project: TestProjInfo, unique_schema: str) -> None:
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


class BaseTestHypertableCompression:
    @pytest.fixture(scope="class")
    def compression_settings(self) -> dict[str, Any]:
        return {"after": "interval '1 day'"}

    @pytest.fixture(
        scope="class"
        # params=[
        #     {"after": "interval '1 day'"},
        #     {"after": "interval '1 day'", "orderby": "col_1 asc"},
        #     {"after": "interval '1 day'", "segmentby": ["col_1"]},
        #     {"after": "interval '1 day'", "chunk_time_interval": "24 hours"},
        # ],
        # ids=[
        #     "compression_default",
        #     "compression_orderby",
        #     "compression_segmentby",
        #     "compression_chunk_time_interval",
        # ],
    )
    def model_config(self, compression_settings: dict[str, Any]) -> dict[str, Any]:
        return {
            "+materialized": "hypertable",
            "+time_column_name": "time_column",
            "+compression": compression_settings,
        }

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

    def validate_compression(self, compression_settings: list) -> None:
        assert len(compression_settings) == 1

    def test_hypertable(self, project: TestProjInfo, unique_schema: str) -> None:
        results = run_dbt(["run"])
        assert len(results) == 1
        check_result_nodes_by_name(results, ["test_model"])
        assert results[0].node.node_info["materialized"] == "hypertable"

        hypertables = project.run_sql(
            f"""
select *
from timescaledb_information.hypertables
where hypertable_name = 'test_model'
and hypertable_schema = '{unique_schema}'""",
            fetch="all",
        )
        assert len(hypertables) == 1
        hypertable = hypertables[0]
        assert hypertable[5]  # compression_enabled

        compression_settings = project.run_sql(
            f"""
select *
from timescaledb_information.compression_settings
where hypertable_name = 'test_model'
and hypertable_schema = '{unique_schema}'""",
            fetch="all",
        )
        self.validate_compression(compression_settings)


class TestHypertableCompressionDefault(BaseTestHypertableCompression):
    pass


class TestHypertableCompressionOrderBy(BaseTestHypertableCompression):
    def compression_settings(self) -> dict[str, Any]:
        return super().compression_settings() | {"orderby": "col_1 asc"}

    def validate_compression(self, compression_settings: list) -> None:
        assert len(compression_settings) == 2
