from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.postgres import Postgres
from pandas import DataFrame

import os
from os import path

from sqlalchemy import create_engine


if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_exporter
def export_data_to_postgres(df: DataFrame, **kwargs) -> None:

    #. 1. Load the configurations from the io_config.yaml file 
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    config_loader = ConfigFileLoader(config_path, config_profile)
    
    def get_val(key, default=None):
        env_val = os.getenv(key)
        if env_val:
            return env_val
        
        yaml_val = config_loader.config.get(key)
        
        if yaml_val and isinstance(yaml_val, str) and yaml_val.startswith('{{'):
            return default
            
        return yaml_val or default
    # 2. Get values using the helper function
    user        = get_val('POSTGRES_USER')
    password    = get_val('POSTGRES_PASSWORD')
    host        = get_val('POSTGRES_HOST')
    port        = get_val('POSTGRES_PORT')
    database    = get_val('POSTGRES_DBNAME') or get_val('POSTGRES_DB')
    table_name  = get_val('POSTGRES_TABLE')
    schema_name = get_val('POSTGRES_SCHEMA') or f"{database}_schema"

    # 2.i Validate that all necessary parameters are present before attempting to connect
    if not all([database, table_name, schema_name]):
        raise ValueError("❌ One or more PostgreSQL connection parameters are missing! Check io_config.yaml for POSTGRES_DBNAME, POSTGRES_TABLE, and POSTGRES_SCHEMA")
    
    print(f"""
    --- BOUNCER AUDIT ---
    Database: {database}
    User:     {user}
    Host:     {host}
    Table:    {table_name}
    Schema:   {schema_name}
    ---------------------
    """)
    
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)
    with engine.connect() as connection:
        print(f"🛠️ Ensuring schema '{schema_name}' exists...")
        connection.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        print(f"✅ Schema check/creation completed.")
    
    if not database:
        raise ValueError("❌ Database name is missing! Check io_config.yaml for POSTGRES_DBNAME or POSTGRES_DB")
    
    print(f"📡 Attempting to export data to PostgreSQL table '{table_name}'...")
    
    #3. Export the DataFrame to PostgreSQL using the Postgres class with the loaded configurations
    try:
        df.to_sql(
            name=table_name,  # name of the table to export to
            schema=schema_name,  # name of the schema to export to
            con=engine, # use the connection from the Postgres loader
            index=False,  # whether to include index in exported table
            if_exists='append',  # resolution policy if table already exists
            method='multi',  # use multi-row insert for better performance
        )
        print("\t✅ Data export to PostgreSQL completed successfully.")
    except Exception as e:
        if table_name is None:
            print(f"\t\t No table name detected!!!")
        raise e
    finally:
        engine.dispose()  # Ensure the connection is closed after the operation