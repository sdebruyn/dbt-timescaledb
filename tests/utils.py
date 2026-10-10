# TimescaleDB < 2.22 stores the default orderby; later versions pick it per chunk.
DEFAULT_ORDERBY = (None, "time_column DESC")


def get_indexes_sql(unique_schema: str, table_name: str) -> str:
    return f"""
select *
from pg_indexes
where schemaname = '{unique_schema}'
and tablename = '{table_name}'"""


# TimescaleDB < 2.20 lists a continuous aggregate's jobs under its materialization hypertable.
def get_jobs_sql(unique_schema: str, relation_name: str, proc_name: str) -> str:
    return f"""
select j.*
from timescaledb_information.jobs j
left join timescaledb_information.continuous_aggregates c
on j.hypertable_schema = c.materialization_hypertable_schema
and j.hypertable_name = c.materialization_hypertable_name
where j.proc_name = '{proc_name}'
and coalesce(c.view_schema, j.hypertable_schema) = '{unique_schema}'
and coalesce(c.view_name, j.hypertable_name) = '{relation_name}'"""


def get_compression_settings_sql(unique_schema: str, table_name: str) -> str:
    return f"""
select segmentby, orderby, compress_interval_length
from timescaledb_information.hypertable_compression_settings
where hypertable = '{unique_schema}.{table_name}'::regclass"""
