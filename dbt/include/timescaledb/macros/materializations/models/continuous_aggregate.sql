{%- materialization continuous_aggregate, adapter="timescaledb" -%}

  {%- set existing_relation = load_cached_relation(this) -%}
  {% if existing_relation is not none %}
      {%- set existing_relation = existing_relation.incorporate(type=this.MaterializedView) -%}
  {% endif %}
  {%- set target_relation = this.incorporate(type=this.MaterializedView) -%}
  {%- set intermediate_relation =  make_intermediate_relation(target_relation) -%}

  -- the intermediate_relation should not already exist in the database; get_relation
  -- will return None in that case. Otherwise, we get a relation that we can drop
  -- later, before we try to use this name for the current operation
  {%- set preexisting_intermediate_relation = load_cached_relation(intermediate_relation) -%}
  {% if preexisting_intermediate_relation is not none %}
    {%- set preexisting_intermediate_relation = preexisting_intermediate_relation.incorporate(type=this.MaterializedView) -%}
  {% endif %}
  /*
     This relation (probably) doesn't exist yet. If it does exist, it's a leftover from
     a previous run, and we're going to try to drop it immediately. At the end of this
     materialization, we're going to rename the "existing_relation" to this identifier,
     and then we're going to drop it. In order to make sure we run the correct one of:
       - drop view ...
       - drop table ...

     We need to set the type of this relation to be the type of the existing_relation, if it exists,
     or else "view" as a sane default if it does not. Note that if the existing_relation does not
     exist, then there is nothing to move out of the way and subsequentally drop. In that case,
     this relation will be effectively unused.
  */
  {%- set backup_relation_type = target_relation.MaterializedView if existing_relation is none else existing_relation.type -%}
  {%- set backup_relation = make_backup_relation(target_relation, backup_relation_type) -%}
  -- as above, the backup_relation should not already exist
  {%- set preexisting_backup_relation = load_cached_relation(backup_relation) -%}
  {% if preexisting_backup_relation is not none %}
    {%- set preexisting_backup_relation = preexisting_backup_relation.incorporate(type=this.MaterializedView) -%}
  {% endif %}
  -- grab current tables grants config for comparision later on
  {% set grant_config = config.get('grants') %}

  {{ run_hooks(pre_hooks, inside_transaction=False) }}

  -- drop the temp relations if they exist already in the database
  {{ drop_relation_if_exists(preexisting_intermediate_relation) }}
  {{ drop_relation_if_exists(preexisting_backup_relation) }}

  -- `BEGIN` happens here:
  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  -- build model
  {% call statement('main') -%}
    {{ get_create_continuous_aggregate_as_sql(intermediate_relation, sql) }}

    {%- if config.get('refresh_policy') %}
      {{ add_refresh_policy(intermediate_relation, config.get('refresh_policy')) }}
    {%- endif -%}

    {%- if config.get('compression') %}
      {{ enable_compression(intermediate_relation, config.get("compression")) }}
      {{ add_compression_policy(intermediate_relation, config.get("compression")) }}
    {%- endif -%}
  {%- endcall %}

  -- cleanup
  -- move the existing view out of the way
  {% if existing_relation is not none %}
     /* Do the equivalent of rename_if_exists. 'existing_relation' could have been dropped
        since the variable was first set. */
    {% set existing_relation = load_cached_relation(existing_relation) %}
    {% if existing_relation is not none %}
      {%- set existing_relation = existing_relation.incorporate(type=this.MaterializedView) -%}
        {{ adapter.rename_relation(existing_relation, backup_relation) }}
    {% endif %}
  {% endif %}
  {{ adapter.rename_relation(intermediate_relation, target_relation) }}

  {% do create_indexes(target_relation) %}

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

  {{ drop_relation_if_exists(backup_relation) }}

  {{ run_hooks(post_hooks, inside_transaction=False) }}

  {#- Load the data into the continuous aggregate -#}
  {% if config.get("refresh_now", True) %}
    {% do do_refresh_continuous_aggregate(target_relation) %}
  {% endif %}

  {{ return({'relations': [target_relation]}) }}

{%- endmaterialization -%}
