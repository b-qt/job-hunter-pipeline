from dotenv import load_dotenv
load_dotenv()

import os
from os import path

import streamlit as st

import pandas as pd
#import time
import json

import subprocess
from datetime import datetime

os.environ['POSTGRES_HOST'] = '127.0.0.1'

# 1. Manually set the path to your Mage project folder
current_dir = os.getcwd()
mage_project_name = 'jobs_monitor_mage' 
os.environ['MAGE_REPO_PATH'] = path.join(current_dir, mage_project_name)


# Import Mage logic (Ensure your PYTHONPATH is set correctly)
# Note: If these decorators cause issues, you may need to strip them in your Mage files
try:
    from jobs_monitor_mage.data_loaders.load_data__rss import JobIngestor
    from jobs_monitor_mage.data_exporters.export_json__database import export_data_to_postgres
    from jobs_monitor_mage.custom.generate_api import save_to_json
except ImportError:
    st.error("Could not import Mage modules. Ensure the app is running in the project root.")

# --- Configure page ---
st.set_page_config(
    page_title="Spanish Job Market Insights",
    page_icon="📊",
    layout="wide"
)

# --- Helper: Load data ---
@st.cache_data
def load_data():
    repo_path = os.getenv('MAGE_REPO_PATH') or os.getcwd()
    jobs_json = os.path.join(repo_path, 'data/jobs.json')
    insights_json = os.path.join(repo_path, 'data/insights.json')
    
    if not os.path.exists(jobs_json) or not os.path.exists(insights_json):
        os.makedirs(os.path.dirname(jobs_json),exist_ok=True)
        os.makedirs(os.path.dirname(insights_json),exist_ok=True)
        #return None, None
    
    try:
        with open(jobs_json, "r", encoding='utf-8') as f:
            jobs_df = pd.DataFrame(json.load(f))
        with open(insights_json, "r", encoding='utf-8') as f:
            insights_df = pd.DataFrame(json.load(f))
        
        #st.write(f"jobs_df: {list(jobs_df.columns)}")
        #st.write(f"insights_df: {list(insights_df.columns)}")
        
        return jobs_df, insights_df
    except Exception as e:
        st.error(f"Error reading JSON: {e}")
        return None, None

# --- Pipeline Execution ---
def run_pipeline(keywords,  areas, sites, time_span):
    """Executes the full ELT sequence"""
    with st.status("🚀 Running Job Pipeline...", expanded=True) as status:
        # 1. Ingest
        status.write("📡 Ingesting from RSS feeds...")
        #st.toast(f"Parameters: \nJobs: {keywords}\n areas: { areas}\nSearching in: {sites}\nOver: {time_span}days")
        ingestor = JobIngestor(
            keywords=keywords,
             areas= areas,
            sites=sites,
            time_span=time_span
        )
        data = ingestor.execute_refinery()
        if not data:
            st.error("No data found for these parameters.")
            return False
        
        df = pd.DataFrame(data)
        # 1.i. Save to JSON
        repo_path = os.getenv('MAGE_REPO_PATH') or os.getcwd()
        target_dir = os.path.join(repo_path, 'data/user_data.json')
        try:
            os.makedirs(os.path.dirname(target_dir),exist_ok=True)
            df.to_json(target_dir,
                       orient="records",
                       indent=4,
                       force_ascii=False)
            st.success(f"Collected {len(df)} records ")# --DEBUGGING -- and saved to {target_dir}")
        except Exception as e:
            st.error(f"❌ Storage error: {e}") 
        
        # 2. Export to DB
        status.write("💾 Exporting raw data to PostgreSQL...")
        try:
            export_data_to_postgres(df)
            st.success(f"Exported data to database")
        except Exception as e:
            st.error(f"❌ Storage error: {e}") 
        
        # 3. dbt Transformations
        status.write("🏗️ Running dbt transformations...")
        try:
            # Update path to your dbt project folder
            base_dir = os.path.dirname(os.path.abspath(__file__))
            #jobs_monitor_mage/dbt/jobs_monitor/dbt_project.yml
            project_dir = os.path.join(base_dir, "jobs_monitor_mage", "dbt","jobs_monitor")
            dbt_path = project_dir
            
            full_env = os.environ.copy()
            
            result = subprocess.run(
                [
                    "dbt", "run",
                    "--project-dir", dbt_path,
                    "--profiles-dir",dbt_path,
                    "--no-partial-parse"
                ],
                env=full_env,
                capture_output=True,
                text=True,
                check=True
            )
            st.success("DBT Transformations completed")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            st.error(f"dbt failed with exit code {e.returncode}")
            error_output = e.stderr if e.stderr else e.stdout
            st.code(error_output) 
            return False
            
        # 4. Generate API JSON
        status.write("📄 Updating JSON API files...")
        save_to_json() # Call the function directly
        
        status.update(label="✅ Pipeline Complete!", state="complete", expanded=False)
    
    st.cache_data.clear() # Clear cache so UI reloads data
    return True

