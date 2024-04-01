from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import run_dbt


class TestContinuousAggregateRetentionPolicy:
    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "vht.sql": "--",
            "cagg.sql": """
{% if var("create_retention_policy", false) %}
    {{ config(retention_policy = {"drop_after": "interval '1 day'"}) }}
{% endif %}
select
    count(*) as col_1,
    time_bucket(interval '1 day', time_column) as bucket
from {{ ref('vht') }}
group by 2""",
        }

    @pytest.fixture(scope="class")
    def project_config_update(self) -> dict[str, Any]:
        return {
            "name": "retention_policy_tests",
            "models": {
                "retention_policy_tests": {
                    "cagg": {"+materialized": "continuous_aggregate"},
                    "vht": {"+materialized": "virtual_hypertable"},
                }
            },
        }

    def find_retention_policy_continuous_aggregates(self, project: TestProjInfo, unique_schema: str) -> int:
        timescale_jobs = project.run_sql(
            f"""
select *
from timescaledb_information.jobs j
join timescaledb_information.continuous_aggregates c
on j.hypertable_schema = c.materialization_hypertable_schema
and j.hypertable_name = c.materialization_hypertable_name
where j.proc_name = 'policy_retention'
and c.view_schema = '{unique_schema}'
and c.view_name = 'cagg'""",
            fetch="all",
        )
        return len(timescale_jobs)

    def test_continuous_aggregate_retention_policy(self, project: TestProjInfo, unique_schema: str) -> None:
        project.run_sql(f"""
create table {unique_schema}.vht (time_column timestamp);
select create_hypertable('{unique_schema}.vht', by_range('time_column'));""")

        results = run_dbt(["run"])
        assert len(results) == 2

        assert self.find_retention_policy_continuous_aggregates(project, unique_schema) == 0

        run_enable_results = run_dbt(["run", "--vars", "create_retention_policy: true"])
        assert len(run_enable_results) == 2

        assert self.find_retention_policy_continuous_aggregates(project, unique_schema) == 1

        run_disable_results = run_dbt(["run"])
        assert len(run_disable_results) == 2

        assert self.find_retention_policy_continuous_aggregates(project, unique_schema) == 0
