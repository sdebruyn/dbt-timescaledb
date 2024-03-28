from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import check_result_nodes_by_name, run_dbt


class TestHypertableDimension:
    @pytest.fixture(scope="class")
    def project_config_update(self) -> dict[str, Any]:
        return {
            "name": "hypertable_tests",
            "models": {
                "hypertable_tests": {
                    "test_model": {
                        "+materialized": "hypertable",
                        "+main_dimension": "time_column",
                        "+empty_hypertable": True,
                        "+dimensions": [
                            {"column_name": "id", "type": "by_hash", "number_partitions": 5},
                            {"column_name": "col_1", "partition_interval": 10000},
                        ],
                    }
                }
            },
        }

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "test_model.sql": "select current_timestamp as time_column, 1 as id, 2 as col_1",
        }

    def test_hypertable_dimension(self, project: TestProjInfo, unique_schema: str) -> None:
        results = run_dbt(["run"])
        assert len(results) == 1
        check_result_nodes_by_name(results, ["test_model"])

        dimensions_results = project.run_sql(
            f"""
select *
from timescaledb_information.dimensions
where hypertable_schema = '{unique_schema}'
and hypertable_name = 'test_model'
""",
            fetch="all",
        )
        assert len(dimensions_results) == 3

        dimension_time_column = [x for x in dimensions_results if x[3] == "time_column"][0]
        dimension_id_column = [x for x in dimensions_results if x[3] == "id"][0]
        dimension_col_1_column = [x for x in dimensions_results if x[3] == "col_1"][0]

        assert dimension_time_column[5] == "Time"
        assert dimension_id_column[5] == "Space"
        assert dimension_col_1_column[5] == "Time"

        assert dimension_id_column[9] == 5
        assert dimension_col_1_column[7] == 10000


class TestHypertableDimensionWithoutTruncateShouldRaiseException:
    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "test_model.sql": "select current_timestamp as time_column, 1 as id",
        }

    @pytest.fixture(scope="class")
    def project_config_update(self) -> dict[str, Any]:
        return {
            "name": "hypertable_tests",
            "models": {
                "hypertable_tests": {
                    "test_model": {
                        "+materialized": "hypertable",
                        "+main_dimension": "time_column",
                        "+dimensions": [{"column_name": "id"}],
                    }
                }
            },
        }

    def test_hypertable_dimension_throw_exception(self, project: TestProjInfo) -> None:
        results = run_dbt(["run"], expect_pass=False)
        assert len(results) == 1
        assert str(results[0].status) == "error"
