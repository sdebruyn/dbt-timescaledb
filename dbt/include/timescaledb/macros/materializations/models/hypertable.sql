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
    select create_hypertable(
      '{{ intermediate_relation }}',
      '{{ time_column_name }}',

      {%- if config.get('partitioning_column') %}
        partition_column => '{{ config.get("partitioning_column") }}',
      {% endif -%}

      {%- if config.get('number_partitions') %}
        number_partitions => {{ config.get('number_partitions') }},
      {% endif -%}

      {%- if config.get('chunk_time_interval') %}
        chunk_time_interval => {{ config.get('chunk_time_interval') }},
      {% endif -%}

      {%- if config.get('create_default_indexes') %}
        create_default_indexes => {{ config.get('create_default_indexes') }},
      {% endif -%}

      {%- if config.get('partitioning_func') %}
        partitioning_func => '{{ config.get("partitioning_func") }}',
      {% endif -%}

      {%- if config.get('associated_schema_name') %}
        associated_schema_name => '{{ config.get("associated_schema_name") }}',
      {% endif -%}

      {%- if config.get('associated_table_prefix') %}
        associated_table_prefix => '{{ config.get("associated_table_prefix") }}',
      {% endif -%}

      {%- if config.get('time_partitioning_func') %}
        time_partitioning_func => '{{ config.get("time_partitioning_func") }}',
      {% endif -%}

      {%- if config.get('replication_factor') %}
        replication_factor => {{ config.get('replication_factor') }},
      {% endif -%}

      {%- if config.get('data_nodes') %}
        data_nodes => '{"{{ config.get("data_nodes")|join("\", \"") }}"}',
      {% endif -%}

      {%- if config.get('distributed') %}
        distributed => {{ config.get('distributed') }},
      {% endif -%}

      if_not_exists => false, {# Users should not be concerned with this #}
      migrate_data => true); {# Required since dbt models will always contain data #}

    {%- if config.get('compression') %}
      alter table {{ intermediate_relation }} set (timescaledb.compress
        {%- if config.get("compression").orderby %}
          ,timescaledb.compress_orderby = '{{ config.get("compression").orderby }}'
        {% endif -%}

        {%- if config.get("compression").segmentby %}
          ,timescaledb.compress_segmentby = '{{ config.get("compression").segmentby | join(",") }}'
        {% endif -%}

        {%- if config.get("compression").chunk_time_interval %}
          ,timescaledb.compress_chunk_time_interval = '{{ config.get("compression").chunk_time_interval }}'
        {% endif -%}
      );

      select add_compression_policy(
        '{{ intermediate_relation }}',
        {{ config.get("compression").after }}

        {%- if config.get("compression").schedule_interval %}
          , schedule_interval => '{{ config.get("compression").schedule_interval }}'
        {% endif -%}

        {%- if config.get("compression").initial_start %}
          , initial_start => {{ config.get("compression").initial_start }}
        {% endif -%}

        {%- if config.get("compression").timezone %}
          , timezone => '{{ config.get("compression").timezone }}'
        {% endif -%}

        );
    {%- endif -%}

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
