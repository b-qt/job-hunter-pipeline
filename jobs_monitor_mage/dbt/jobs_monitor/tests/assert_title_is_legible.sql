/*
The title should not contain any special characters or be excessively long, as this can make it difficult to read and understand. A legible title should be concise, clear, and free of unnecessary punctuation or symbols. It should effectively convey the main topic or purpose of the content in a straightforward manner. Additionally, using proper capitalization and avoiding all caps can enhance readability.
*/
select
    {{ clean_alphanumeric('title') }} as cleaned_title -- use the clean_alphanumeric macro to remove special characters from the title
from {{ ref('int_jobs_cleaned') }} -- reference to the intermediate model that contains cleaned and categorized job listings
order by published desc -- order the results by the published date in descending order to get the most recent first