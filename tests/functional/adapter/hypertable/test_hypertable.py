from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import (
    check_result_nodes_by_name,
    relation_from_name,
    run_dbt,
)

_base_model_config: dict[str, str] = {
    "+materialized": "hypertable",
    "+main_dimension": "time_column",
}

_models_with_configs: dict[str, Any] = {
    "default": _base_model_config,
    "empty": _base_model_config
    | {
        "+empty_hypertable": True,
    },
}

_model_sql: str = """
select
    current_timestamp as time_column,
    1 as col_1
"""


class TestHypertable:
    @pytest.fixture(scope="class")
    def project_config_update(self) -> dict[str, Any]:
        return {
            "name": "hypertable_tests",
            "models": {"hypertable_tests": _models_with_configs},
        }

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {f"{k}.sql": _model_sql for k in _models_with_configs.keys()}

    def test_hypertable(self, project: TestProjInfo, unique_schema: str) -> None:
        results = run_dbt(["run"])
        assert len(results) == len(_models_with_configs)
        check_result_nodes_by_name(results, _models_with_configs.keys())
        assert all(result.node.config.materialized == "hypertable" for result in results)

        hypertables = project.run_sql(
            f"""
select *
from timescaledb_information.hypertables
where hypertable_schema = '{unique_schema}'""",
            fetch="all",
        )
        assert len(hypertables) == len(_models_with_configs)

        for model in _models_with_configs.keys():
            relation = relation_from_name(project.adapter, model)
            result = project.run_sql(f"select count(*) as num_rows from {relation}", fetch="one")
            assert result[0] == (0 if model == "empty" else 1)
