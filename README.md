![dbt logo for light mode](https://raw.githubusercontent.com/sdebruyn/dbt-timescaledb/main/assets/dbt-signature_tm.png#gh-light-mode-only)
![dbt logo for dark mode](https://raw.githubusercontent.com/sdebruyn/dbt-timescaledb/main/assets/dbt-signature_tm_light.png#gh-dark-mode-only)
![timescale logo for light mode](https://raw.githubusercontent.com/sdebruyn/dbt-timescaledb/main/assets/Timescale-Logo-Black-PNG.png#gh-light-mode-only)
![timescale logo for dark mode](https://raw.githubusercontent.com/sdebruyn/dbt-timescaledb/main/assets/Timescale-Logo-Primary-PNG.png#gh-dark-mode-only)

[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm-project.org)
[![PyPI - Version](https://img.shields.io/pypi/v/dbt-timescaledb)](https://pypi.org/project/dbt-timescaledb/)
[![PyPI - License](https://img.shields.io/pypi/l/dbt-timescaledb)](https://github.com/sdebruyn/dbt-timescaledb/blob/main/LICENSE)
[![tests](https://github.com/sdebruyn/dbt-timescaledb/actions/workflows/test.yml/badge.svg)](https://github.com/sdebruyn/dbt-timescaledb/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/sdebruyn/dbt-timescaledb/badge.svg?branch=main)](https://coveralls.io/github/sdebruyn/dbt-timescaledb?branch=main)

**[dbt](https://www.getdbt.com/)** enables data analysts and engineers to transform their data using the same practices that software engineers use to build applications.

dbt is the T in ELT. Organize, cleanse, denormalize, filter, rename, and pre-aggregate the raw data in your warehouse so that it's ready for analysis.

## TimescaleDB

**[Timescale](https://www.timescale.com/)** extends PostgreSQL for all of your resource-intensive production workloads, so you can build faster, scale further, and stay under budget.

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

Since hypertables make more sense as empty tables in which you insert data, you can also set the configuration option `empty_hypertable` (`false` by default) which will truncate the data right after creating the table and right before converting it into a hypertable.

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
    compression={
      after='1 day',
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

The following compression options ([docs for compression](https://docs.timescale.com/api/latest/compression/alter_table_compression/) and docs for [compression policy](https://docs.timescale.com/api/latest/compression/add_compression_policy/#add_compression_policy)) are supported:

* `orderby` (string)
* `segmentby` (list of strings)
* `chunk_time_interval` (the actual interval, not prefixed with "interval")
* `after` (interval or integer depending on your time column): **required**
* `schedule_interval` (interval)
* `initial_start`
* `timezone`

### Transaction per chunk indexes

You can create [transaction per chunk indexes](https://docs.timescale.com/api/latest/hypertable/create_index/) by setting the optional boolean `transaction_per_chunk` in the [index configuration](https://docs.getdbt.com/reference/resource-configs/postgres-configs#indexes), similar to the `unique` setting.

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

* Continuous aggregate policies
* Continuous aggregate compression

## License

MIT License. See [LICENSE](https://dbt-timescaledb.debruyn.dev/license/) for full details.

## Code of Conduct

Everyone interacting in the dbt project's codebases, issue trackers, chat rooms, and mailing lists is expected to follow the [dbt Code of Conduct](https://community.getdbt.com/code-of-conduct).
