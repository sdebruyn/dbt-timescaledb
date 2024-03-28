from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import run_dbt


class BaseTestVirtualHypertableIntegerNowFunc:
    @pytest.fixture(scope="class")
    def extra_model_config(self) -> dict[str, Any]:
        return {}

    @pytest.fixture(scope="class")
    def project_config_update(self, extra_model_config: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": "virtual_hypertable_tests",
            "models": {
                "virtual_hypertable_tests": {
                    "vht": {
                        "+materialized": "virtual_hypertable",
                        "+integer_now_func": "test_model_now",
                    }
                    | extra_model_config,
                }
            },
        }

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "vht.sql": "--",
        }

    def prepare_func(self, project: TestProjInfo, unique_schema: str) -> None:
        project.run_sql(f"""
create table {unique_schema}.vht (id bigint);
select create_hypertable('{unique_schema}.vht', by_range('id'));""")

    def test_integer_now_func(self, project: TestProjInfo, unique_schema: str) -> None:
        self.prepare_func(project, unique_schema)
        results = run_dbt(["run"])
        assert len(results) == 1


class TestVirtualHypertableIntegerNowFuncWithoutSQL(BaseTestVirtualHypertableIntegerNowFunc):
    def prepare_func(self, project: TestProjInfo, unique_schema: str) -> None:
        super().prepare_func(project, unique_schema)
        project.run_sql(
            f"""
create or replace function {unique_schema}.test_model_now() returns bigint language sql immutable as $$
      select extract(epoch from now())::bigint
    $$;
"""
        )


class TestVirtualHypertableIntegerNowFuncWithSQL(BaseTestVirtualHypertableIntegerNowFunc):
    @pytest.fixture(scope="class")
    def extra_model_config(self) -> dict[str, Any]:
        return {"integer_now_func_sql": "select extract(epoch from now())::bigint"}
