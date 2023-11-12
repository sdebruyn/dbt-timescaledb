# Installation

Install the package using pip:

```bash
pip install dbt-timescaledb
```

In your `profiles.yml`, use the same configuration [as you'd do for a regular PostgreSQL database](https://docs.getdbt.com/docs/core/connect-data-platform/postgres-setup#profile-configuration). The only difference is that you need to set the `type` to `timescaledb`.

```yaml hl_lines="5" title="profiles.yml"
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
