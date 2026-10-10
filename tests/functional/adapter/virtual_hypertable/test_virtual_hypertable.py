from datetime import timedelta
from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import (
    run_dbt,
)
from tests.utils import DEFAULT_ORDERBY, get_compression_settings_sql, get_jobs_sql


class BaseTestVirtualHypertable:
    @pytest.fixture(scope="class")
    def extra_model_config(self) -> dict[str, Any]:
        return {}

    @pytest.fixture(scope="class")
    def project_config_update(self, extra_model_config: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": "virtual_hypertable_tests",
            "models": {
                "virtual_hypertable_tests": {
                    "vht": {"+materialized": "virtual_hypertable"} | extra_model_config
                }
            },
        }

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {"vht.sql": "--"}

    def run_assertions(self, project: TestProjInfo, unique_schema: str, hypertable: Any) -> None:
        pass

    def test_virtual_hypertable(self, project: TestProjInfo, unique_schema: str) -> None:
        project.run_sql(f"""
create table {unique_schema}.vht (time_column timestamp, col_1 int);
select create_hypertable('{unique_schema}.vht', by_range('time_column'));""")
        results = run_dbt(["run"])
        assert len(results) == 1
        assert all(result.node.config.materialized == "virtual_hypertable" for result in results)

        hypertables = project.run_sql(
            f"""
select *
from timescaledb_information.hypertables
where hypertable_name = 'vht'
and hypertable_schema = '{unique_schema}'""",
            fetch="all",
        )
        assert len(hypertables) == 1
        hypertable = hypertables[0]

        timescale_jobs = project.run_sql(
            get_jobs_sql(unique_schema, "vht", "policy_compression"), fetch="all"
        )
        self.validate_jobs(timescale_jobs)

        self.run_assertions(project, unique_schema, hypertable)

    def validate_jobs(self, jobs: Any) -> None:
        assert len(jobs) == 0


class TestVirtualHypertable(BaseTestVirtualHypertable):
    pass


class TestVirtualHypertableCompression(BaseTestVirtualHypertable):
    @pytest.fixture(scope="class")
    def extra_model_config(self) -> dict[str, Any]:
        return {"+compression": {"after": "interval '1 day'", "schedule_interval": "interval '6 day'"}}

    def run_assertions(self, project: TestProjInfo, unique_schema: str, hypertable: Any) -> None:
        assert hypertable[5]  # compression_enabled

        segmentby, orderby, interval = project.run_sql(
            get_compression_settings_sql(unique_schema, "vht"), fetch="one"
        )
        assert segmentby is None
        assert orderby in DEFAULT_ORDERBY
        assert interval is None

    def validate_jobs(self, jobs: Any) -> None:
        assert len(jobs) == 1
        job = jobs[0]
        assert job[2] == timedelta(days=6)  # schedule_interval
        assert job[9]  # scheduled
