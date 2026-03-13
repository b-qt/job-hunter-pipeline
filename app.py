# Build and deploy the dashboard using streamlit

import streamlit as st

import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import os

import json

# --- Configure page ---
st.set_page_config(
    page_title="Spanish Job Market Insights",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load data ---
@st.cache_data
def load_data():
    # Because the data is stored in a JSON file for simplicity
    jobs_json = "data/jobs.json"
    insights_json = "data/insights.json"
    
    if not os.path.exists(jobs_json) or not os.path.exists(insights_json):
        st.error("Data files not found. Please ensure the data is available.")
        return None, None
    
    with open(jobs_json, "r") as f:
        jobs_data = pd.DataFrame(json.load(f))
    
    with open(insights_json, "r") as f:
        insights_data = pd.DataFrame(json.load(f))
        
    return jobs_data, insights_data
    
try:
    jobs_df, insights_df = load_data()
    
    # --- Sidebar filters ---
    st.sidebar.header("Filters")
    location_filter = st.sidebar.multiselect(
        "Select Location",
        options=jobs_df["location"].unique(),
        default=jobs_df["location"].unique()
    )
    platform_filter = st.sidebar.multiselect(
        "Select Platform",
        options=jobs_df["platform"].unique(),
        default=jobs_df["platform"].unique()
    )
    # Apply filters
    filtered_jobs = jobs_df[
        (jobs_df["location"].isin(location_filter)) &
        (jobs_df["platform"].isin(platform_filter))
    ]
    
    # --- Top Insights ---
    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Total Job Postings", len(filtered_jobs))
    metric2.metric("Top Location", filtered_jobs["location"].mode()[0])
    metric3.metric("Top Platform", filtered_jobs["platform"].mode()[0])
    st.markdown("---")
    
    # --- Visualizations ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Jobs by Seniority Level")
        
        job_level_chart_data = filtered_jobs["job_level"].value_counts().reset_index()
        job_level_chart_data.columns = ["job_level", "count"]
        
        st.bar_chart(
            data = job_level_chart_data,
            x = "job_level",
            y = "count"
        )
        
    with col2:
        st.subheader("Jobs by Platform")
        
        platform_chart_data = filtered_jobs["platform"].value_counts().reset_index()
        platform_chart_data.columns = ["platform", "count"]
        
        st.bar_chart(
            data = platform_chart_data,
            x = "platform",
            y = "count"
        )
        
    # --- Insights Section ---
    st.subheader("Key Insights")
    st.table(insights_df.sample(10))  # Show a random sample of insights for variety
    
    # --- Raw data ---
    st.subheader("Latest Job Postings")
    
    display_df = filtered_jobs[[
        "title",
        "platform",
        "location",
        "published",
        "link"
    ]].copy()
    st.markdown(display_df.platform.unique())
    display_df["published"] = pd.to_datetime(
            display_df["published"], 
            errors="coerce",
            unit="ms"
        )
    display_df = display_df.sort_values(by="published", 
                                        ascending=False).reset_index(drop=True)
    display_df["published"] = display_df["published"].dt.strftime("%d %B %Y")
    
    st.dataframe(
        display_df,
        column_config={
            "link": st.column_config.LinkColumn(
                "Job URL",
                display_text="View Job"
            ),
                "published": st.column_config.TextColumn(
                    "Published Date"
                )
        },
        hide_index=True,
        use_container_width=True
    )
except Exception as e:
    st.error(f"Error loading data: {e}")
    jobs_df, insights_df = None, None