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

{%- macro timescaledb__update_indexes_on_virtual_hypertable(relation, index_changes) -%}
    {%- for _index_change in index_changes -%}
        {%- set _index = _index_change.context -%}

        {%- if _index_change.action == "drop" -%}
            {{ postgres__get_drop_index_sql(relation, _index.name) }};

        {%- elif _index_change.action == "create" -%}
            {{ postgres__get_create_index_sql(relation, _index.as_node_config) }}

        {%- endif -%}

    {%- endfor -%}

{%- endmacro -%}

{% macro describe_hypertable(relation) %}
    {% set _indexes = run_query(get_show_indexes_sql(relation)) %}
    {% do return({'indexes': _indexes}) %}
{% endmacro %}

{% macro get_virtual_hypertable_change_collection(existing_relation, new_config) %}
    {% set _existing_hypertable = describe_hypertable(existing_relation) %}
    {% set _change_collection = existing_relation.get_hypertable_config_change_collection(_existing_hypertable, new_config.model) %}
    {% do return(_change_collection) %}
{% endmacro %}

{% macro set_chunk_time_interval(relation, chunk_time_interval, dimension_name = none) %}
  select set_chunk_time_interval('{{ relation }}', {{ chunk_time_interval }}
    {%- if dimension_name %}
      , dimension_name => '{{ dimension_name }}'
    {%- endif %}
  );
{% endmacro %}
