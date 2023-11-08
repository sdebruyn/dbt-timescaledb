{% macro get_create_continuous_aggregate_as_sql(relation, sql) %}
    create materialized view if not exists {{ relation }} with (timescaledb.continuous) as {{ sql }};

    {% for _index_dict in config.get('indexes', []) -%}
        {{- get_create_index_sql(relation, _index_dict) -}}
    {%- endfor -%}

{% endmacro %}
