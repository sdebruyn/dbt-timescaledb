from typing import Literal

from dbt.adapters.postgres import PostgresCredentials


class TimescaleDBCredentials(PostgresCredentials):
    @property
    def type(self) -> Literal["timescaledb"]:
        return "timescaledb"
