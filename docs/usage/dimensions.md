### Dimensions

Hypertables and virtual hypertables have one or more dimensions.

In this adapter, dimensions can be provided as a dictionary with the following options:

* `column_name`
* `type`: `by_hash` or `by_range`
* `partition_interval` (only for `by_range`)
* `number_partitions` (only for `by_hash`)
* `partitioning_func`
* `chunk_time_interval` (not for the main time dimension of a hypertable)

!!! warning "Empty hypertable required"
    You can only add dimensions to an empty hypertable.

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/api/latest/hypertable/add_dimension/) for more information regarding adding dimensions or the [documentation on dimension builders](https://docs.timescale.com/api/latest/hypertable/dimension_info/).

=== "SQL"

    ```sql+jinja hl_lines="5" title="models/my_hypertable.sql"
    {{ config(
        materialized = 'hypertable',
        main_dimension = {"column_name": "time_column", "type": "by_range"},
        dimensions=[
          {"column_name": "id", "type": "by_hash", "number_partitions": 5},
          {"column_name": "col_1", "type": "by_range", "chunk_time_interval": 10000},
          {"column_name": "another_column", "type": "by_range"}
        ]
    }}

    select
      current_timestamp as time_column,
      1 as id,
      2 as col_1,
      3 as another_column
    ```

=== "YAML"

    ```yaml hl_lines="8" title="dbt_project.yml"
    models:
      your_project_name:
        model_name:
          +materialized: hypertable
          +main_dimension:
            column_name: time_column
            type: by_range
          +dimensions:
            - column_name: id
              type: by_hash
              number_partitions: 5
            - column_name: another_time_column
              type: by_range
              chunk_time_interval: interval '1 day'
    # ...
    ```
