# Hypertables

[Hypertables](https://docs.timescale.com/use-timescale/latest/hypertables/about-hypertables/) are usually used to ingest time-series data. They are a high-performance version of regular Postgres tables focussed on time-based bucketting, chunking, and partitioning.

Hypertables make less sense as dbt models to store transformed data. However, you can still use them as such. A more useful version right now is the `empty` option, which will create empty hypertables.

!!! tip "Look into virtual hypertables"
    If you're looking to use dbt to configure your leverage pre-existing hypertables, check out the [virtual hypertables](../usage/virtual-hypertables.md) guide.

!!! danger "Only run hypertable models once"

    dbt will always recreate your entire model. This means that all existing data in your hypertables will be lost when you run them again. If you're using hypertables for ingesting time-series data, you probably don't want this.

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/use-timescale/latest/hypertables/about-hypertables/) for more information regarding hypertables.

## Usage

To materialize a model as a hypertable, simply set its `materialization` in the config to `hypertable`. Every hypertable also requires you to set the name of the time column.

=== "SQL"

    ```sql+jinja hl_lines="3 4" title="models/my_hypertable.sql"
    {{
      config(
        materialized='hypertable',
        main_dimension='time_column'
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
            model_one:
              +main_dimension: time_column  # (1)!
            model_two:
              +main_dimension: time_column_in_model_two
    # ...
    ```

    1.  While you can set the `hypertable` materialization for multiple models, you'll still have to configure the `main_dimension` for each model individually.

## Configuration options

### dbt-specific options

The following options are not taken from the TimescaleDB APIs, but are specific to this adapter.

* `empty_hypertable`: If set to `true`, the hypertable will be truncated right after creation (as a regular table) and right before converting it into a hypertable. Defaults to `false`.

### TimescaleDB hypertable options

The TimescaleDB option `create_default_indexes` can be set to `true` or `false`. It defaults to `true`.

--8<-- "docs_build/dimensions.md"

--8<-- "docs_build/integer_now_func.md"

--8<-- "docs_build/chunk_time_interval.md"
