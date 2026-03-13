![Task Definition](https://img.shields.io/badge/Task%20Definition-Data%20Pipeline-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow?style=for-the-badge&logo=python)


# 1. Data loader (jobs_monitor_mage/data_loaders/load_data__rss.py)
- [x] Create a data loader that fetches job-related news from RSS feeds (LinkedIn, InfoJobs, Google News).
- [x] Store the raw data in a structured format (e.g., JSON or CSV) for further processing.
- [x] Implement error handling to manage potential issues with data fetching (e.g., network errors, API limits, schema mismatches, environmental errors).
- [x] Test the data loader to ensure it correctly fetches and stores the data as expected.
- [x] Document the data loader's functionality and usage for future reference and maintenance in a data_loaders/README.md file.
- [x] Store the data in a PostgreSQL database for easy querying and integration with the rest of the pipeline.

# 2. DBT Model (Transformation and Business Logic)
- [x] Integrate the DBT model with the data loader to seamlessly move data from raw storage into database tables.
- [x] Implement quality tests in DBT to ensure data integrity and consistency (no duplicates, valid date formats).
- [x] Document the DBT model's functionality and the logic behind the transformations for future reference and maintenance in a dbt/models/README.md file.

# 3. Marts (Visualization and Business Logic)
_Create marts that prepare the data for visualization, ensuring that it is structured in a way that allows for easy analysis and insights generation. This may involve aggregating similar companies, filtering for specific regions, and categorizing sentiment._
- [x] Sort the model to be structured around the specific business logic (finding job listings categorized by region and company) with a table materialization.
- [x] Generate insights from the data around locations, platforms, job levels, job mode 
- [x] Document the marts' functionality and the logic behind the transformations for future reference and maintenance in a dbt/models/README.md file.

# 4. Orchestration and Deployment
- [x] Automate the data loader to run on a schedule to ensure the data is updated regularly (e.g., every 6 hours).
- [x] Set up a workflow to run the DBT transformations after the data loader has fetched new data, ensuring that the data pipeline is seamless and efficient.
- [x] Implement monitoring and alerting for the data pipeline to quickly identify and resolve any issues that may arise (e.g., data fetching failures, transformation errors, data freshness).
- [] Create a simple API endpoint to serve the processed data for visualization
- [] Document the orchestration process and any dependencies for future reference and maintenance in    an orchestration/README.md file.

# I. Updates
- [] Log the data fetching process for monitoring and debugging purposes.
- [] Make manual entries possible for future flexibility (e.g., adding new sources or specific keywords).
- [] Ensure the DBT model is optimized for performance, especially as the volume of data grows over time.
- [] Include a job_status column in the database to track the status of each job listing (e.g., active, expired, removed) for better data management and insights generation.