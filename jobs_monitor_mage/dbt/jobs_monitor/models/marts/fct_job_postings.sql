/*
This is the main search feed table. 

The model is materialized as a table to optimize for performance and storage, as it will likely be queried frequently for analysis and insights generation.
*/

{{ config(materialized='table') }} -- for performance and storage optimization.

with platform_categorized as (
    select 
        title,
        link,
        published,
        area,
        platform,
        scraped_at,
        work_mode, -- categorized work mode (Remote, Onsite, Other/Hybrid)
        job_level -- categorized job level (Senior, Junior, Mid-Level/Unspecified)
    from {{ ref('int_jobs_cleaned')}}
)

select 
    title,
    link,
    published,
    area,
    platform,
    scraped_at,
    work_mode, -- categorized work mode (Remote, Onsite, Other/Hybrid)
    job_level -- categorized job level (Senior, Junior, Mid-Level/Unspecified)
from platform_categorized
order by published desc -- order the final output by published date in descending order to show the most recent job postings