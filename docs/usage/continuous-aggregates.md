# Continuous aggregates

Continuous aggregates are the reason that this adapter exists. With this adapter, you can use dbt to manage your continuous aggregates and their configuration.

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/use-timescale/latest/hypertables/about-hypertables/) for more information on continuous aggregates.

!!! tip "Materialized views"
    dbt-postgres 1.6 added support for [materialized views](https://docs.getdbt.com/docs/build/materializations#materialized-view). This feature is **also still available** in this adapter. The main difference between materialized views and continuous aggregates is that continuous aggregates are automatically refreshed (based on a policy) by TimescaleDB, while materialized views are refreshed manually or when you run `dbt run`.

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
