# Virtual hypertables

[Hypertables](https://docs.timescale.com/use-timescale/latest/hypertables/about-hypertables/) are usually used to ingest time-series data. They are a high-performance version of regular Postgres tables focussed on time-based bucketting, chunking, and partitioning.

Hypertables by themselves don't make a lot of sense in dbt as you'd create them outside of dbt and then ingest data into them. With virtual hypertables, we can leverage pre-existing hypertables and use dbt to manage their configuration.

!!! info
    Consult the [Timescale docs](https://docs.timescale.com/use-timescale/latest/hypertables/about-hypertables/) for more information regarding hypertables.

!!! danger "Work in progress"
    This feature is still a work in progress. Testing and documentation has not been completed yet. Use at your own risk.

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

At the moment, only [compression](../usage/compression.md) has been tested and verified to work. Other features are already implemented but require testing and documentation.
