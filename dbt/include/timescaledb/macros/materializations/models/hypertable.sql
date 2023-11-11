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
  {% set grant_config = config.get('grants') %}
  {% set time_column_name = config.get('time_column_name') %}

  -- drop the temp relations if they exist already in the database
  {{ drop_relation_if_exists(preexisting_intermediate_relation) }}
  {{ drop_relation_if_exists(preexisting_backup_relation) }}

  {{ run_hooks(pre_hooks, inside_transaction=False) }}

  -- `BEGIN` happens here:
  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  -- build model
  {% call statement('main') -%}
    {{ get_create_table_as_sql(False, intermediate_relation, sql) }}
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

  {% call statement('hypertable') %}
    select create_hypertable(
      '{{ target_relation }}',
      '{{ time_column_name }}',

      {# optional arguments:
        - partitioning_column (str)
        - number_partitions (int)
        - chunk_time_interval (int)
        - create_default_indexes (bool)
        - partitioning_func (str)
        - associated_schema_name (str)
        - associated_table_prefix (str)
        - time_partitioning_func (str)
        - replication_factor (int)
        - data_nodes (list)
        - distributed (bool)
       #}

      {% if config.get('partitioning_column') is not none %}
        partition_column => '{{ config.get("partitioning_column") }}',
      {% endif %}

      {% if config.get('number_partitions') is not none %}
        number_partitions => {{ config.get('number_partitions') }},
      {% endif %}

      {% if config.get('chunk_time_interval') is not none %}
        chunk_time_interval => {{ config.get('chunk_time_interval') }},
      {% endif %}

      {% if config.get('create_default_indexes') is not none %}
        create_default_indexes => {{ config.get('create_default_indexes') }},
      {% endif %}

      {% if config.get('partitioning_func') is not none %}
        partitioning_func => '{{ config.get("partitioning_func") }}',
      {% endif %}

      {% if config.get('associated_schema_name') is not none %}
        associated_schema_name => '{{ config.get("associated_schema_name") }}',
      {% endif %}

      {% if config.get('associated_table_prefix') is not none %}
        associated_table_prefix => '{{ config.get("associated_table_prefix") }}',
      {% endif %}

      {% if config.get('time_partitioning_func') is not none %}
        time_partitioning_func => '{{ config.get("time_partitioning_func") }}',
      {% endif %}

      {% if config.get('replication_factor') is not none %}
        replication_factor => {{ config.get('replication_factor') }},
      {% endif %}

      {% if config.get('data_nodes') is not none %}
        data_nodes => '{{ config.get("data_nodes") }}',
      {% endif %}

      {% if config.get('distributed') is not none %}
        distributed => {{ config.get('distributed') }},
      {% endif %}

      if_not_exists => false, {# Users should not be concerned with this #}
      migrate_data => true); {# Required since dbt models will always contain data #}
  {% endcall %}

  {% do create_indexes(target_relation) %}

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
