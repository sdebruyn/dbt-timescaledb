from dbt.adapters.timescaledb.connections import TimescaleDBConnectionManager  # noqa
from dbt.adapters.timescaledb.connections import TimescaleDBCredentials
from dbt.adapters.timescaledb.impl import TimescaleDBAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import timescaledb


Plugin = AdapterPlugin(
    adapter=TimescaleDBAdapter, credentials=TimescaleDBCredentials, include_path=timescaledb.PACKAGE_PATH
)
