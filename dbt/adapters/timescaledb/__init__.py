from dbt.adapters.base import AdapterPlugin
from dbt.adapters.postgres import PostgresCredentials
from dbt.adapters.timescaledb.impl import TimescaleDBAdapter
from dbt.include import timescaledb

Plugin = AdapterPlugin(
    adapter=TimescaleDBAdapter,
    credentials=PostgresCredentials,
    include_path=timescaledb.PACKAGE_PATH,
    dependencies=["postgres"],
)

__all__ = ["TimescaleDBAdapter", "Plugin"]
