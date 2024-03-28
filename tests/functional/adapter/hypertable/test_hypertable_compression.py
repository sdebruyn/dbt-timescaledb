from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import check_result_nodes_by_name, run_dbt


class BaseTestHypertableCompression:
    def base_compression_settings(self) -> dict[str, Any]:
        return {"after": "interval '1 day'", "schedule_interval": "interval '6 day'"}

    @pytest.fixture(scope="class")
    def compression_settings(self) -> dict[str, Any]:
        return self.base_compression_settings()

    @pytest.fixture(scope="class")
    def model_config(self, compression_settings: dict[str, Any]) -> dict[str, Any]:
        return {
            "+materialized": "hypertable",
            "+main_dimension": "time_column",
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
        timescale_jobs = project.run_sql(
            f"""
select *
from timescaledb_information.jobs
where hypertable_name = 'test_model'
and hypertable_schema = '{unique_schema}'
and application_name like 'Compression Policy%'
and schedule_interval = interval '6 day'""",
            fetch="all",
        )
        self.validate_jobs(timescale_jobs)


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


class TestHypertableCompressionDefault(BaseTestHypertableCompression):
    pass
