# Transaction per chunk indexes

Next to all regular Postgres indexes, TimescaleDB also supports [transaction per chunk](https://docs.timescale.com/api/latest/hypertable/create_index/) indexes.

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/api/latest/hypertable/create_index/) for more information regarding the usage of these indexes.

## Usage

To create a transaction per chunk index, simply set the `transaction_per_chunk` option to `true` in the [index configuration](https://docs.getdbt.com/reference/resource-configs/postgres-configs#indexes), similar to the `unique` option.

=== "SQL"

    ```sql+jinja hl_lines="5" title="models/my_hypertable.sql"
    {{ config(
        materialized='hypertable',
        main_dimension='time_column',
        indexes=[
          {'columns': ['column_a'], 'transaction_per_chunk': True}
        ]
    }}

    select ...
    ```

=== "YAML"

    ```yaml hl_lines="8" title="dbt_project.yml"
    models:
      your_project_name:
        model_name:
          +materialized: hypertable
          +main_dimension: time_column
          +indexes:
            - columns: ['column_a']
              transaction_per_chunk: true
    # ...
    ```

!!! info
    Consult the [dbt Postgres docs](https://docs.getdbt.com/reference/resource-configs/postgres-configs#indexes) for more information regarding how indexes can be configured.
