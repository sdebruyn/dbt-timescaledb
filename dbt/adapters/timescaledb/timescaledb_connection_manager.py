import time
from typing import Any, Optional, Tuple

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from dbt.adapters.postgres.connections import PostgresConnectionManager
from dbt.contracts.connection import Connection
from dbt.events.contextvars import get_node_info
from dbt.events.functions import fire_event
from dbt.events.types import ConnectionUsed, SQLQuery, SQLQueryStatus
from dbt.utils import cast_to_str


class TimescaleDBConnectionManager(PostgresConnectionManager):
    TYPE = "timescaledb"

    def add_query(
        self,
        sql: str,
        auto_begin: bool = True,
        bindings: Optional[Any] = None,
        abridge_sql_log: bool = False,
    ) -> Tuple[Connection, Any]:
        connection = self.get_thread_connection()

        if auto_begin and connection.transaction_open is False:
            self.begin()
        fire_event(
            ConnectionUsed(
                conn_type=self.TYPE,
                conn_name=cast_to_str(connection.name),
                node_info=get_node_info(),
            )
        )

        with self.exception_handler(sql):
            if abridge_sql_log:
                log_sql = "{}...".format(sql[:512])
            else:
                log_sql = sql

            fire_event(
                SQLQuery(conn_name=cast_to_str(connection.name), sql=log_sql, node_info=get_node_info())
            )
            pre = time.time()

            restore_isolation_level = -1
            if "-- MARKER RUN OUTSIDE TRANSACTION" in sql:
                restore_isolation_level = connection.handle.isolation_level
                connection.handle.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            cursor = connection.handle.cursor()
            try:
                cursor.execute(sql, bindings)
            finally:
                if restore_isolation_level != -1:
                    connection.handle.set_isolation_level(restore_isolation_level)

            fire_event(
                SQLQueryStatus(
                    status=str(self.get_response(cursor)),
                    elapsed=round((time.time() - pre)),
                    node_info=get_node_info(),
                )
            )

            return connection, cursor
