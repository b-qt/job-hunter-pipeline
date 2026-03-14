import os
import pandas as pd
from sqlalchemy import create_engine, text
from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from os import path

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom

@custom
def save_to_json(*args, **kwargs) -> None:
    # 1. Load configurations from io_config.yaml
    repo_path = get_repo_path() 
    config_path = path.join(repo_path, 'io_config.yaml')
    config_profile = 'default'
    config_loader = ConfigFileLoader(config_path, config_profile)
    
    # Helper to get setting from Env Var or Config File
    def get_setting(key, default=None):
        return os.getenv(key) or config_loader.config.get(key) or default

    # 2. Extract Database Parameters
    user     = get_setting('POSTGRES_USER')
    password = get_setting('POSTGRES_PASSWORD')
    host     = get_setting('POSTGRES_HOST')
    port     = get_setting('POSTGRES_PORT', '5432')
    database = get_setting('POSTGRES_DBNAME') or get_setting('POSTGRES_DB')
    
    # Default settings for your schema and tables
    initial_schema = get_setting('POSTGRES_SCHEMA', 'job_monitor_schema')
    fct_jobs_table = get_setting('FACT_JOB_POSTING', 'fct_job_postings')
    fct_insights_table = get_setting('FACT_MARKET_INSIGHTS', 'fct_market_insights')

    # 3. Create Connection
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)

    # 4. Define target directory (Absolute path for Mage Docker)
    target_dir = "/home/src/data"
    os.makedirs(target_dir, exist_ok=True)

    try:
        with engine.connect() as conn:
            # --- AUTO-DISCOVERY LOGIC ---
            # Check if fct_jobs exists in the provided schema
            check_sql = text(f"""
                SELECT schemaname FROM pg_tables 
                WHERE tablename = :tname AND schemaname = :sname
            """)
            res = conn.execute(check_sql, {"tname": fct_jobs_table, "sname": initial_schema}).fetchone()

            if res:
                final_schema = initial_schema
            else:
                print(f"⚠️ Table {fct_jobs_table} not found in '{initial_schema}'. Searching database...")
                # Find the actual schema where dbt put the table
                find_sql = text("SELECT schemaname FROM pg_tables WHERE tablename = :tname LIMIT 1")
                actual = conn.execute(find_sql, {"tname": fct_jobs_table}).fetchone()
                
                if actual:
                    final_schema = actual[0]
                    print(f"💡 Found it! Using schema: '{final_schema}'")
                else:
                    # If we still can't find it, list all tables to the log for debugging
                    all_tabs = conn.execute(text("SELECT schemaname, tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema')")).fetchall()
                    print("--- 🔍 Current Database Tables ---")
                    for s, t in all_tabs: print(f"{s}.{t}")
                    raise ValueError(f"❌ Table {fct_jobs_table} does not exist in the database.")

            # 5. Fetch Data with the Corrected Schema
            print(f"📡 Exporting {final_schema}.{fct_jobs_table} and {final_schema}.{fct_insights_table}...")
            
            df_jobs = pd.read_sql_query(
                text(f'SELECT * FROM "{final_schema}"."{fct_jobs_table}"'), 
                conn
            )
            
            df_insights = pd.read_sql_query(
                text(f'SELECT * FROM "{final_schema}"."{fct_insights_table}"'), 
                conn
            )

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