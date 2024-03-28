from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import check_result_nodes_by_name, run_dbt


class TestContinuousAggregateCompression:
    @pytest.fixture(scope="class")
    def project_config_update(self) -> dict[str, Any]:
        return {
            "name": "continuous_aggregate_tests",
            "models": {
                "continuous_aggregate_tests": {
                    "base": {
                        "+materialized": "hypertable",
                        "+main_dimension": "time_column",
                    },
                    "test_model": {
                        "+materialized": "continuous_aggregate",
                        "+refresh_policy": {
                            "start_offset": "interval '1 month'",
                            "end_offset": "interval '1 day'",
                            "schedule_interval": "interval '1 day'",
                        },
                        "+compression": {
                            "after": "interval '40 day'",
                            "schedule_interval": "interval '5 day'",
                        },
                    },
                }
            },
        }

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "base.sql": "select current_timestamp as time_column",
            "test_model.sql": """
select
    count(*),
    time_bucket(interval '1 day', time_column) as bucket
from {{ ref('base') }}
group by 2
""",
        }

    def test_continuous_aggregate(self, project: TestProjInfo, unique_schema: str) -> None:
        results = run_dbt(["run"])
        assert len(results) == 2
        check_result_nodes_by_name(results, ["base", "test_model"])

        continuous_aggregate_results = project.run_sql(
            f"""
select *
from timescaledb_information.continuous_aggregates
where view_schema = '{unique_schema}'
and view_name = 'test_model'""",
            fetch="all",
        )
        assert len(continuous_aggregate_results) == 1
        continuous_aggregate = continuous_aggregate_results[0]

        assert continuous_aggregate[2] == unique_schema
        assert continuous_aggregate[3] == "test_model"
        assert continuous_aggregate[6]  # compression_enabled

        job_results = project.run_sql(
            """
select *
from timescaledb_information.jobs
where application_name like 'Compression Policy%'
and schedule_interval = interval '5 day'
""",
            fetch="all",
        )
        assert len(job_results) == 1
