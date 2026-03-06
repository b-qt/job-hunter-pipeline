
/*
   I can override configurations from the dbt_project.yml file here. 
   - For example, I can change the materialization strategy for this model to
      'view' instead of the default 'table'. This means that when I run dbt, it
      will create a view in the database instead of a table for this model.
    - I can also add other configurations such as tags, description, or custom configurations specific to this model.

    Note: The configurations set in this file will only apply to this specific model and will not affect other models in the project.

    1. This model reads the database and creates a view with the specified materialization strategy.
*/

{{ config(materialized='view') }}

with source_data as (

    select *
    from {{ source('my_source', 'my_table') }}

)

select *
from source_data

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
