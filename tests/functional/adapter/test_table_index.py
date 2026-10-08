from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import run_dbt
from tests.utils import get_indexes_sql


class TestTableIndex:
    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "table_with_index.sql": """
{{ config(materialized = "table", indexes = [{"columns": ["col_1"]}]) }}

select 1 as col_1
"""
        }

    def test_table_index(self, project: TestProjInfo, unique_schema: str) -> None:
        for _ in range(2):
            results = run_dbt(["run"])
            assert len(results) == 1

            indexes = project.run_sql(get_indexes_sql(unique_schema, "table_with_index"), fetch="all")
            assert len(indexes) == 1
