# Retention policies

You can add a retention policy to automatically drop old chunks of data from (virtual) hypertables and continuous aggregates in the background.

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/use-timescale/latest/data-retention/about-data-retention/) to learn more about retention policies.

!!! note
    You can only create 1 retention policy per hypertable or continuous aggregate.

## Usage

=== "SQL"

    ```sql+jinja title="models/my_hypertable.sql"
    {{
      config(
        materialized='hypertable',
        main_dimension='time_column',
        retention_policy={
          "drop_after": "interval '1 month'"
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
              +main_dimension: time_column
              +retention_policy:
                drop_after: interval '1 month'
    # ...
    ```

## Configuration options

The following configuration options are supported (as part of `retention_policy`):

* `drop_after` (required)
* `schedule_interval`
* `initial_start`
* `timezone`
