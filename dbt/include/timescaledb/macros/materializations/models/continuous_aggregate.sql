{%- materialization continuous_aggregate, adapter="timescaledb" -%}

  {%- set existing_relation = load_cached_relation(this) -%}
  {%- set target_relation = this.incorporate(type=this.MaterializedView) -%}

  {{ run_hooks(pre_hooks, inside_transaction=False) }}

  -- `BEGIN` happens here:
  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  {%- set grant_config = config.get('grants') -%}

  {%- set full_refresh_mode = should_full_refresh() -%}

  {#- If the existing relation is not a materialized view or we do a full refresh,
    we will just drop it and create this one instead. -#}
  {%- if full_refresh_mode or not existing_relation.is_materialized_view %}
    {{- drop_relation_if_exists(existing_relation) -}}
  {% endif -%}

  {% call statement('main') -%}
    {#- Now we find out if we have to alter any existing relation or we create a new one. -#}
    {{ get_create_continuous_aggregate_as_sql(target_relation, sql) }}

    {{ clear_refresh_policy(target_relation) }}
    {%- if config.get('refresh_policy') %}
      {{ add_refresh_policy(target_relation, config.get('refresh_policy')) }}
    {%- endif -%}

    {{ set_compression(target_relation, config.get("compression")) }}
    {{ clear_compression_policy(target_relation) }}
    {%- if config.get('compression') %}
      {{ add_compression_policy(target_relation, config.get("compression")) }}
    {%- endif -%}
  {%- endcall %}

  {% do create_indexes(target_relation) %}

  {%- call statement("clear_retention_policy") %}
    {{ clear_retention_policy(target_relation) }}
  {% endcall -%}
  {%- if config.get("retention_policy") %}
    {% call statement("retention_policy") %}
      {{ add_retention_policy(target_relation, config.get("retention_policy")) }}
    {% endcall %}
  {% endif -%}

  {% set should_revoke = should_revoke(existing_relation, full_refresh_mode=True) %}
  {% do apply_grants(target_relation, grant_config, should_revoke=should_revoke) %}

  {% do persist_docs(target_relation, model) %}

  {{ run_hooks(post_hooks, inside_transaction=True) }}

  {{ adapter.commit() }}

  {{ run_hooks(post_hooks, inside_transaction=False) }}

  {#- Load the data into the continuous aggregate -#}
  {% if config.get("refresh_now", True) %}
    {% do do_refresh_continuous_aggregate(target_relation) %}
  {% endif %}

  {{ return({'relations': [target_relation]}) }}

{%- endmaterialization -%}
