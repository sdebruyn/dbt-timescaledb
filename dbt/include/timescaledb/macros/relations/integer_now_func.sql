{% macro set_integer_now_func(relation, integer_now_func, integer_now_func_sql = none) %}
  {% if integer_now_func_sql %}
    create or replace function {{ relation.database }}.{{ relation.schema }}.{{ integer_now_func }}() returns bigint language sql immutable as $$
      {{ integer_now_func_sql }}
    $$;
  {% endif %}
  select set_integer_now_func('{{ relation }}', '{{ relation.database }}.{{ relation.schema }}.{{ integer_now_func }}');
{% endmacro %}
