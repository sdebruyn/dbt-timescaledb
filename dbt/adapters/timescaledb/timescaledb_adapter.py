from typing import Any, Optional

from dbt.adapters.base.meta import available
from dbt.adapters.postgres import PostgresAdapter
from dbt.adapters.timescaledb.timescaledb_connection_manager import (
    NO_TRANSACTION_MARKER,
    TimescaleDBConnectionManager,
)
from dbt.adapters.timescaledb.timescaledb_index_config import TimescaleDBIndexConfig


class TimescaleDBAdapter(PostgresAdapter):
    ConnectionManager = TimescaleDBConnectionManager

    @available
    def parse_index(self, raw_index: Any) -> Optional[TimescaleDBIndexConfig]:  # noqa: ANN401
        return TimescaleDBIndexConfig.parse(raw_index)

    @available
    def marker_run_outside_transaction(self) -> str:
        return NO_TRANSACTION_MARKER
