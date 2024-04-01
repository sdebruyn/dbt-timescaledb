{%- materialization continuous_aggregate, adapter="timescaledb" -%}

  {%- set existing_relation = load_cached_relation(this) -%}
  {%- set target_relation = this.incorporate(type=this.MaterializedView) -%}

  {{ run_hooks(pre_hooks, inside_transaction=False) }}

  -- `BEGIN` happens here:
  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  {%- set grant_config = config.get('grants') -%}

  {%- set full_refresh_mode = should_full_refresh() -%}

  {%- set should_drop = full_refresh_mode or not existing_relation.is_materialized_view -%}
  {%- set create_mode = not existing_relation or should_drop -%}
  {%- set alter_mode = not create_mode -%}
  {%- set configuration_changes = none -%}

  {%- if alter_mode -%}
    {%- set configuration_changes = get_materialized_view_configuration_changes(existing_relation, config) -%}
  {%- endif -%}

  {%- if configuration_changes.requires_full_refresh -%}
    {%- set alter_mode = false -%}
    {%- set should_drop = true -%}
    {%- set create_mode = true -%}
  {%- endif -%}

  {%- if should_drop -%}
    {{- drop_relation_if_exists(existing_relation) -}}
  {%- endif -%}

  {% call statement('main') -%}
    {%- if create_mode %}
      {{ get_create_continuous_aggregate_as_sql(target_relation, sql) }}
    {% endif -%}

    {%- if alter_mode and configuration_changes.indexes %}
      {{ postgres__update_indexes_on_materialized_view(target_relation, configuration_changes.indexes) }}
    {% endif -%}

    {%- if alter_mode %}
      {{ clear_refresh_policy(target_relation) }}
    {% endif -%}
    {%- if config.get('refresh_policy') %}
      {{ add_refresh_policy(target_relation, config.get('refresh_policy')) }}
    {%- endif -%}

    {%- if alter_mode or config.get('compression') %}
      {{ set_compression(target_relation, config.get("compression")) }}
    {% endif -%}
    {%- if alter_mode %}
      {{ clear_compression_policy(target_relation) }}
    {% endif -%}
    {%- if config.get('compression') %}
      {{ add_compression_policy(target_relation, config.get("compression")) }}
    {%- endif -%}
  {%- endcall %}

  {%- if create_mode %}
    {% do create_indexes(target_relation) %}
  {% endif -%}

  {%- if alter_mode %}
    {%- call statement("clear_retention_policy") %}
      {{ clear_retention_policy(target_relation) }}
    {% endcall -%}
  {% endif -%}
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
