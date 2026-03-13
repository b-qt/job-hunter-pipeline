/*
Using an ephemeral materialization so it creates a reusable CTE that can be referenced by downstream models without creating a physical table in the database. This is particularly useful for performance optimization and storage efficiency, especially when dealing with large datasets or when the data is only needed temporarily during the transformation process.

This model performs several key transformations on the raw data:
1. Deduplication: It uses the ROW_NUMBER() window function to assign a unique index to each record based on the combination of title and link, ordered by the scraped_at timestamp in descending order.
2. Categorization: It categorizes job listings based on keywords in the location and title fields. For example, it identifies whether a job is remote or onsite based on the presence of certain keywords in the location field, and it categorizes the job level (e.g., Senior, Junior) based on keywords in the title field.
3. Data Cleaning: It ensures that the published date is in a consistent date format for easier querying and analysis.

The final output of this model includes the cleaned and categorized job listings, which can then be used for further analysis or to populate downstream models in the DBT project.
*/

{{ config(materialized='ephemeral') }} -- non-persistent, reusable CTE for downstream models.

with raw_data as (
    select *
    from {{ ref('stg_read_postgres') }} -- reference to the staging model that reads from Postgres
),
deduplicates as (
    select
        title,
        link,
        published,
        location,
        platform,
        scraped_at,
        row_number() over (partition by title, link order by scraped_at desc) as idx -- assign a row number to each record based on the combination of title and link, ordered by scraped_at in descending order
    from raw_data
),
categorized as (
    select
        title,
        link,
        cast(published as date) as published, -- ensure the published field is in date format for consistency and easier querying
        location, -- modify this so linkedin.com/jobs becomes linkedin.com
        platform,
        scraped_at,
        case
            when location ilike '%remote%' then 'Remote'
            when location ilike '%onsite%' then 'Onsite'
            else 'Other/Hybrid'
        end as work_mode, -- categorize the job listing based on the presence of keywords in the location field
        case
            when lower(title) like '%senior%' or lower(title) like '%sr%' then 'Senior'
            when lower(title) like '%junior%' or lower(title) like '%jr%' then 'Junior'
            else 'Mid-Level/Unspecified'
        end as job_level -- categorize the job listing based on the presence of keywords in the title field
    from deduplicates
    where idx = 1 -- ensure we are only working with the most recent record for each unique combination of title and link
)

select
    title,
    link,
    published,
    location,
    platform,
    scraped_at,
    work_mode, -- categorized work mode (Remote, Onsite, Other/Hybrid)
    job_level
from categorized