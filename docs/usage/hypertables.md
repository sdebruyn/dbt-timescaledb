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
        time_column_name='time_column'
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
              +time_column_name: time_column # (1)!
            model_two:
              +time_column_name: time_column_name_in_model_two
    # ...
    ```

    1.  While you can set the `hypertable` materialization for multiple models, you'll still have to configure the `time_column_name` for each model individually.

## Configuration options

### dbt-specific options

The following options are not taken from the TimescaleDB APIs, but are specific to this adapter.

* `empty_hypertable`: If set to `true`, the hypertable will be truncated right after creation (as a regular table) and right before converting it into a hypertable. Defaults to `false`.

### TimescaleDB hypertable options

All [TimescaleDB hypertable configuration options](https://docs.timescale.com/api/latest/hypertable/create_hypertable/#optional-arguments) as of version 2.12 are supported through model configuration as well:

* `time_column_name`
* `partitioning_column`
* `number_partitions`
* `chunk_time_interval` (interval - required if time column is not a timestamp)
* `create_default_indexes` (boolean)
* `partitioning_func`
* `associated_schema_name`
* `associated_table_prefix`
* `time_partitioning_func`
* `replication_factor`
* `data_nodes` (list of strings)
* `distributed` (boolean)

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/api/latest/hypertable/create_hypertable/#optional-arguments) for more information regarding these options.

### set_integer_now_func options

The following 2 options are available for hypertables where the time column is not a timestamp:

* `integer_now_func` (string): name of a function to be used to generate the current time as an integer.
* `integer_now_func_sql` (string, optional): SQL code for the function mentioned above. If provided, the function with the name set in `integer_now_func` will be created. If not provided, an error will be thrown if the function does not exist already.

!!! tip "Use a macro"
    You could also call a macro for your `integer_now_func_sql`.

!!! tip "Idempotent"
    The `integer_now_func_sql` is idempotent and will replace an existing function if a function with the given name already exists. So while it may cause some overhead during the dbt run, it doesn't matter if you share this config across multiple models.

!!! tip "The name is enough"
    You don't have to provide the SQL code for the function if you already have a function with the name set in `integer_now_func` in your database. You could create the function once in a single model or with `dbt run-operation` and then reuse it in all other models.

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/api/latest/hypertable/set_integer_now_func/) for more information regarding this functionality.

```sql+jinja title="models/my_hypertable.sql"
{{
  config(
    materialized='hypertable',
    time_column_name='time_column',
    chunk_time_interval="interval '1 day'",
    integer_now_func='my_hypertable_int_to_now',
    integer_now_func_sql='select extract(epoch from now())::bigint'
  )
}}
select 1::bigint as time_column
```

### Dimension options

You can add dimensions to a hypertable.

!!! warning "Empty hypertable required"
    You can only add dimensions to an empty hypertable. Therefore, you'll have to set `empty_hypertable` to `true` as well.

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/api/latest/hypertable/add_dimension/) for more information regarding dimensions.

=== "SQL"

    ```sql+jinja hl_lines="5" title="models/my_hypertable.sql"
    {{ config(
        materialized = 'hypertable',
        time_column_name = 'time_column',
        dimensions=[
          {"column_name": "id", "number_partitions": 5},
          {"column_name": "col_1", "chunk_time_interval": 10000},
          {"column_name": "another_column"}
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
          +time_column_name: time_column
          +dimensions:
            - column_name: id
              number_partitions: 5
            - column_name: another_time_column
              chunk_time_interval: interval '1 day'
    # ...
    ```

Dimensions are a list. Every dimension can have the following configuration options:

* `column`
* `number_partitions`
* `chunk_time_interval`
* `partitioning_func`
