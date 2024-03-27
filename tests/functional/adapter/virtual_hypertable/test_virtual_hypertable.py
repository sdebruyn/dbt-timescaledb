from typing import Any

import pytest

from dbt.tests.util import (
    run_dbt,
)


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

    def run_assertions(self, project, unique_schema: str, hypertable) -> None:  # noqa: ANN001
        pass

    def test_virtual_hypertable(self, project, unique_schema: str) -> None:  # noqa: ANN001
        project.run_sql(f"create table {unique_schema}.vht (time_column timestamp, col_1 int);")
        project.run_sql(f"select create_hypertable('{unique_schema}.vht', 'time_column');")
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

        self.run_assertions(project, unique_schema, hypertable)


class TestVirtualHypertable(BaseTestVirtualHypertable):
    pass


class TestVirtualHypertableCompression(BaseTestVirtualHypertable):
    @pytest.fixture(scope="class")
    def extra_model_config(self) -> dict[str, Any]:
        return {"+compression": {"after": "interval '1 day'", "schedule_interval": "interval '6 day'"}}

    def run_assertions(self, project, unique_schema: str, hypertable) -> None:  # noqa: ANN001
        assert hypertable[5]  # compression_enabled

        compression_settings = project.run_sql(
            f"""
select *
from timescaledb_information.compression_settings
where hypertable_name = 'vht'
and hypertable_schema = '{unique_schema}'""",
            fetch="all",
        )

        assert len(compression_settings) == 1
        time_column = [x for x in compression_settings if x[2] == "time_column"][0]

        assert time_column[3] is None
        assert not time_column[5]
        assert time_column[6]

        timescale_jobs = project.run_sql(
            f"""
select *
from timescaledb_information.jobs
where hypertable_name = 'vht'
and hypertable_schema = '{unique_schema}'
and application_name like 'Compression Policy%'
and schedule_interval = interval '6 day'""",
            fetch="all",
        )
        assert len(timescale_jobs) == 1
        job = timescale_jobs[0]
        assert job[9]
