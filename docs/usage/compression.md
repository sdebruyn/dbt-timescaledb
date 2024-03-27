# Compression

Compression is one of the key features of TimescaleDB and can speed up queries while drastically reducing storage requirements.

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/use-timescale/latest/compression/about-compression/) to learn more about compression.

## Usage

Compression is a configuration option for **(virtual) hypertables and continuous aggregates**. The only required argument is `after`, referring to the time interval after which compression should be applied. This can be an interval or an integer depending on the data type of your time column.

=== "SQL"

    ```sql+jinja title="models/my_hypertable.sql"
    {{
      config(
        materialized='hypertable',
        time_column_name='time_column',
        compression={
          after="interval '1 day'",
        }
      )
    }}
    select current_timestamp as time_column
    ```

=== "YAML"

    ```yaml title="dbt_project.yml"
    models:
      your_project_name:
        folder_containing_the_hypertables:
          +materialized: hypertable
          +compression: false # (1)!
            model_one:
              +time_column_name: time_column
              +compression:
                after: interval '1 day'
            model_two:
              +time_column_name: time_column_name_in_model_two
              +compression:
                after: interval '1 hour'
                chunk_time_interval: 1 day
                orderby: 'another_column'
                segmentby: ['column_one', 'column_two']
    # ...
    ```

    1. This is the default value and the same as leaving out the `compression` key entirely.

## Configuration options

The `after` option from the compression policy settings is the only required option.

### Compression settings

* `orderby` (string)
* `segmentby` (list of strings)
* `chunk_time_interval` (the actual interval, not prefixed with "interval")

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/api/latest/compression/alter_table_compression/) for more information regarding these settings.

### Compression policy settings

* `after` (interval or integer depending on your time column)
* `schedule_interval` (interval)
* `initial_start`
* `timezone`

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/api/latest/compression/add_compression_policy/#add_compression_policy) for more information regarding these settings.
