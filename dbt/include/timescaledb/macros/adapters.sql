{% macro timescaledb__get_create_index_sql(relation, index_dict) -%}
  {%- set index_config = adapter.parse_index(index_dict) -%}
  {%- set comma_separated_columns = ", ".join(index_config.columns) -%}
  {%- set index_name = index_config.render(relation) -%}

  create {% if index_config.unique -%}
    unique
  {%- endif %} index if not exists
  "{{ index_name }}"
  on {{ relation }} {% if index_config.type -%}
    using {{ index_config.type }}
  {%- endif %}
  ({{ comma_separated_columns }})
  {%- if index_config.transaction_per_type %}
    with (timescaledb.transaction_per_chunk)
  {% endif -%};
{%- endmacro %}

{# TODO: log an issue in dbt-core as this should probably be the default impl #}
{% macro timescaledb__rename_relation(from_relation, to_relation) -%}
  {% set target_name = adapter.quote_as_configured(to_relation.identifier, 'identifier') %}
  {{ log('from_relation: ' ~ from_relation, info=True) }}
  {% call statement('rename_relation') -%}
    {{ get_rename_sql(from_relation, target_name) }}
  {%- endcall %}
{% endmacro %}
