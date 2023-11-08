from dbt.adapters.postgres import PostgresAdapter
from dbt.adapters.timescaledb.timescaledb_connection_manager import TimescaleDBConnectionManager


class TimescaleDBAdapter(PostgresAdapter):
    ConnectionManager = TimescaleDBConnectionManager
