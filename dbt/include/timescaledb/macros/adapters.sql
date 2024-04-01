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

{# https://github.com/dbt-labs/dbt-core/issues/9124 #}
{% macro timescaledb__rename_relation(from_relation, to_relation) -%}
  {% set target_name = adapter.quote_as_configured(to_relation.identifier, 'identifier') %}
  {% call statement('rename_relation') -%}
    {{ get_rename_sql(from_relation, target_name) }};
  {%- endcall %}
{% endmacro %}

{# Continuous aggregates are seen as views instead of materialized views, fixing this below #}
{% macro timescaledb__list_relations_without_caching(schema_relation) %}
  {% call statement('list_relations_without_caching', fetch_result=True) -%}
    with
    continuous_aggregates as (
      select
        view_name as name,
        view_schema as schema
      from timescaledb_information.continuous_aggregates
      where view_schema ilike '{{ schema_relation.schema }}'
    ),
    views_without_continuous_aggregates as (
      select
        viewname as name,
        schemaname as schema
      from pg_views
      where schemaname ilike '{{ schema_relation.schema }}'
      except all
      select * from continuous_aggregates
    )
    select
      '{{ schema_relation.database }}' as database,
      *,
      'materialized_view' as type
    from continuous_aggregates
    union all
    select
      '{{ schema_relation.database }}' as database,
      tablename as name,
      schemaname as schema,
      'table' as type
    from pg_tables
    where schemaname ilike '{{ schema_relation.schema }}'
    union all
    select
      '{{ schema_relation.database }}' as database,
      name,
      schema,
      'view' as type
    from views_without_continuous_aggregates
    union all
    select
      '{{ schema_relation.database }}' as database,
      matviewname as name,
      schemaname as schema,
      'materialized_view' as type
    from pg_matviews
    where schemaname ilike '{{ schema_relation.schema }}'
  {% endcall %}
  {{ return(load_result('list_relations_without_caching').table) }}
{% endmacro %}
