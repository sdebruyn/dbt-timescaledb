from dbt.adapters.postgres import PostgresCredentials


class TimescaleDBCredentials(PostgresCredentials):
    @property
    def type(self):
        return "timescaledb"
