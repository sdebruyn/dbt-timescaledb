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

{% macro add_refresh_policy(relation, refresh_config) %}
  select add_continuous_aggregate_policy('{{ relation }}',
    start_offset => {{ refresh_config.start_offset }},
    end_offset => {{ refresh_config.end_offset }},

    {%- if refresh_config.schedule_interval %}
        schedule_interval => {{ refresh_config.schedule_interval }},
    {% endif -%}

    {%- if refresh_config.initial_start %}
        initial_start => {{ refresh_config.initial_start }},
    {% endif -%}

    {%- if refresh_config.timezone %}
        timezone => '{{ refresh_config.timezone }}',
    {% endif -%}

    if_not_exists => true);
{% endmacro %}

{% macro clear_refresh_policy(relation) %}
  select remove_continuous_aggregate_policy('{{ relation }}', if_exists => true);
{% endmacro %}
