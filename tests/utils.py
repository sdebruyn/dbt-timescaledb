def get_indexes_sql(unique_schema: str, table_name: str) -> str:
    return f"""
        SELECT
          pg_get_indexdef(idx.indexrelid) as index_definition
        FROM pg_index idx
        JOIN pg_class tab ON tab.oid = idx.indrelid
        WHERE
          tab.relname = '{table_name}'
          AND tab.relnamespace = (
            SELECT oid FROM pg_namespace WHERE nspname = '{unique_schema}'
          );
    """
