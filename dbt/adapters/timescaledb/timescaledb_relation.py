from dataclasses import dataclass
from typing import Optional

import agate

from dbt.adapters.contracts.relation import RelationConfig
from dbt.adapters.postgres.relation import PostgresRelation
from dbt.adapters.postgres.relation_configs import (
    PostgresIndexConfig,
)
from dbt.adapters.relation_configs import (
    RelationResults,
)
from dbt.adapters.timescaledb.timescaledb_change_collection import TimescaleDBHypertableConfigChangeCollection


@dataclass(frozen=True, eq=False, repr=False)
class TimescaleDBRelation(PostgresRelation):
    def get_hypertable_config_change_collection(
        self, relation_results: RelationResults, relation_config: RelationConfig
    ) -> Optional[TimescaleDBHypertableConfigChangeCollection]:
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
        obj_from_config = [PostgresIndexConfig.from_dict(index) for index in parsed_from_config]
        set_from_config = frozenset(obj_from_config)

        # add_reorder_policy creates and reuses this index itself; keep it out of the comparison.
        reorder_policy = relation_config.config.get("reorder_policy") or {}
        create_index = reorder_policy.get("create_index")
        if reorder_policy and (create_index is None or create_index):
            reorder_index = PostgresIndexConfig.from_dict(
                PostgresIndexConfig.parse_model_node(reorder_policy.get("index") or {})
            )
            index_set -= {reorder_index}
            set_from_config -= {reorder_index}

        changeset = TimescaleDBHypertableConfigChangeCollection(
            indexes=self._get_index_config_changes(index_set, set_from_config)
        )
        return changeset if changeset.has_changes else None
