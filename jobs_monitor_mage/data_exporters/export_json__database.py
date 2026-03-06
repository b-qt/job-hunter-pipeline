from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.postgres import Postgres
from pandas import DataFrame

import os
from os import path


if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_postgres(df: DataFrame, **kwargs) -> None:
    """
    Template for exporting data to a PostgreSQL database.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#postgresql
    
    # Define your schema and table names here :
    # - 'schema_name' is the name of the database schema where the table will 
    #    be created or replaced creating a postgreSQL schema 
    # - 'table_name' is the name of the table that will be created or replaced
    #    in the specified schema; this is also defined in the .env file
    
    """
    #. 1. Load the configurations from the io_config.yaml file 
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    config_loader = ConfigFileLoader(config_path, config_profile)
    
    #. 2. Create the schema and table names using environment variables
    table_name = config_loader.config.get('POSTGRES_TABLE')  # Get table name from config
    schema_name = config_loader.config.get('POSTGRES_SCHEMA')  # Get schema name from config
    if not table_name:
        raise ValueError("❌ POSTGRES_TABLE not found in .env or io_config.yaml")
        
    print(f"📡 Attempting to export data to PostgreSQL table '{schema_name}.{table_name}'...")
    
    #3. Export the DataFrame to PostgreSQL using the Postgres class with the loaded configurations
    try:
        with Postgres.with_config(config_loader) as loader:
            loader.export(
                df,
                schema_name,
                table_name,
                index=False,  # whether to include index in exported table
                if_exists='replace',  # resolution policy if table already exists
            )
    except Exception as e:
        print(f"💥 Connection Failed! Check your io_config.yaml and Postgres network access.")
        raise e
        
    print("✅ Data export to PostgreSQL completed successfully.")