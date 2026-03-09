# 1. Data loader (jobs_monitor_mage/data_loaders/load_data__rss.py)
- [x] Create a data loader that fetches job-related news from RSS feeds (LinkedIn, InfoJobs, Google News).
- [x] Store the raw data in a structured format (e.g., JSON or CSV) for further processing.
- [x] Implement error handling to manage potential issues with data fetching (e.g., network errors, API limits, schema mismatches, environmental errors).
- [x] Test the data loader to ensure it correctly fetches and stores the data as expected.
- [x] Document the data loader's functionality and usage for future reference and maintenance in a data_loaders/README.md file.
- [x] Store the data in a PostgreSQL database for easy querying and integration with the rest of the pipeline.

# 2. DBT Model (Transformation and Business Logic)
- [x] Integrate the DBT model with the data loader to seamlessly move data from raw storage into database tables.
- [] Implement quality tests in DBT to ensure data integrity and consistency (e.g., no duplicates, valid date formats).
- [] Sort the model to be structured around the specific business logic (finding job listings categorized by region and company) into staging, intermediate and marts.
- [] In the staging layer, create models that clean and standardize the raw data (e.g., removing duplicates, fixing date formats).
- [] Ensure the DBT model can handle the specific requirements of the project, such as filtering for job-related news and categorizing sentiment.
- [] Test the DBT model to ensure it correctly transforms the data and passes all quality tests as expected.
- [] In the intermediate layer, create models that apply the transformations to categorize the news into companies and regions.
- [] In the marts layer, create models that prepare the final datasets for visualization (e.g., aggregating similar companies, filtering for regions).
- [] Document the DBT model's functionality and the logic behind the transformations for future reference and maintenance in a dbt/models/README.md file.
- [] Ensure the DBT model is optimized for performance, especially as the volume of data grows over time.


# 3. Orchestration ()
- [] Automate the data loader to run on a schedule to ensure the data is updated regularly (e.g., every 6 hours).
- [] Set up a workflow to run the DBT transformations after the data loader has fetched new data, ensuring that the data pipeline is seamless and efficient.
- [] Implement monitoring and alerting for the data pipeline to quickly identify and resolve any issues that may arise (e.g., data fetching failures, transformation errors).
- [] Document the orchestration process and any dependencies for future reference and maintenance in    an orchestration/README.md file.

# 4. Updates
- [] Log the data fetching process for monitoring and debugging purposes.
- [] Make manual entries possible for future flexibility (e.g., adding new sources or specific keywords).
