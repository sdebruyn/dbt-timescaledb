from typing import Any, Optional, Tuple

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from dbt.adapters.postgres.connections import PostgresConnectionManager
from dbt.contracts.connection import Connection


class TimescaleDBConnectionManager(PostgresConnectionManager):
    TYPE = "timescaledb"

    def add_query(
        self,
        sql: str,
        auto_begin: bool = True,
        bindings: Optional[Any] = None,  # noqa: ANN401
        abridge_sql_log: bool = False,
    ) -> Tuple[Connection, Any]:
        restore_isolation_level = ISOLATION_LEVEL_AUTOCOMMIT
        connection = None

        if "-- MARKER RUN OUTSIDE TRANSACTION" in sql:
            auto_begin = False
            connection = self.get_thread_connection()
            restore_isolation_level = connection.handle.isolation_level
            connection.handle.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        try:
            res1, res2 = super().add_query(sql, auto_begin, bindings, abridge_sql_log)
        finally:
            if restore_isolation_level != ISOLATION_LEVEL_AUTOCOMMIT:
                connection.handle.set_isolation_level(restore_isolation_level)

        return res1, res2
