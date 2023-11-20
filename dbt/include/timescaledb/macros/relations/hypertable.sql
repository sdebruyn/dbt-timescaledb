{% macro get_create_hypertable_as_sql(relation) %}
  {% set time_column_name = config.get("time_column_name") %}
  {% if not time_column_name %}
    {{ exceptions.raise_compiler_error("The configuration option time_column_name is required for hypertables.") }}
  {% endif %}

  select create_hypertable(
    '{{ relation }}',
    '{{ time_column_name }}',

    {%- if config.get('partitioning_column') %}
      partition_column => '{{ config.get("partitioning_column") }}',
    {% endif -%}

    {%- if config.get('number_partitions') %}
      number_partitions => {{ config.get('number_partitions') }},
    {% endif -%}

    {%- if config.get('chunk_time_interval') %}
      chunk_time_interval => {{ config.get('chunk_time_interval') }},
    {% endif -%}

    {%- if config.get('create_default_indexes') is not none %}
      create_default_indexes => {{ config.get('create_default_indexes') }},
    {% endif -%}

    {%- if config.get('partitioning_func') %}
      partitioning_func => '{{ config.get("partitioning_func") }}',
    {% endif -%}

    {%- if config.get('associated_schema_name') %}
      associated_schema_name => '{{ config.get("associated_schema_name") }}',
    {% endif -%}

    {%- if config.get('associated_table_prefix') %}
      associated_table_prefix => '{{ config.get("associated_table_prefix") }}',
    {% endif -%}

    {%- if config.get('time_partitioning_func') %}
      time_partitioning_func => '{{ config.get("time_partitioning_func") }}',
    {% endif -%}

    {%- if config.get('replication_factor') %}
      replication_factor => {{ config.get('replication_factor') }},
    {% endif -%}

    {%- if config.get('data_nodes') %}
      data_nodes => '{"{{ config.get("data_nodes")|join("\", \"") }}"}',
    {% endif -%}

    {%- if config.get('distributed') %}
      distributed => {{ config.get('distributed') }},
    {% endif -%}

    if_not_exists => false, {# Users should not be concerned with this #}
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

{% macro create_dimensions(relation) %}
  {%- set _dimensions = config.get('dimensions', default=[]) -%}
  {% for _dimension in _dimensions %}
    {% set create_dimension_sql = add_dimension(relation, _dimension) %}
    {% do run_query(create_dimension_sql) %}
  {% endfor %}
{% endmacro %}

{% macro add_dimension(relation, dimension_config) %}
  select add_dimension(
    '{{ relation }}',
    '{{ dimension_config.column_name }}',

    {%- if dimension_config.number_partitions %}
      number_partitions => {{ dimension_config.number_partitions }},
    {% endif -%}

    {%- if dimension_config.chunk_time_interval %}
      chunk_time_interval => {{ dimension_config.chunk_time_interval }},
    {% endif -%}

    {%- if dimension_config.partitioning_func %}
      partitioning_func => '{{ dimension_config.partitioning_func }}',
    {% endif -%}

    if_not_exists => true);
{% endmacro %}
