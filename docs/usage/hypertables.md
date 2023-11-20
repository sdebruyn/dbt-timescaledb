# Hypertables

[Hypertables](https://docs.timescale.com/use-timescale/latest/hypertables/about-hypertables/) are usually used to ingest time-series data. They are a high-performance version of regular Postgres tables focussed on time-based bucketting, chunking, and partitioning.

Hypertables make less sense as dbt models to store transformed data. However, you can still use them as such. A more useful version right now is the `empty` option, which will create empty hypertables.

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

## :thinking: Ideas

dbt could still be useful to manage hypertables and their policies. Here are a few ideas of features we could implement in the future to make this process easier.

### Leverage sources

You probably will want to expose your hypertables to dbt as [sources](https://docs.getdbt.com/docs/build/sources) since they are meant for data ingestion, not for data tranformation. We could maybe add all required configuration options to the `source` properties and then leverage that to manage the policies on the hypertable or even to initially create the hypertable itself.

### :heart_eyes: Virtual table

The problem with the sources above however is that the new [dbt contract](https://docs.getdbt.com/docs/collaborate/govern/model-contracts) features defining the schema are only available for models. Therefore, we could create a virtual version of this materialization which only sets all policies and updates the schema. This would probably feel more native in dbt as you could leverage its extensive configuration options and the schema defined in the contract.
