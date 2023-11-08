from dbt.adapters.postgres.connections import PostgresConnectionManager


class TimescaleDBConnectionManager(PostgresConnectionManager):
    TYPE = "timescaledb"
