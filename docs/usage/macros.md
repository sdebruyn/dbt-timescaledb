# Macros

The macros below are available to use in your dbt project. They are also used internally by the adapter to implement the configuration options.

!!! tip
    Usually the macros below won't be used directly but instead will be used via the configuration options of the hypertables and continuous aggregates. They are documented here for completeness.

## `enable_compression`

Enable compression on a (virtual) hypertable or continuous aggregate.

[Configuration options](compression.md#compression-settings)

```sql+jinja
{{ enable_compression('table_name', {"orderby": "column_name"}) }}
```

## `add_compression_policy`

Add a compression policy to a (virtual) hypertable or continuous aggregate.

[Configuration options](compression.md#compression-policy-settings)

```sql+jinja
{{ add_compression_policy('table_name', {"after": "interval '60d'"}) }}
```

## `add_reorder_policy`

Add a reorder policy to a (virtual) hypertable.

[Configuration options](reorder-policies.md#configuration-options)

```sql+jinja
{{ add_reorder_policy('table_name', {"index": {"columns": "column_name"}}) }}
```

## `clear_reorder_policy`

Remove any existing reorder policy from a (virtual) hypertable.

```sql+jinja
{{ clear_reorder_policy('table_name') }}
```

## `add_refresh_policy`

Add a refresh policy to a continuous aggregate.

[Configuration options](continuous-aggregates.md#timescaledb-refresh-policy-options)

```sql+jinja
{{ add_refresh_policy('continuous_aggregate_name', {
    "start_offset": "interval '3 day'",
    "end_offset": "interval '2 day'"}) }}
```

## `set_integer_now_func`

Set the function used to generate the current time for integer time columns in hypertables.

```sql+jinja
{{ set_integer_now_func('table_name', 'function_name') }}
```

## `add_dimension`

Add a dimension to a hypertable.

```sql+jinja
{{ add_dimension('table_name', dimension_config) }}
```

--8<-- "docs_build/dimensions.md:5"

## `add_retention_policy`

Add a retention policy to a (virtual) hypertable or continuous aggregate.

[Configuration options](retention-policies.md#configuration-options)

```sql+jinja
{{ add_retention_policy('table_name', {
    "drop_after": "interval '1 month'"
}) }}
```

## `clear_retention_policy`

Remove any existing retention policy from a (virtual) hypertable or a continuous aggregate.

```sql+jinja
{{ clear_retention_policy('table_name') }}
```
