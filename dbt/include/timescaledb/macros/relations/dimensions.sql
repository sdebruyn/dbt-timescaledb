{% macro create_dimensions(relation) %}
  {%- set _dimensions = config.get('dimensions', default=[]) -%}
  {% for _dimension in _dimensions %}
    {% set create_dimension_sql = add_dimension(relation, _dimension) %}
    {% do run_query(create_dimension_sql) %}
  {% endfor %}
{% endmacro %}

{% macro add_dimension(relation, dimension_config) %}
  select add_dimension('{{ relation }}', {{ parse_dimension_config(dimension_config) }});
{% endmacro %}

{% macro parse_dimension_config(config_object) %}
  {#
    Example config objects:

    some_by_range_dimension = {
        "column_name": "the name of the column",
        "type": "by_range",
        "partition_interval": "interval '1 day'",
        "partition_func": "the name of the function"
    }

    or the shorthand version with just the name of the column for a by_range

    some_by_hash_dimension = {
        "column_name": "the name of the column",
        "type": "by_hash",
        "number_partitions": 123,
        "partition_func": "the name of the function"
    }

  #}

  {% if config_object is string %}
    {% set dimension_config = {"column_name": config_object} %}
  {% else %}
    {% set dimension_config = config_object %}
  {% endif %}

  {{- dimension_config.type|default('by_range') }}('{{ dimension_config.column_name }}'
  {%- if dimension_config.number_partitions %}
      , number_partitions => {{ dimension_config.number_partitions }}
    {% endif -%}
    {%- if dimension_config.partition_interval %}
      , partition_interval => {{ dimension_config.partition_interval }}
    {% endif -%}
    {%- if dimension_config.partition_func %}
      , partition_func => '{{ dimension_config.partition_func }}'
    {% endif -%}
  )

{% endmacro %}
