if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

import json
import os

import psycopg2

@custom
def export_to_static_api(*args, **kwargs):
    """
    args: The output from any upstream parent blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    data_loc = "data/linkedin_insights.json"
    result_loc = "data/api_snapshot.json"
    db_path = os.getenv("DB_PATH", data_loc)
    conn = psycopg2.connect(db_path)
    
    data = conn.execute(
        "SELECT * FROM main.fct_job_postings"
        ).df().to_dict(orient="records")
    
    with open(result_loc, "w") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Static API Snapshot Created")
    conn.close()
    
export_to_static_api()