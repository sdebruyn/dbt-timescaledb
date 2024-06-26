# Virtual hypertables

[Hypertables](https://docs.timescale.com/use-timescale/latest/hypertables/about-hypertables/) are usually used to ingest time-series data. They are a high-performance version of regular Postgres tables focussed on time-based bucketting, chunking, and partitioning.

Hypertables by themselves don't make a lot of sense in dbt as you'd create them outside of dbt and then ingest data into them. With virtual hypertables, we can leverage pre-existing hypertables and use dbt to manage their configuration.

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/use-timescale/latest/hypertables/about-hypertables/) for more information regarding hypertables.

!!! warning "Existing configurations"
    As soon as you start to manage a hypertable as a virtual hypertable with dbt-timescaledb, dbt will replace existing configurations on every run. This includes the retention policy, compression, and other settings. If you have existing configurations in place, you have to make sure to adjust the dbt configuration accordingly.

## Usage

The hypertable has to pre-exist in your database. If the hypertable is not present, dbt will throw an error. Optionally, you can specify dbt's built-in `schema` parameter to reference a hypertable in a different schema.

The SQL code in the dbt model does not matter and will be fully ignored. However, dbt will ignore empty models. You could just put `--` in the model to make it non-empty.

=== "SQL"

    ```sql+jinja hl_lines="3" title="models/existing_hypertable.sql"
    {{
      config(
        materialized='virtual_hypertable'
      )
    }}
    --
    ```

=== "YAML"

    ```yaml hl_lines="4" title="dbt_project.yml"
    models:
      your_project_name:
        folder_containing_the_hypertables:
          +materialized: virtual_hypertable
    # ...
    ```

## Configuration options

Dimensions are not supported for virtual hypertables as you can only set them during the creation of the hypertable.

You can use virtual hypertables to manage [compression](compression.md), indexes, set a [reorder policy](reorder-policies.md), define [retention policies](retention-policies.md), or any of the options below.

--8<-- "docs_build/integer_now_func.md"

--8<-- "docs_build/chunk_time_interval.md"
