{% macro get_create_hypertable_as_sql(relation) %}
  {% set main_dimension = config.get("main_dimension") %}
  {% if not main_dimension %}
    {{ exceptions.raise_compiler_error("The configuration option main_dimension is required for hypertables.") }}
  {% endif %}

  select create_hypertable(
    '{{ relation }}',
    {{ parse_dimension_config(main_dimension) }},

    {%- if config.get('create_default_indexes') is not none %}
      create_default_indexes => {{ config.get('create_default_indexes') }},
    {% endif -%}

    migrate_data => true {# Required since dbt models will always contain data #}
  );
{% endmacro %}

{% macro add_reorder_policy(relation, reorder_config) %}
  {%- set index_dict = reorder_config.index -%}
  {%- set index_config = adapter.parse_index(index_dict) -%}
  {%- set index_name = index_config.render(relation) -%}

  {%- if reorder_config.create_index is none or reorder_config.create_index %}
    {{ get_create_index_sql(relation, index_dict) }}
  {% endif -%}

  select add_reorder_policy('{{ relation }}', '{{ index_name }}',

    {%- if reorder_config.initial_start %}
        initial_start => '{{ reorder_config.initial_start }}',
    {% endif -%}

    {%- if reorder_config.timezone %}
        timezone => '{{ reorder_config.timezone }}',
    {% endif -%}

    if_not_exists => true
  );
{% endmacro %}

{% macro set_integer_now_func(relation, integer_now_func, integer_now_func_sql = none) %}
  {% if integer_now_func_sql %}
    create or replace function {{ integer_now_func }}() returns bigint language sql immutable as $$
      {{ integer_now_func_sql }}
    $$;
  {% endif %}
  select set_integer_now_func('{{ relation }}', '{{ integer_now_func }}');
{% endmacro %}
