{% materialization virtual_hypertable, adapter="timescaledb" %}

    {%- set target_relation = this.incorporate(type=this.Table) -%}
    {%- set existing_relation = load_cached_relation(target_relation) -%}
    {%- set change_collection = get_virtual_hypertable_change_collection(existing_relation, config) -%}
    {%- set grant_config = config.get('grants') -%}
    {{ run_hooks(pre_hooks, inside_transaction=False) }}

    -- `BEGIN` happens here:
    {{ run_hooks(pre_hooks, inside_transaction=True) }}

    -- build model
    {% call statement('main') -%}
        select 1 as dummy;

        {{ set_compression(target_relation, config.get("compression")) }}
        {{ clear_compression_policy(target_relation) }}
        {%- if config.get('compression') %}
            {{ add_compression_policy(target_relation, config.get("compression")) }}
        {% endif -%}

        {%- if config.get("integer_now_func") %}
            {{ set_integer_now_func(target_relation, config.get("integer_now_func"), config.get("integer_now_func_sql")) }}
        {% endif -%}

        {%- if config.get("chunk_time_interval") %}
            {{ set_chunk_time_interval(target_relation, config.get("chunk_time_interval")) }}
        {% endif -%}

        {%- if change_collection %}
            {{ timescaledb__update_indexes_on_virtual_hypertable(target_relation, change_collection.indexes) }}
        {%- endif %}

        {{ clear_reorder_policy(target_relation) }}
        {%- if config.get("reorder_policy") %}
            {{ add_reorder_policy(target_relation, config.get("reorder_policy")) }}
        {% endif -%}

        {{ clear_retention_policy(target_relation) }}
        {%- if config.get("retention_policy") %}
            {{ add_retention_policy(target_relation, config.get("retention_policy")) }}
        {% endif -%}

    {%- endcall %}

    {{ run_hooks(post_hooks, inside_transaction=True) }}

    {% set should_revoke = should_revoke(target_relation, full_refresh_mode=True) %}
    {% do apply_grants(target_relation, grant_config, should_revoke=should_revoke) %}

    {% do persist_docs(target_relation, model) %}

    -- `COMMIT` happens here
    {{ adapter.commit() }}

    {{ run_hooks(post_hooks, inside_transaction=False) }}

    {{ return({'relations': [target_relation]}) }}

{% endmaterialization %}
