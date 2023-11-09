<p align="center">
  <img src="https://raw.githubusercontent.com/dbt-labs/dbt/ec7dee39f793aa4f7dd3dae37282cc87664813e4/etc/dbt-logo-full.svg" alt="dbt logo" width="300"/>
  <img src="https://avatars.githubusercontent.com/u/8986001?s=200&v=4" alt="timescale logo" width="100"/>
</p>

[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm-project.org)
[![PyPI - Version](https://img.shields.io/pypi/v/dbt-timescaledb)](https://pypi.org/project/dbt-timescaledb/)
[![PyPI - License](https://img.shields.io/pypi/l/dbt-timescaledb)](https://github.com/sdebruyn/dbt-timescaledb/blob/main/LICENSE)
[![tests](https://github.com/sdebruyn/dbt-timescaledb/actions/workflows/test.yml/badge.svg)](https://github.com/sdebruyn/dbt-timescaledb/actions/workflows/test.yml)

**[dbt](https://www.getdbt.com/)** enables data analysts and engineers to transform their data using the same practices that software engineers use to build applications.

dbt is the T in ELT. Organize, cleanse, denormalize, filter, rename, and pre-aggregate the raw data in your warehouse so that it's ready for analysis.

## TimescaleDB

[Timescale](https://www.timescale.com/) extends PostgreSQL for all of your resource-intensive production workloads, so you can build faster, scale further, and stay under budget.

## dbt-timescaledb features

### Hypertables

You can materialize your models as hypertables. The `hypertable` materialization requires you to set a `time_column_name` configuration option in your models. This will create a hypertable in TimescaleDB.

```sql
{{
  config(
    materialized='hypertable',
    time_column_name='time_column'
  )
}}
select current_timestamp as time_column
```

### Continuous aggregates

There is support for a `continuous_aggregate` materialization. This materialization will create a continuous aggregate in TimescaleDB.

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

## Reporting bugs and contributing code

- Want to report a bug or request a feature? Let us know on [Slack](http://community.getdbt.com/), or open [an issue](https://github.com/sdebruyn/dbt-timescaledb/issues)
- Want to help us build dbt? Check out the [Contributing Guide](https://github.com/dbt-labs/dbt/blob/HEAD/CONTRIBUTING.md)

## Code of Conduct

Everyone interacting in the dbt project's codebases, issue trackers, chat rooms, and mailing lists is expected to follow the [dbt Code of Conduct](https://community.getdbt.com/code-of-conduct).
