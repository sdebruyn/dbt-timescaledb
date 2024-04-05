{% materialization hypertable, adapter="timescaledb" %}

  {%- set existing_relation = load_cached_relation(this) -%}
  {%- set target_relation = this.incorporate(type='table') %}
  {%- set intermediate_relation =  make_intermediate_relation(target_relation) -%}
  -- the intermediate_relation should not already exist in the database; get_relation
  -- will return None in that case. Otherwise, we get a relation that we can drop
  -- later, before we try to use this name for the current operation
  {%- set preexisting_intermediate_relation = load_cached_relation(intermediate_relation) -%}
  /*
      See ../view/view.sql for more information about this relation.
  */
  {%- set backup_relation_type = 'table' if existing_relation is none else existing_relation.type -%}
  {%- set backup_relation = make_backup_relation(target_relation, backup_relation_type) -%}
  -- as above, the backup_relation should not already exist
  {%- set preexisting_backup_relation = load_cached_relation(backup_relation) -%}
  -- grab current tables grants config for comparision later on
  {%- set grant_config = config.get('grants') -%}
  {%- set should_truncate = config.get("empty_hypertable", false) -%}
  {%- set dimensions_count = config.get("dimensions", []) | length -%}
  {% if dimensions_count > 0 and not should_truncate %}
    {{ exceptions.raise_compiler_error("The hypertable should always be empty when adding dimensions. Make sure empty_hypertable is set in your model configuration.") }}
  {% endif %}

  -- drop the temp relations if they exist already in the database
  {{ drop_relation_if_exists(preexisting_intermediate_relation) }}
  {{ drop_relation_if_exists(preexisting_backup_relation) }}

  {{ run_hooks(pre_hooks, inside_transaction=False) }}

  -- `BEGIN` happens here:
  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  -- build model
  {% call statement('main') -%}
    {{ get_create_table_as_sql(False, intermediate_relation, sql) }}

    {%- if should_truncate %}
      truncate {{ intermediate_relation }};
    {% endif -%}

    {{- get_create_hypertable_as_sql(intermediate_relation) }}

    {{ set_compression(intermediate_relation, config.get("compression")) }}
    {%- if config.get('compression') %}
      {{ add_compression_policy(intermediate_relation, config.get("compression")) }}
    {% endif -%}

    {%- if config.get("integer_now_func") %}
      {{ set_integer_now_func(intermediate_relation, config.get("integer_now_func"), config.get("integer_now_func_sql")) }}
    {% endif -%}

    {%- if config.get("chunk_time_interval") %}
      {{ set_chunk_time_interval(intermediate_relation, config.get("chunk_time_interval")) }}
    {% endif -%}

  {%- endcall %}

  -- cleanup
  {% if existing_relation is not none %}
     /* Do the equivalent of rename_if_exists. 'existing_relation' could have been dropped
        since the variable was first set. */
    {% set existing_relation = load_cached_relation(existing_relation) %}
    {% if existing_relation is not none %}
        {{ adapter.rename_relation(existing_relation, backup_relation) }}
    {% endif %}
  {% endif %}

  {{ adapter.rename_relation(intermediate_relation, target_relation) }}

  {% do create_indexes(target_relation) %}

  {%- if config.get("reorder_policy") %}
    {% call statement("reorder_policy") %}
      {{ add_reorder_policy(target_relation, config.get("reorder_policy")) }}
    {% endcall %}
  {% endif -%}

  {%- if config.get("retention_policy") %}
    {% call statement("retention_policy") %}
      {{ add_retention_policy(target_relation, config.get("retention_policy")) }}
    {% endcall %}
  {% endif -%}

  {% do create_dimensions(target_relation) %}

  {{ run_hooks(post_hooks, inside_transaction=True) }}

  {% set should_revoke = should_revoke(existing_relation, full_refresh_mode=True) %}
  {% do apply_grants(target_relation, grant_config, should_revoke=should_revoke) %}

  {% do persist_docs(target_relation, model) %}

  -- `COMMIT` happens here
  {{ adapter.commit() }}

  -- finally, drop the existing/backup relation after the commit
  {{ drop_relation_if_exists(backup_relation) }}

  {{ run_hooks(post_hooks, inside_transaction=False) }}

  {{ return({'relations': [target_relation]}) }}
{% endmaterialization %}
