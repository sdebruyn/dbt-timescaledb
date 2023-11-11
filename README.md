<p align="center">
  <img src="https://raw.githubusercontent.com/dbt-labs/dbt/ec7dee39f793aa4f7dd3dae37282cc87664813e4/etc/dbt-logo-full.svg" alt="dbt logo" width="300"/>
  <img src="https://avatars.githubusercontent.com/u/8986001?s=200&v=4" alt="timescale logo" width="100"/>
</p>

[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm-project.org)
[![PyPI - Version](https://img.shields.io/pypi/v/dbt-timescaledb)](https://pypi.org/project/dbt-timescaledb/)
[![PyPI - License](https://img.shields.io/pypi/l/dbt-timescaledb)](https://github.com/sdebruyn/dbt-timescaledb/blob/main/LICENSE)
[![tests](https://github.com/sdebruyn/dbt-timescaledb/actions/workflows/test.yml/badge.svg)](https://github.com/sdebruyn/dbt-timescaledb/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/sdebruyn/dbt-timescaledb/badge.svg?branch=main)](https://coveralls.io/github/sdebruyn/dbt-timescaledb?branch=main)

**[dbt](https://www.getdbt.com/)** enables data analysts and engineers to transform their data using the same practices that software engineers use to build applications.

dbt is the T in ELT. Organize, cleanse, denormalize, filter, rename, and pre-aggregate the raw data in your warehouse so that it's ready for analysis.

## TimescaleDB

[Timescale](https://www.timescale.com/) extends PostgreSQL for all of your resource-intensive production workloads, so you can build faster, scale further, and stay under budget.

## dbt-timescaledb features & documentation

### Installation

Install the package using pip:

```bash
pip install dbt-timescaledb
```

In your `profiles.yml`, use the same configuration [as you'd do for a regular PostgreSQL database](https://docs.getdbt.com/docs/core/connect-data-platform/postgres-setup#profile-configuration). The only difference is that you need to set the `type` to `timescaledb`.

```yaml
company-name:
  target: dev
  outputs:
    dev:
      type: timescaledb # only option different from regular dbt-postgres
      host: [hostname]
      user: [username]
      password: [password]
      port: [port]
      dbname: [database name]
      schema: [dbt schema]
      # see dbt-postgres docs linked above for more options
```

### Hypertables

You can materialize your models as [hypertables](https://docs.timescale.com/use-timescale/latest/hypertables/about-hypertables/). The `hypertable` materialization requires you to set the `time_column_name` configuration option in your models. This will create a hypertable in TimescaleDB.

```sql
{{
  config(
    materialized='hypertable',
    time_column_name='time_column'
  )
}}
select current_timestamp as time_column
```

As with any dbt model configuration, you can also set this in YAML ([docs](https://docs.getdbt.com/reference/model-configs)):

```yaml
models:
  your_project_name:
    folder_containing_the_hypertables:
      +materialized: hypertable
        model_one:
          +time_column_name: time_column
        model_two:
          +time_column_name: time_column_name_in_model_two
# ...
```

All [other TimescaleDB hypertable configuration options](https://docs.timescale.com/api/latest/hypertable/create_hypertable/#optional-arguments) are supported through model configuration as well:

* `time_column_name`
* `partitioning_column`
* `number_partitions`
* `chunk_time_interval`
* `create_default_indexes` (boolean)
* `partitioning_func`
* `associated_schema_name`
* `associated_table_prefix`
* `time_partitioning_func`
* `replication_factor`
* `data_nodes` (list of strings)
* `distributed` (boolean)

### Hypertable compression

You can also configure [hypertable compression](https://docs.timescale.com/use-timescale/latest/compression/about-compression/) options:

```sql
{{
  config(
    materialized='hypertable',
    time_column_name='time_column',
    compression=True
  )
}}
select current_timestamp as time_column
```

or in YAML:

```yaml
models:
  your_project_name:
    folder_containing_the_hypertables:
      +materialized: hypertable
# ...
```

or

```sql
{{
  config(
    materialized='hypertable',
    time_column_name='time_column',
    compression={
      chunk_time_interval='1 day',
    }
  )
}}
select current_timestamp as time_column
```

or YAML examples:

```yaml
models:
  your_project_name:
    folder_containing_the_hypertables:
      +materialized: hypertable
      +compression: false # same as leaving this out, default value
        model_one:
          +time_column_name: time_column
          +compression: true
        model_two:
          +time_column_name: time_column_name_in_model_two
          +compression:
            chunk_time_interval: '1 day'
            orderby: 'another_column'
            segmentby: ['column_one', 'column_two']
# ...
```

The following compression options are supported:

* `orderby` (string)
* `segmentby` (list of strings)
* `chunk_time_interval` (the actual interval, not prefixed with "interval")

### Continuous aggregates

There is support for `continuous_aggregate` materialization. This materialization will create a continuous aggregate in TimescaleDB.

```sql
{{
  config(
    materialized='continuous_aggregate',
  )
}}
select
    count(*),
    time_bucket(interval '1 day', time_column) as bucket
from {{ ref('a_hypertable') }}
group by 2
```

### More

Feel free to request things you're interested in by creating an [issue](https://github.com/sdebruyn/dbt-timescaledb/issues).

The following things are planned:

- [x] Basic hypertable support
- [x] Basic continuous aggregate support
- [ ] Configure continuous aggregate policies through dbt

## License

MIT License. See [LICENSE](LICENSE) for full details.

## Code of Conduct

Everyone interacting in the dbt project's codebases, issue trackers, chat rooms, and mailing lists is expected to follow the [dbt Code of Conduct](https://community.getdbt.com/code-of-conduct).
