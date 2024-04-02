from dataclasses import dataclass, field
from typing import Set

from dbt.adapters.postgres.relation_configs.index import (
    PostgresIndexConfigChange,
)


@dataclass
class TimescaleDBHypertableConfigChangeCollection:
    indexes: Set[PostgresIndexConfigChange] = field(default_factory=set)

    @property
    def requires_full_refresh(self) -> bool:
        return any(index.requires_full_refresh for index in self.indexes)

    @property
    def has_changes(self) -> bool:
        return self.indexes != set()
