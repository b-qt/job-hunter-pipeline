/*
This model aggregates market insights from the job postings data.
It shows which platforms or  areas have the most job listings, and how the distribution of job levels (Senior, Junior, Mid-Level/Unspecified) varies across different platforms and  areas.
*/
{{ config(materialized='table') }} -- for performance and storage optimization.

select
    platform,
    work_mode,
    job_level,
    area,
    count(*) as job_count -- count of job listings for each combination of platform, area, and job level
    --published::date as published_date, -- day for aggregation
from {{ ref('int_jobs_cleaned') }} -- reference to the intermediate model that contains cleaned and categorized job listings
group by 1, 2, 3, 4 -- group by published date, platform, job area, and job level
order by 4 desc, 5 desc -- order the results by published date in descending order and then by job count in descending order to show the most recent and most popular job listings first