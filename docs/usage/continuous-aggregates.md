# Continuous aggregates

Continuous aggregates are the reason that this adapter exists. With this adapter, you can use dbt to manage your continuous aggregates and their configuration.

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/use-timescale/latest/hypertables/about-hypertables/) for more information regarding continuous aggregates.

!!! tip "Materialized views"
    dbt-postgres 1.6 added support for [materialized views](https://docs.getdbt.com/docs/build/materializations#materialized-view). This feature is **also still available** in this adapter. The main difference between materialized views and continuous aggregates is that continuous aggregates are automatically refreshed (based on a policy) by TimescaleDB, while materialized views are refreshed manually or when you run `dbt run`.

!!! tip "Full refresh"
    Once continuous aggregates have been created, only its metadata will be updated on subsequent runs. If you need to fully refresh the continuous aggregate, - maybe because you have changed its implementation - you can use the `full-refresh` option in dbt to drop and recreate the continuous aggregate.

!!! failure "CTEs and subqueries not supported"
    TimescaleDB [does not support](https://github.com/timescale/timescaledb/issues/1931) [CTE](https://docs.getdbt.com/terms/cte)s, subqueries and set-returning functions in continuous aggregates.

## Usage

To use continuous aggregates, you need to set the `materialized` config to `continuous_aggregate`.

=== "SQL"

    ```sql+jinja hl_lines="2" title="models/my_aggregate.sql"
    {{
      config(materialized='continuous_aggregate')
    }}
    select
        count(*),
        time_bucket(interval '1 day', time_column) as bucket
    from {{ source('a_hypertable') }}
    group by 2
    ```

=== "YAML"

    ```yaml hl_lines="4" title="dbt_project.yaml"
    models:
      your_project_name:
        model_name:
          +materialized: continuous_aggregate
    # ...
    ```

## Configuration options

### dbt-specific options: refreshing upon creation

Continuous aggregates are refreshed automatically by TimescaleDB. This is configured using a [refresh policy](#timescaledb-refresh-policy-options).

They are also refreshed initially when they are created. This is done by default but can be disabled by setting the `refresh_now` config option to `false`.

### TimescaleDB continuous aggregate options

All [TimescaleDB continuous aggregate configuration options](https://docs.timescale.com/api/latest/continuous-aggregates/create_materialized_view/#parameters) as of version 2.12 are supported through model configuration as well:

* `materialized_only` (make sure to quote the value when setting to false, e.g. "False")
* `create_group_indexes`

### TimescaleDB refresh policy options

A continuous aggregate is usually used with a refresh policy. This is configured using the `refresh_policy` config option. The following options are supported:

* `start_offset`
* `end_offset`
* `schedule_interval`
* `initial_start`
* `timezone`

=== "SQL"

    ```sql+jinja hl_lines="2" title="models/my_aggregate.sql"
    {{
      config(
        materialized='continuous_aggregate',
        refresh_policy={
          'start_offset': "interval '1 month'",
          'end_offset': "interval '1 hour'",
          'schedule_interval': "interval '1 hour'",
        })
    }}
    select
        count(*),
        time_bucket(interval '1 day', time_column) as bucket
    from {{ source('a_hypertable') }}
    group by 2
    ```

=== "YAML"

    ```yaml hl_lines="4" title="dbt_project.yaml"
    models:
      your_project_name:
        model_name:
          +materialized: continuous_aggregate
          +refresh_policy:
            start_offset: "interval '1 month'"
            end_offset: "interval '1 hour'"
            schedule_interval: "interval '1 hour'"
    # ...
    ```

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/api/latest/continuous-aggregates/add_continuous_aggregate_policy/) for more information regarding these settings.
