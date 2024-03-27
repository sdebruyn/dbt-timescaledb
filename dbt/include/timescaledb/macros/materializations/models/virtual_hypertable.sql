{% materialization virtual_hypertable, adapter="timescaledb" %}

    {%- set existing_relation = load_cached_relation(this) -%}
    {% if existing_relation is none %}
        {{ exceptions.raise_compiler_error("Virtual hypertables require existing hypertables") }}
    {% endif %}

    {%- set grant_config = config.get('grants') -%}
    {{ run_hooks(pre_hooks, inside_transaction=False) }}

    -- `BEGIN` happens here:
    {{ run_hooks(pre_hooks, inside_transaction=True) }}

    -- build model
    {% call statement('main') -%}
        select 1 as dummy;

        {%- if config.get('compression') %}
            {{ enable_compression(existing_relation, config.get("compression")) }}
            {{ add_compression_policy(existing_relation, config.get("compression")) }}
        {% endif -%}

        {%- if config.get("integer_now_func") %}
            {{ set_integer_now_func(existing_relation, config.get("integer_now_func"), config.get("integer_now_func_sql")) }}
        {% endif -%}

    {%- endcall %}

    {% do create_indexes(existing_relation) %}

    {%- if config.get("reorder_policy") %}
        {% call statement("reorder_policy") %}
            {{ add_reorder_policy(existing_relation, config.get("reorder_policy")) }}
        {% endcall %}
    {% endif -%}

    {%- if config.get("retention_policy") %}
        {% call statement("retention_policy") %}
            {{ add_retention_policy(existing_relation, config.get("retention_policy")) }}
        {% endcall %}
    {% endif -%}

    {{ run_hooks(post_hooks, inside_transaction=True) }}

    {% set should_revoke = should_revoke(existing_relation, full_refresh_mode=True) %}
    {% do apply_grants(existing_relation, grant_config, should_revoke=should_revoke) %}

    {% do persist_docs(existing_relation, model) %}

    -- `COMMIT` happens here
    {{ adapter.commit() }}

    {{ run_hooks(post_hooks, inside_transaction=False) }}

    {{ return({'relations': [existing_relation]}) }}

{% endmaterialization %}
