### set_integer_now_func options

The following 2 options are available for (virtual) hypertables where the time column is not a timestamp:

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
    main_dimension='time_column',
    integer_now_func='my_hypertable_int_to_now',
    integer_now_func_sql='select extract(epoch from now())::bigint'
  )
}}
select 1::bigint as time_column
```
