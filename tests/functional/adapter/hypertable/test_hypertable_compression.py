from datetime import timedelta
from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import check_result_nodes_by_name, run_dbt
from tests.utils import DEFAULT_ORDERBY, get_compression_settings_sql, get_jobs_sql


class BaseTestHypertableCompression:
    expected_segmentby: str | None = None
    expected_orderby: tuple[str | None, ...] = DEFAULT_ORDERBY
    expected_interval: str | None = None

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

    def validate_jobs(self, timescale_jobs: list) -> None:
        assert len(timescale_jobs) == 1
        job = timescale_jobs[0]
        assert job[2] == timedelta(days=6)  # schedule_interval
        assert job[9]  # scheduled

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

        segmentby, orderby, interval = project.run_sql(
            get_compression_settings_sql(unique_schema, "test_model"), fetch="one"
        )
        assert segmentby == self.expected_segmentby
        assert orderby in self.expected_orderby
        assert interval == self.expected_interval

        timescale_jobs = project.run_sql(
            get_jobs_sql(unique_schema, "test_model", "policy_compression"), fetch="all"
        )
        self.validate_jobs(timescale_jobs)


class TestHypertableCompressionSegmentBy(BaseTestHypertableCompression):
    expected_segmentby = "col_1"

    @pytest.fixture(scope="class")
    def compression_settings(self) -> dict[str, Any]:
        return super().base_compression_settings() | {"segmentby": ["col_1"]}


class TestHypertableCompressionChunkTimeInterval(BaseTestHypertableCompression):
    expected_interval = "1 day"

    @pytest.fixture(scope="class")
    def compression_settings(self) -> dict[str, Any]:
        return super().base_compression_settings() | {"chunk_time_interval": "1 day"}


class TestHypertableCompressionOrderBy(BaseTestHypertableCompression):
    expected_orderby = ("col_1,time_column DESC",)

    @pytest.fixture(scope="class")
    def compression_settings(self) -> dict[str, Any]:
        return super().base_compression_settings() | {"orderby": "col_1 asc"}


class TestHypertableCompressionDefault(BaseTestHypertableCompression):
    pass
