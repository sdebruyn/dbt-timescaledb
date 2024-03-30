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

{% macro clear_reorder_policy(relation) %}
  select remove_reorder_policy('{{ relation }}', if_exists => true);
{% endmacro %}
