### chunk_time_interval

The `chunk_time_interval` config option allows you to set the interval at which TimescaleDB will chunk your (virtual) hypertable. This is useful for optimizing query performance and storage efficiency. The default value is `1 week`.

Note that the type of the interval depends on the type of your time column and has to match.

```sql+jinja title="models/my_hypertable.sql"
{{
  config(
    materialized='hypertable',
    main_dimension='time_column',
    chunk_time_interval="interval '1 day'"
  )
}}
