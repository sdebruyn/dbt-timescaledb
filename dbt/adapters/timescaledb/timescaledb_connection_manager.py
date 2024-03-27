from typing import Any, Optional, Tuple

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from dbt.adapters.contracts.connection import Connection
from dbt.adapters.events.logging import AdapterLogger
from dbt.adapters.postgres.connections import PostgresConnectionManager

NO_TRANSACTION_MARKER = "/* MARKER SHOULD RUN OUTSIDE TRANSACTION */"

logger = AdapterLogger("TimescaleDB")


class TimescaleDBConnectionManager(PostgresConnectionManager):
    TYPE = "timescaledb"

    def add_query(
        self,
        sql: str,
        auto_begin: bool = True,
        bindings: Optional[Any] = None,
        abridge_sql_log: bool = False,
    ) -> Tuple[Connection, Any]:
        restore_isolation_level = ISOLATION_LEVEL_AUTOCOMMIT
        connection = None

        if NO_TRANSACTION_MARKER in sql:
            logger.debug("Found marker to run SQL outside transaction")
            auto_begin = False
            connection = self.get_thread_connection()
            restore_isolation_level = connection.handle.isolation_level
            logger.debug(f"Current isolation level: {restore_isolation_level}")
            connection.handle.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            logger.debug(f"Set isolation level to {ISOLATION_LEVEL_AUTOCOMMIT} and autocommit to False")

        try:
            res1, res2 = super().add_query(sql, auto_begin, bindings, abridge_sql_log)
        finally:
            if restore_isolation_level != ISOLATION_LEVEL_AUTOCOMMIT:
                logger.debug(f"Restoring isolation level to {restore_isolation_level}")
                connection.handle.set_isolation_level(restore_isolation_level)

        return res1, res2
