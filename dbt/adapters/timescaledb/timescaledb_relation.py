from dataclasses import dataclass
from typing import Optional, Set

import agate

from dbt.adapters.contracts.relation import RelationConfig
from dbt.adapters.postgres.relation import PostgresRelation
from dbt.adapters.postgres.relation_configs import (
    PostgresIndexConfig,
    PostgresIndexConfigChange,
)
from dbt.adapters.relation_configs import (
    RelationResults,
)


@dataclass(frozen=True, eq=False, repr=False)
class TimescaleDBRelation(PostgresRelation):
    def get_hypertable_index_changes(
        self, relation_results: RelationResults, relation_config: RelationConfig
    ) -> Optional[Set[PostgresIndexConfigChange]]:
        if not relation_results:
            return None

        index_rows: agate.Table = relation_results.get("indexes", agate.Table(rows={}))
        index_dicts = [PostgresIndexConfig.parse_relation_results(index) for index in index_rows.rows]
        index_list = [PostgresIndexConfig.from_dict(index) for index in index_dicts]
        filtered_list = [
            index
            for index in index_list
            if not (
                not index.unique
                and index.method == "btree"
                and len(index.column_names) == 1
                and index.name.endswith("_idx")
            )
        ]
        index_set = frozenset(filtered_list)

        indexes_from_config = relation_config.config.get("indexes", [])
        parsed_from_config = [PostgresIndexConfig.parse_model_node(index) for index in indexes_from_config]
        set_from_config = frozenset(parsed_from_config)

        return self._get_index_config_changes(index_set, set_from_config)
