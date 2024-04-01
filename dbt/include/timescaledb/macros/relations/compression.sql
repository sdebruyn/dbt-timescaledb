{% macro set_compression(relation, compression_config) %}
  {%- if relation.is_materialized_view -%}
    {%- set relation_type = "materialized view" -%}
  {%- elif relation.is_table -%}
    {%- set relation_type = "table" -%}
  {%- else -%}
    {{ exceptions.raise_compiler_error("Cannot enable compression on a " ~ relation.type) }}
  {%- endif -%}

  {% set bool_compression = compression_config is not none %}

  alter {{ relation_type }} {{ relation }} set (
    timescaledb.compress = {{ bool_compression }}

    {%- if compression_config and compression_config.orderby %}
        ,timescaledb.compress_orderby = '{{ compression_config.orderby }}'
    {% endif -%}

    {%- if compression_config and compression_config.segmentby %}
        ,timescaledb.compress_segmentby = '{{ compression_config.segmentby | join(",") }}'
    {% endif -%}

    {%- if compression_config and compression_config.chunk_time_interval %}
        ,timescaledb.compress_chunk_time_interval = '{{ compression_config.chunk_time_interval }}'
    {% endif -%}
  );
{% endmacro %}

{% macro add_compression_policy(relation, compression_config) %}
  select add_compression_policy(
    '{{ relation }}',
    {{ compression_config.after }},

    {%- if compression_config.schedule_interval %}
        schedule_interval => {{ compression_config.schedule_interval }},
    {% endif -%}

    {%- if compression_config.initial_start %}
        initial_start => {{ compression_config.initial_start }},
    {% endif -%}

    {%- if compression_config.timezone %}
        timezone => '{{ compression_config.timezone }}',
    {% endif -%}

    if_not_exists => true);
{% endmacro %}

{% macro clear_compression_policy(relation) %}
  select remove_compression_policy('{{ relation }}', if_exists => true);
{% endmacro %}
