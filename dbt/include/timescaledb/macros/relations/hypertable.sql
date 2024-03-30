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
