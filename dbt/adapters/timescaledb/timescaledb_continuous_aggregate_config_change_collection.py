from dataclasses import dataclass

from dbt.adapters.postgres.relation_configs.materialized_view import (
    PostgresMaterializedViewConfigChangeCollection,
)


@dataclass
class TimescaleDBContinuousAggregateConfigChangeCollection(PostgresMaterializedViewConfigChangeCollection):
    pass