def main():

    # --- Load Data Initially ---
    jobs_df, insights_df = load_data()

    # --- Sidebar Configuration ---
    st.sidebar.header("Pipeline Control")
    
    with st.sidebar.popover("⚙️ Fetch New Data"):
        st.markdown("### Search Parameters")
        kw_input = st.text_input("Keywords (comma-separated)", "Data Engineer")
        loc_input = st.text_input("Areas (comma-separated)", "Bizkaia, Bilbao")
        site_input = st.text_input("Platforms", "site:linkedin.com,site:infojobs.net")
        days = st.slider("Days to look back", 1, 30, 7)
        
        if st.button("Start Pipeline"):
            kws = [k.strip() for k in kw_input.split(",")]
            locs = [l.strip() for l in loc_input.split(",")]
            sts = [s.strip() for s in site_input.split(",")]
            
            success = run_pipeline(kws, locs, sts, days)
            if success:
                st.cache_data.clear()
                jobs_df, insights_df = load_data()
                last_updated_dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.sidebar.caption(f"📅 Data last updated: {last_updated_dt}")
                st.rerun()

    if jobs_df is None or jobs_df.empty:
        st.warning("No data found. Please run the pipeline from the sidebar to generate data.")
        return

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")
    # Using 'query_area' or 'area' depending on your dbt output
    #st.write(f"columns: {list(jobs_df.columns)}")
    loc_col = "area" if "area" in jobs_df.columns else "query_area"
    if loc_col is None:
        st.error(f"Could not find area column {loc_col}... Available columns: {list(jobs_df.columns)}")
    
    selected_locs = st.sidebar.multiselect(
        "Location", options=sorted(jobs_df[loc_col].unique()), default=jobs_df[loc_col].unique()
    )
    selected_platforms = st.sidebar.multiselect(
        "Platform", options=sorted(jobs_df["platform"].unique()), default=jobs_df["platform"].unique()
    )

    # Filter Data
    filtered_jobs = jobs_df[
        (jobs_df[loc_col].isin(selected_locs)) & 
        (jobs_df["platform"].isin(selected_platforms))
    ]

    # --- Dashboard Layout ---
    st.title(f"🏹 Spanish Job Market Insights")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Jobs Found", len(filtered_jobs))
    m2.metric("Top City", filtered_jobs[loc_col].mode()[0] if not filtered_jobs.empty else "N/A")
    m3.metric("Top Source", filtered_jobs["platform"].mode()[0] if not filtered_jobs.empty else "N/A")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Seniority Distribution")
        if "job_level" in filtered_jobs.columns:
            st.bar_chart(filtered_jobs["job_level"].value_counts())
        else:
            st.info("Intermediate dbt layer required for seniority classification.")

    with col2:
        st.subheader("Jobs per Platform")
        st.bar_chart(filtered_jobs["platform"].value_counts())

    # --- Table Sections ---
    st.subheader("💡 Market Insights")
    st.dataframe(insights_df, width="stretch")

    st.subheader("🔍 Latest Listings")
    
    # Format dates
    filtered_jobs["published"] = pd.to_datetime(filtered_jobs["published"], errors="coerce")
    filtered_jobs = filtered_jobs.sort_values("published", ascending=False)

    st.dataframe(
        filtered_jobs[["title", "platform", loc_col, "published", "link"]],
        column_config={
            "link": st.column_config.LinkColumn("Apply", display_text="View Job"),
            "published": st.column_config.DateColumn("Date")
        },
        hide_index=True,
        width="stretch"
    )

if __name__ == "__main__":
    main()