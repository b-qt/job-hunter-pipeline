from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.postgres import Postgres

from pandas import DataFrame
import os
from os import path
from sqlalchemy import create_engine, text
import socket

#from dotenv import load_dotenv
#load_dotenv()

import sqlalchemy
import pandas as pd
import psycopg2
print(f"DEBUG: SQLAlchemy Version: {sqlalchemy.__version__}")
print(f"DEBUG: Pandas Version: {pd.__version__}")
print(f"DEBUG: Psycopg2 Version: {psycopg2.__version__}")


if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_data_to_postgres(df: DataFrame, **kwargs) -> None:

    # 1. Load the configurations
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    config_loader = ConfigFileLoader(config_path, config_profile)
    
    # Helper to clean values from env/yaml
    def get_clean_val(key, default=None):
        val = os.getenv(key) or config_loader.config.get(key) or default
        if val is None or str(val).lower() == 'none':
            return default
        # Strip quotes if they were accidentally included in .env
        return str(val).strip('"').strip("'").strip()

    # 2. Extract and Validate
    user     = get_clean_val('POSTGRES_USER', 'admin')
    password = get_clean_val('POSTGRES_PASSWORD', 'admin')
    database = get_clean_val('POSTGRES_DBNAME') or get_clean_val('POSTGRES_DB', 'job_monitor')
    raw_host = get_clean_val('POSTGRES_HOST', '127.0.0.1')
    port     = int(get_clean_val('POSTGRES_PORT', 5432))
    table    = get_clean_val('POSTGRES_TABLE', 'job_postings')
    schema   = get_clean_val('POSTGRES_SCHEMA', 'job_monitor_schema')

    # 3. Smart Host Resolution
    host = raw_host
    # If we are in Streamlit (Local), we try these in order
    potential_hosts = [host, '127.0.0.1', 'localhost', '0.0.0.0','data-controller']
    
    host = None
    for h in potential_hosts:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                if s.connect_ex((h, port)) == 0:
                    host = h
                    print(f"✅ Python successfully probed {h}:{port}")
                    break
        except:
            continue

    if not host:
        raise ConnectionError(
            f"❌ Could not reach Postgres on any known host. "
            f"Check if 'jobs_monitor_db' is running in Docker."
        )

    # 4. Final Connection Audit (The Bouncer)
    safe_uri = f"postgresql+psycopg2:://{user}:****@{host}:{port}/{database}"
    print(f"🚀 [BOUNCER] Attempting connection: {safe_uri}")

    # 5. Connect and Export
    # Explicitly use +psycopg2 to avoid dialect confusion
    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")
    df.columns = [c.strip('_').lower().strip() for c in df.columns]

    try:
        # Check if the port is actually responsive to Python specifically
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            if s.connect_ex((host, port)) != 0:
                raise ConnectionError(f"Port {port} on {host} is not responding to TCP probes.")

        with engine.begin() as connection:
            print(f"🛠️ Ensuring schema '{schema}' exists...")
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        engine.dispose()

        print(f"📡 Exporting {len(df)} rows with columns: {list(df.columns)} to {schema}.{table}...")
        
        with Postgres.with_config(config_loader) as loader:
            loader.export(
                df,
                schema,
                table,
                index=False,
                if_exists='replace'
            )
            
        print("✅ Data export to PostgreSQL completed successfully.")
        
    except Exception as e:
        print(f"❌ DATABASE ERROR: {str(e)}")
        print(f"💡 DEBUG INFO: User={user}, Host={host}, Port={port}, DB={database}")
        raise e
    finally:
        engine.dispose()