from typing import Any

import pytest

from dbt.tests.util import run_dbt


class TestHypertableIndex:
    def _model_sql(self, create_default_indexes: bool) -> str:
        return f"""
{{{{
  config(
    materialized = "hypertable",
    time_column_name = "time_column",
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

    def _get_indexes_sql(self, unique_schema: str, table_name: str) -> str:
        return f"""
            SELECT
              pg_get_indexdef(idx.indexrelid) as index_definition
            FROM pg_index idx
            JOIN pg_class tab ON tab.oid = idx.indrelid
            WHERE
              tab.relname = '{table_name}'
              AND tab.relnamespace = (
                SELECT oid FROM pg_namespace WHERE nspname = '{unique_schema}'
              );
        """

    @pytest.fixture(scope="class")
    def models(self) -> dict[str, Any]:
        return {
            "with_default.sql": self._model_sql(True),
            "without_default.sql": self._model_sql(False),
        }

    def test_table(self, project: Any, unique_schema: str) -> None:  # noqa: ANN401
        results = run_dbt(["run"])
        assert len(results) == 2

        with_default_results = project.run_sql(
            self._get_indexes_sql(unique_schema, "with_default"), fetch="all"
        )
        without_default_results = project.run_sql(
            self._get_indexes_sql(unique_schema, "without_default"), fetch="all"
        )

        assert len(with_default_results) == 2
        assert len(without_default_results) == 1
