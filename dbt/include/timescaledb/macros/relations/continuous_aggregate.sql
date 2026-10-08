{% macro do_refresh_continuous_aggregate(relation) %}
  {% call statement('refresh', fetch_result=False, auto_begin=False) %}
    {%- set end_offset = config.get('refresh_policy', {}).get('end_offset') -%}
    {{ adapter.marker_run_outside_transaction() }}
    call refresh_continuous_aggregate('{{ relation }}', null, {{ end_offset or 'null' }});
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

{#- The indexes of a continuous aggregate sit on its materialization hypertable -#}
{% macro timescaledb__get_show_indexes_sql(relation) %}
  {%- set _hypertable_sql -%}
    select materialization_hypertable_schema, materialization_hypertable_name
    from timescaledb_information.continuous_aggregates
    where view_schema = '{{ relation.schema }}' and view_name = '{{ relation.identifier }}'
  {%- endset -%}
  {%- set _hypertable = run_query(_hypertable_sql) if execute else none -%}

  {%- if _hypertable and _hypertable.rows -%}
    {%- set _schema = _hypertable.rows[0][0] -%}
    {%- set _name = _hypertable.rows[0][1] -%}
    {#- TimescaleDB names its own indexes after the materialization hypertable -#}
    select *
    from ({{ postgres__get_show_indexes_sql(relation.incorporate(path={"schema": _schema, "identifier": _name})) }}) _indexes
    where name not like '{{ _name }}%'
  {%- else -%}
    {{ postgres__get_show_indexes_sql(relation) }}
  {%- endif -%}
{% endmacro %}
