# Reorder policies

You can add a reorder policy to reorder chunks on a given (virtual) hypertable index in the background.

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/api/latest/hypertable/add_reorder_policy/) to learn more about reorder policies.

!!! note
    You can only create 1 reorder policy per hypertable.

## Usage

=== "SQL"

    ```sql+jinja title="models/my_hypertable.sql"
    {{
      config(
        materialized='hypertable',
        time_column_name='time_column',
        reorder_policy={
          index: {
            columns: ['column_a']
          }
        }
      )
    }}
    select
        current_timestamp as time_column,
        1 as column_a
    ```

=== "YAML"

    ```yaml title="dbt_project.yml"
    models:
      your_project_name:
        folder_containing_the_hypertables:
          +materialized: hypertable
            model_one:
              +time_column_name: time_column
              +reorder_policy:
                index:
                  columns: ['column_a']
    # ...
    ```

## Configuration options

* `index` (required): The configuration for the index to reorder on. See [dbt Postgres docs](https://docs.getdbt.com/reference/resource-configs/postgres-configs#indexes) for more information regarding how indexes can be configured.
* `create_index`: `true` by default. A boolean value to indicate if the index specified in `index` should be created or if it already exists.
