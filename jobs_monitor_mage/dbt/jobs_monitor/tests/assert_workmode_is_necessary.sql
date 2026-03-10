/*
This test ensures that the work_mode column is properly populated with values (Remote, Onsite, Other/Hybrid) for all job listings in the dataset.
*/
select
    work_mode -- select the work_mode column to check for necessary values
from {{ ref('int_jobs_cleaned') }} -- reference to the intermediate model that contains cleaned and categorized job listings
where work_mode is null -- filter for rows where work_mode is null to identify any missing values
order by published desc -- order the results by the published date in descending order to get the most recent job listings first