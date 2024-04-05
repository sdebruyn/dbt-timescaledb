from datetime import timedelta
from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import run_dbt


class TestVirtualHypertableChunkTimeInterval:
    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {"vht.sql": "--"}

    @pytest.fixture(scope="class")
    def project_config_update(self) -> dict[str, Any]:
        return {
            "name": "virtual_hypertable_tests",
            "models": {
                "virtual_hypertable_tests": {
                    "vht": {"+materialized": "virtual_hypertable", "+chunk_time_interval": "interval '1 day'"}
                }
            },
        }

    def test_virtual_hypertable_chunk_time_interval(self, project: TestProjInfo, unique_schema: str) -> None:
        project.run_sql(f"""
create table {unique_schema}.vht (time_column timestamp, col_1 int);
select create_hypertable('{unique_schema}.vht', by_range('time_column'));""")

        check_interval_query = f"""
select time_interval from timescaledb_information.dimensions
where hypertable_schema = '{unique_schema}'
and hypertable_name = 'vht'
and column_name = 'time_column';
        """
        before: timedelta = project.run_sql(check_interval_query, fetch="all")[0][0]

        results = run_dbt(["run"])
        assert len(results) == 1

        after: timedelta = project.run_sql(check_interval_query, fetch="all")[0][0]

        assert before.days == 7
        assert after.days == 1
