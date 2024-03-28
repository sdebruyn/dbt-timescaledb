from typing import Any

import pytest

from dbt.tests.fixtures.project import TestProjInfo
from dbt.tests.util import run_dbt
from tests.utils import get_indexes_sql


class TestHypertableIndex:
    def _model_sql(self, create_default_indexes: bool) -> str:
        return f"""
{{{{
  config(
    materialized = "hypertable",
    main_dimension = "time_column",
    create_default_indexes = {create_default_indexes},
    indexes=[
      {{'columns': ['col_1'], 'transaction_per_chunk': True}}
    ]
  )
}}}}

select
    current_timestamp as time_column,
    1 as col_1
"""

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "with_default.sql": self._model_sql(True),
            "without_default.sql": self._model_sql(False),
        }

    def test_table(self, project: TestProjInfo, unique_schema: str) -> None:
        results = run_dbt(["run"])
        assert len(results) == 2

        with_default_results = project.run_sql(get_indexes_sql(unique_schema, "with_default"), fetch="all")
        without_default_results = project.run_sql(
            get_indexes_sql(unique_schema, "without_default"), fetch="all"
        )

        assert len(with_default_results) == 2
        assert len(without_default_results) == 1
