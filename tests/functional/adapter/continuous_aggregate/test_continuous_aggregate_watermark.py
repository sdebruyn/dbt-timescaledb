from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import (
    check_result_nodes_by_name,
    run_dbt,
)


class TestContinuousAggregateWatermark:
    @pytest.fixture(scope="class")
    def project_config_update(self) -> dict[str, Any]:
        return {
            "name": "continuous_aggregate_tests",
            "models": {
                "continuous_aggregate_tests": {
                    "base": {"+materialized": "hypertable", "+main_dimension": "time_column"},
                    "test_model": {
                        "+materialized": "continuous_aggregate",
                        "+refresh_policy": {
                            "start_offset": "interval '1 month'",
                            "end_offset": "interval '1 day'",
                            "schedule_interval": "interval '3 day'",
                        },
                    },
                }
            },
        }

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "base.sql": "select current_timestamp as time_column, 1 as value",
            "test_model.sql": """
select
    time_bucket(interval '1 day', time_column) as bucket,
    sum(value) as total_value
from {{ ref('base') }}
group by 1
""",
        }

    def test_continuous_aggregate_watermark(self, project: TestProjInfo, unique_schema: str) -> None:
        results = run_dbt(["run"])
        assert len(results) == 2
        check_result_nodes_by_name(results, ["base", "test_model"])

        materialization_hypertable_id = project.run_sql(
            f"""
            SELECT id FROM _timescaledb_catalog.hypertable
            WHERE table_name=(
                SELECT materialization_hypertable_name
                FROM timescaledb_information.continuous_aggregates
                WHERE view_schema = '{unique_schema}'
                AND view_name = 'test_model'
            )
            """,
            fetch="one",
        )[0]

        is_watermark_valid = project.run_sql(
            f"""
            WITH w AS (
                SELECT _timescaledb_functions.cagg_watermark({materialization_hypertable_id}) as watermark_raw
            )
            SELECT
                w.watermark_raw IS NULL OR
                _timescaledb_functions.to_timestamp(w.watermark_raw) < now()
            FROM w
            """,
            fetch="one",
        )[0]

        assert is_watermark_valid, "Watermark is in the future"
