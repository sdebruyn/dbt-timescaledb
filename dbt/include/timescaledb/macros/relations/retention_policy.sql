{% macro add_retention_policy(relation, retention_config) %}
  select add_retention_policy(
    '{{ relation }}',
    {{ retention_config.drop_after }},

    {%- if retention_config.schedule_interval %}
        schedule_interval => {{ retention_config.schedule_interval }},
    {% endif -%}

    {%- if retention_config.initial_start %}
        initial_start => {{ retention_config.initial_start }},
    {% endif -%}

    {%- if retention_config.timezone %}
        timezone => '{{ retention_config.timezone }}',
    {% endif -%}

    if_not_exists => true);
{% endmacro %}

{% macro clear_retention_policy(relation) %}
  select remove_retention_policy('{{ relation }}', if_exists => true);
{% endmacro %}
