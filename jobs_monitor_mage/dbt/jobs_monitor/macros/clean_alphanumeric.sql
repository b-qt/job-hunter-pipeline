/*
This macro takes a column_name as arguments and removes all non-alphanumeric characters. 
It uses a regular expression to replace any character that is not a letter or a number with an empty string.
*/
{% macro clean_alphanumeric(column_name) %}
    regexp_replace({{ column_name }}, '[^a-zA-Z0-9 áéíóúÁÉÍÓÚñÑ]', '', 'g')
{% endmacro %}