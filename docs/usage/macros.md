# Macros

The macros below are available to use in your dbt project. They are also used internally by the adapter to implement the configuration options.

## enable_compression

Enable compression on a table.

[Configuration options](compression.md#compression-settings)

```sql+jinja
{{ enable_compression('table_name', {"orderby": "column_name"}) }}
```
