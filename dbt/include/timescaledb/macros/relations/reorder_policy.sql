{% macro add_reorder_policy(relation, reorder_config) %}
  {%- set index_dict = reorder_config.index -%}
  {%- set index_config = adapter.parse_index(index_dict) -%}
  {%- set index_name = index_config.render(relation) -%}
  {%- set _columns = index_config.columns | join(",") | lower | replace("'", "''") -%}
  {#- Index names carry a timestamp, so an existing index is found by its columns -#}

  do $$
  declare
    _index_name name;
  begin
    select c.relname into _index_name
    from pg_index i
    join pg_class c on c.oid = i.indexrelid
    where i.indrelid = '{{ relation }}'::regclass
    and array(
      select a.attname::text
      from unnest(i.indkey::int2[]) with ordinality k(attnum, position)
      left join pg_attribute a on a.attrelid = i.indrelid and a.attnum = k.attnum
      order by k.position
    ) = string_to_array('{{ _columns }}', ',')
    order by c.relname;

    if _index_name is null then
      {%- if reorder_config.create_index is none or reorder_config.create_index %}
      {{ timescaledb__get_create_index_sql(relation, index_dict, index_name) }}
      _index_name := '{{ index_name }}';
      {%- else %}
      raise exception 'Reorder policy on {{ relation }}: no index on ({{ _columns }})';
      {%- endif %}
    end if;

    perform add_reorder_policy('{{ relation }}', _index_name,

    {%- if reorder_config.initial_start %}
        initial_start => '{{ reorder_config.initial_start }}',
    {% endif -%}

    {%- if reorder_config.timezone %}
        timezone => '{{ reorder_config.timezone }}',
    {% endif -%}

    if_not_exists => true
  );
  end $$;
{% endmacro %}

{% macro clear_reorder_policy(relation) %}
  select remove_reorder_policy('{{ relation }}', if_exists => true);
{% endmacro %}
