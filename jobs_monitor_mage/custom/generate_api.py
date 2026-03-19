import os
import pandas as pd
from sqlalchemy import create_engine, text
from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from os import path

import sqlalchemy
import pandas as pd
import psycopg2
print(f"DEBUG: SQLAlchemy Version: {sqlalchemy.__version__}")
print(f"DEBUG: Pandas Version: {pd.__version__}")
print(f"DEBUG: Psycopg2 Version: {psycopg2.__version__}")

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom

@custom
def save_to_json(*args, **kwargs) -> None:
    # 1. Load configurations from io_config.yaml
    repo_path = get_repo_path() or os.getenv('MAGE_REPO_PATH')
    config_path = path.join(repo_path, 'io_config.yaml')
    config_profile = 'default'
    config_loader = ConfigFileLoader(config_path, config_profile)
    
    # Helper to get setting from Env Var or Config File
    def get_setting(key, default=None):
        return os.getenv(key) or config_loader.config.get(key) or default

    # 2. Extract Database Parameters
    user     = get_setting('POSTGRES_USER', 'username')
    password = get_setting('POSTGRES_PASSWORD', 'password')
    host     = get_setting('POSTGRES_HOST','127.0.0.1')
    port     = get_setting('POSTGRES_PORT', 5432)
    database = get_setting('POSTGRES_DBNAME') or get_setting('POSTGRES_DB')
    
    # Default settings for your schema and tables
    initial_schema = get_setting('POSTGRES_SCHEMA', 'job_monitor_schema')
    fct_jobs_table = get_setting('FACT_JOB_POSTING', 'fct_job_postings')
    fct_insights_table = get_setting('FACT_MARKET_INSIGHTS', 'fct_market_insights')

    # 3. Create Connection
    connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)

    # 4. Define target directory (Absolute path for Mage Docker)
    #target_dir = "/home/src/data"
    project_root = os.path.dirname(repo_path)
    target_dir = os.path.join(project_root, 'data')
    os.makedirs(target_dir, exist_ok=True)

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

        def fetch_to_df(tablename):
            query = f'SELECT * FROM "{initial_schema}"."{tablename}"'
            with conn.cursor() as cur:
                cur.execute(query)
                rows=cur.fetchall()
                colnames = [desc[0] for desc in cur.description]

                return pd.DataFrame(rows, columns=colnames)
        df_jobs = fetch_to_df(fct_jobs_table)
        df_insights = fetch_to_df(fct_insights_table)


        # 6. Save to JSON files
        jobs_path = path.join(target_dir, 'jobs.json')
        insights_path = path.join(target_dir, 'insights.json')

        df_jobs.to_json(jobs_path, orient='records', indent=4, force_ascii=False)
        df_insights.to_json(insights_path, orient='records', indent=4, force_ascii=False)

        print(f"✅ JSON Update Complete!")
        print(f"📍 Jobs: {jobs_path} ({len(df_jobs)} rows)")
        print(f"📍 Insights: {insights_path} ({len(df_insights)} rows)")

    except Exception as e:
        print(f"❌ Error during JSON generation: {e}")
        raise e
    finally:
        engine.dispose()