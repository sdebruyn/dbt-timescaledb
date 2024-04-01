from typing import Optional

from dbt.adapters.contracts.relation import RelationConfig
from dbt.adapters.postgres.relation import PostgresRelation
from dbt.adapters.relation_configs import (
    RelationResults,
)
from dbt.adapters.timescaledb.timescaledb_continuous_aggregate_config_change_collection import (
    TimescaleDBContinuousAggregateConfigChangeCollection,
)
from dbt.adapters.timescaledb.timescaledb_hypertable_config_change_collection import (
    TimescaleDBHypertableConfigChangeCollection,
)


class TimescaleDBRelation(PostgresRelation):
    pass

    def get_hypertable_config_change_collection(
        self, relation_results: RelationResults, relation_config: RelationConfig
    ) -> Optional[TimescaleDBHypertableConfigChangeCollection]:
        return self.get_materialized_view_config_change_collection(
            relation_results=relation_results, relation_config=relation_config
        )

    def get_continuous_aggregate_config_change_collection(
        self, relation_results: RelationResults, relation_config: RelationConfig
    ) -> Optional[TimescaleDBContinuousAggregateConfigChangeCollection]:
        return self.get_materialized_view_config_change_collection(
            relation_results=relation_results, relation_config=relation_config
        )
