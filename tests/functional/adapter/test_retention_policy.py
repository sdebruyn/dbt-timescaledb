from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import run_dbt

RETENTION_CONFIGS: list = [
    pytest.param(
        {
            "drop_after": "interval '1 day'",
        },
        id="drop_after",
    ),
    pytest.param(
        {"drop_after": "interval '1 day'", "schedule_interval": "interval '3 day'"},
        id="drop_after_schedule_interval",
    ),
]


class TestRetentionPolicy:
    @pytest.fixture(scope="class", params=RETENTION_CONFIGS)
    def retention_config(self, request: Any) -> dict[str, Any]:
        return request.param

    def base_models(self) -> dict[str, Any]:
        return {
            "base.sql": "select current_timestamp as time_column",
        }

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return self.base_models()

    @pytest.fixture(scope="class")
    def model_count(self, models: dict[str, Any]) -> int:
        return len(models)

    def base_model_config(self, retention_config: dict[str, Any]) -> dict[str, Any]:
        return {
            "base": {
                "+materialized": "hypertable",
                "+main_dimension": "time_column",
                "+retention_policy": retention_config,
            }
        }

    @pytest.fixture(scope="class")
    def model_configs(self, retention_config: dict[str, Any]) -> dict[str, Any]:
        return self.base_model_config(retention_config)

    @pytest.fixture(scope="class")
    def project_config_update(self, model_configs: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": "retention_policy_tests",
            "models": {"retention_policy_tests": model_configs},
        }

    def test_retention_policy(self, project: TestProjInfo, model_count: int, unique_schema: str) -> None:
        results = run_dbt(["run"])
        assert len(results) == model_count

        hypertable_jobs = project.run_sql(
            f"""
select *
from timescaledb_information.jobs
where proc_name = 'policy_retention'
and hypertable_schema = '{unique_schema}'
and hypertable_name = 'base'
""",
            fetch="all",
        )
        assert len(hypertable_jobs) == 1


class TestRetentionPolicyOnContinuousAggregate(TestRetentionPolicy):
    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return self.base_models() | {
            "cagg.sql": """
select
    count(*) as col_1,
    time_bucket(interval '1 day', time_column) as bucket
from {{ ref('base') }}
group by 2
""",
        }

    @pytest.fixture(scope="class")
    def model_configs(self, retention_config: dict[str, Any]) -> dict[str, Any]:
        return super().base_model_config(retention_config) | {
            "cagg": {
                "+materialized": "continuous_aggregate",
                "+retention_policy": retention_config,
            }
        }

    def test_retention_policy(self, project: TestProjInfo, model_count: int, unique_schema: str) -> None:
        super().test_retention_policy(project, model_count, unique_schema)

        cagg_jobs = project.run_sql(
            f"""
select *
from timescaledb_information.jobs j
join timescaledb_information.continuous_aggregates c
on j.hypertable_schema = c.materialization_hypertable_schema
and j.hypertable_name = c.materialization_hypertable_name
where j.proc_name = 'policy_retention'
and c.view_schema = '{unique_schema}'
and c.view_name = 'cagg'
""",
            fetch="all",
        )
        assert len(cagg_jobs) == 1
