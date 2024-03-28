from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import run_dbt


class BaseTestHypertableIntegerNowFunc:
    @pytest.fixture(scope="class")
    def extra_model_config(self) -> dict[str, Any]:
        return {}

    @pytest.fixture(scope="class")
    def project_config_update(self, extra_model_config: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": "hypertable_tests",
            "models": {
                "hypertable_tests": {
                    "test_model": {
                        "+materialized": "hypertable",
                        "+main_dimension": "id",
                        "+integer_now_func": "test_model_now",
                    }
                    | extra_model_config,
                }
            },
        }

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "test_model.sql": "select 1::bigint as id",
        }

    def prepare_func(self, project: TestProjInfo, unique_schema: str) -> None:
        pass

    def test_integer_now_func(self, project: TestProjInfo, unique_schema: str) -> None:
        self.prepare_func(project, unique_schema)
        results = run_dbt(["run"])
        assert len(results) == 1


class TestHypertableIntegerNowFuncWithoutSQL(BaseTestHypertableIntegerNowFunc):
    def prepare_func(self, project: TestProjInfo, unique_schema: str) -> None:
        project.run_sql(
            f"""
create or replace function {project.database}.{unique_schema}.test_model_now()
returns bigint language sql immutable as $$
      select extract(epoch from now())::bigint
    $$;
"""
        )


class TestHypertableIntegerNowFuncWithSQL(BaseTestHypertableIntegerNowFunc):
    @pytest.fixture(scope="class")
    def extra_model_config(self) -> dict[str, Any]:
        return {"integer_now_func_sql": "select extract(epoch from now())::bigint"}
