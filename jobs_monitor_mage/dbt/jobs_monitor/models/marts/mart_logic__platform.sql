/*
This model applies the transformation to categorize job listings by region. It uses the cleaned data from the previous model (int_jobs_cleaned) and applies additional logic to categorize the job listings based on their location. The categorization is done using a CASE statement that checks for specific keywords in the location field to determine if a job is remote, onsite, or other.

Materialization Strategy:
- The model is materialized as a view, which means that it will create a virtual table in the database.

Key Transformations:
1. It references the cleaned data from the int_jobs_cleaned model to ensure that it is working with deduplicated and categorized job listings.
2. It partitions the data by job_loc to create separate categories for remote, onsite, and other job listings.
3. The final output includes the job listings along with their categorized location (job_loc) 
*/
{{ config(materialized='view') }} -- for performance and storage optimization.
with cleaned_data as (
    select *
    from {{ ref('int_jobs_cleaned') }} -- reference to the intermediate model that contains cleaned and categorized job listings
)
select
    title,
    link,
    published,
    location,
    platform,
    scraped_at,
    job_loc, -- categorized location (Remote, Onsite, Other)
    job_level -- categorized job level (Senior, Junior, Mid-Level/Unspecified)
from cleaned_data
order by platform -- partition the data by platform