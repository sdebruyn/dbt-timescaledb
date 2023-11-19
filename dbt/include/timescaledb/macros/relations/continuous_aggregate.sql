{% macro do_refresh_continuous_aggregate(relation) %}
  {% call statement('refresh', fetch_result=False, auto_begin=False) %}
    {{ adapter.marker_run_outside_transaction() }}
    call refresh_continuous_aggregate('{{ relation }}', null, null);
  {% endcall %}
{% endmacro %}

{% macro get_create_continuous_aggregate_as_sql(relation, sql) %}
  create materialized view if not exists {{ relation }}
  with (
    timescaledb.continuous

    {%- if config.get('materialized_only') %}
      ,timescaledb.materialized_only = {{ config.get("materialized_only") }}
    {% endif -%}

    {%- if config.get('create_group_indexes') %}
      ,timescaledb.create_group_indexes = {{ config.get("create_group_indexes") }}
    {% endif -%}

    ) as {{ sql }}
  with no data;
{% endmacro %}
