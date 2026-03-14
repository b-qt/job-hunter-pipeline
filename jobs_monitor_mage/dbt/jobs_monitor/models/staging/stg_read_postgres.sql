
/*
   I can override configurations from the dbt_project.yml file here. 
   - For example, I can change the materialization strategy for this model to
      'view' instead of the default 'table'. This means that when I run dbt, it
      will create a view in the database instead of a table for this model.
    - I can also add other configurations such as tags, description, or custom configurations specific to this model.

    Note: The configurations set in this file will only apply to this specific model and will not affect other models in the project.

    1. This model reads the database and creates a view with the specified materialization strategy.
    1.i. The materialization strategy determines how the model is stored in the database (e.g., as a table, view, or incremental model).
    1.ii. By setting the materialization to 'view', we ensure that the model is created as a view in the database, which can be useful for performance and maintenance reasons, especially when dealing with large datasets or when we want to avoid storing redundant data.
*/
-- models/staging/stg_read_postgres
{{ config(materialized='view') }} -- performance and storage optimization.

with source_data as (
    select *
    from {{ source(
        'internal_postgres',
        env_var('POSTGRES_TABLE')
    )}}
)

select
    title,
    link,
    published,
    location, --- ensure that linkedin.com/jobs is saved as linkedin.com
    platform,
    scraped_at 
from source_data