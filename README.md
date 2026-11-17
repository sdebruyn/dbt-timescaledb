# dbt-timescaledb

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/sdebruyn/dbt-timescaledb/main/assets/dbt-signature_tm_light.png">
  <img alt="dbt logo" src="https://raw.githubusercontent.com/sdebruyn/dbt-timescaledb/main/assets/dbt-signature_tm.png">
</picture>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/sdebruyn/dbt-timescaledb/main/assets/Timescale-Logo-Primary-PNG.png">
  <img alt="timescale logo" src="https://raw.githubusercontent.com/sdebruyn/dbt-timescaledb/main/assets/Timescale-Logo-Black-PNG.png">
</picture>

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![PyPI - Version](https://img.shields.io/pypi/v/dbt-timescaledb)](https://pypi.org/project/dbt-timescaledb/)
[![PyPI - License](https://img.shields.io/pypi/l/dbt-timescaledb)](https://github.com/sdebruyn/dbt-timescaledb/blob/main/LICENSE)
[![tests](https://github.com/sdebruyn/dbt-timescaledb/actions/workflows/test.yml/badge.svg)](https://github.com/sdebruyn/dbt-timescaledb/actions/workflows/test.yml)
[![codecov](https://codecov.io/github/sdebruyn/dbt-timescaledb/graph/badge.svg?token=7SLONAKRMD)](https://codecov.io/github/sdebruyn/dbt-timescaledb)

**[dbt](https://www.getdbt.com/)** enables data analysts and engineers to transform their data using the same practices that software engineers use to build applications.

dbt is the T in ELT. Organize, cleanse, denormalize, filter, rename, and pre-aggregate the raw data in your warehouse so that it's ready for analysis.

## TimescaleDB

**[Timescale](https://www.timescale.com/)** extends PostgreSQL for all of your resource-intensive production workloads, so you can build faster, scale further, and stay under budget.

## Supported versions

| Adapter versions  | Supported dbt versions | Supported TimescaleDB versions |
| ----------------- | ---------------------- | ------------------------------ |
| 1.7.0a1 - 1.7.0a7 | 1.7.x                  | 2.12 - latest                  |
| 1.8.0a1 - 1.8.0a2 | 1.8.x - latest         | 2.12 - latest                  |
| 1.8.0a3 - 1.8.x   | 1.8.x - latest         | 2.13 - latest                  |
| 1.12.0 - latest   | 1.12.x - latest        | 2.13 - latest                  |

The recommended versions of Timescale are TimescaleDB Community Edition or Timescale cloud. It is not recommended to use this adapter with TimescaleDB Apache 2 Edition. See the [TimescaleDB editions](https://docs.timescale.com/about/latest/timescaledb-editions/) page for more information.

## Features & documentation

[Read the documentation](https://dbt-timescaledb.debruyn.dev/) ([installation](https://dbt-timescaledb.debruyn.dev/installation/) | [usage](https://dbt-timescaledb.debruyn.dev/usage/)) for more information.

## Development

Create the development environment with `uv sync --group test`, then run the checks:

```shell
uv lock --check
uv run pre-commit run --all-files
uv run pre-commit run ruff --all-files
uv run pre-commit run ruff-format --all-files
uv run pytest --cov=dbt
```

## Code of Conduct

Both dbt Labs and Timescale have published a code of conduct. Everyone interacting in this project's codebases, issues, discussions, and related Slack channels is expected to follow the [dbt Code of Conduct](https://docs.getdbt.com/community/resources/code-of-conduct) and the [Timescale Code of Conduct](https://www.timescale.com/code-of-conduct).
