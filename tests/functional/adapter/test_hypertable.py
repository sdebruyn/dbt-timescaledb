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


class BaseTestHypertableCompression:
    def base_compression_settings(self) -> dict[str, Any]:
        return {"after": "interval '1 day'"}

    @pytest.fixture(scope="class")
    def compression_settings(self) -> dict[str, Any]:
        return self.base_compression_settings()

    @pytest.fixture(scope="class")
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
        time_column = [x for x in compression_settings if x[2] == "time_column"][0]

        assert time_column[3] is None
        assert not time_column[5]
        assert time_column[6]

    def validate_jobs(self, timescale_jobs: list) -> None:
        assert len(timescale_jobs) == 1
        job = timescale_jobs[0]
        assert job[9]

    def test_hypertable(self, project, unique_schema: str) -> None:  # noqa: ANN001
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
        timescale_jobs = project.run_sql(
            f"""
select *
from timescaledb_information.jobs
where hypertable_name = 'test_model'
and hypertable_schema = '{unique_schema}'""",
            fetch="all",
        )
        self.validate_jobs(timescale_jobs)


class TestHypertableCompressionDefault(BaseTestHypertableCompression):
    pass


class TestHypertableCompressionOrderBy(BaseTestHypertableCompression):
    @pytest.fixture(scope="class")
    def compression_settings(self) -> dict[str, Any]:
        return super().base_compression_settings() | {"orderby": "col_1 asc"}

    def validate_compression(self, compression_settings: list) -> None:
        assert len(compression_settings) == 2
        time_column = [x for x in compression_settings if x[2] == "time_column"][0]
        col_1 = [x for x in compression_settings if x[2] == "col_1"][0]

        assert time_column[3] is None
        assert not time_column[5]
        assert time_column[6]

        assert col_1[3] is None
        assert col_1[4] == 1
        assert col_1[5]
        assert not col_1[6]


class TestHypertableCompressionSegmentBy(BaseTestHypertableCompression):
    @pytest.fixture(scope="class")
    def compression_settings(self) -> dict[str, Any]:
        return super().base_compression_settings() | {"segmentby": ["col_1"]}

    def validate_compression(self, compression_settings: list) -> None:
        assert len(compression_settings) == 2
        time_column = [x for x in compression_settings if x[2] == "time_column"][0]
        col_1 = [x for x in compression_settings if x[2] == "col_1"][0]

        assert time_column[3] is None
        assert not time_column[5]
        assert time_column[6]

        assert col_1[3] == 1
        assert col_1[4] is None
        assert col_1[5] is None
        assert col_1[6] is None


class TestHypertableCompressionChunkTimeInterval(BaseTestHypertableCompression):
    @pytest.fixture(scope="class")
    def compression_settings(self) -> dict[str, Any]:
        return super().base_compression_settings() | {"chunk_time_interval": "1 day"}
