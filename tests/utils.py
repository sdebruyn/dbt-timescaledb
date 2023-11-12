def get_indexes_sql(unique_schema: str, table_name: str) -> str:
    return f"""
select *
from pg_indexes
where schemaname = '{unique_schema}'
and tablename = '{table_name}'"""
