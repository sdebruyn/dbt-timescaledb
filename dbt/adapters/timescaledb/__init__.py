from dbt.adapters.base import AdapterPlugin
from dbt.adapters.timescaledb.timescaledb_adapter import TimescaleDBAdapter
from dbt.adapters.timescaledb.timescaledb_credentials import TimescaleDBCredentials
from dbt.include import timescaledb

Plugin = AdapterPlugin(
    adapter=TimescaleDBAdapter,
    credentials=TimescaleDBCredentials,
    include_path=timescaledb.PACKAGE_PATH,
    dependencies=["postgres"],
)
