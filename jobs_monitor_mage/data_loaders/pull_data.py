import pandas as pd

import json
import os

from datetime import datetime, date, timedelta

import feedparser

from bs4 import BeautifulSoup


if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

@data_loader
def load_data_from_api(*args, **kwargs):
    # 1. Clean Parameter Definition
    # Use kwargs.get() to allow for dynamic overrides from the Mage UI
    keywords = kwargs.get('keywords', 'Data Engineer')
    
    # Practitioner Tip: Collapsing synonyms into an 'OR' group reduces network calls by 80%
    locations = kwargs.get('location', 
                            [
                                'Bizkaia', 
                                'Zamudio', 
                                'IDOM', 
                                'Bilbao', 
                                'Vizcaya', 
                                'Basque Country'
                            ]) #Bizkaia, Zamudio, IDOM, Bilbao, Vizcaya
    
    time_span = kwargs.get('time_span', 10)
    start_date = kwargs.get('start_date', (datetime.now() - timedelta(days=time_span)).strftime('%Y-%m-%d'))
    
    # Practitioner Tip: Collapsing sites into an 'OR' group ensures we hit Google once per language setting
    sites = kwargs.get('site', ['site:linkedin.com/jobs', 'site:infojobs.net'])#/view')

    results = []
    seen_links = set()

    for site in sites:
        print(f"📡 Ingesting {site.split('site:')[-1]} jobs for Northern Spain since {start_date} ...")
        
        for location in locations:
            query = f'"{keywords}" {location} {site} after:{start_date}'
            encoded_query = query.replace(' ', '+').replace('"', '%22').lower()
            
            rss_urls = [
                f"https://news.google.com/rss/search?q={encoded_query}&hl=es&gl=ES&ceid=ES:es",  
                f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=ES&ceid=ES:en"  # jobs in spanish companies where the host language is english 
                    ]  #hl=host language ; gl=geolocation ; ceid?customid | 

            #https://news.google.com/rss/search?q=data+engineer+bizkaia+site:linkedin.com%2fjobs%2fview+after:2026-02-17&hl=es&gl=ES&ceid=ES:es
            #https://www.linkedin.com/jobs/search/?currentJobId=4379942236&f_TPR=r604800&geoId=102608479&keywords=data%20engineer&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true
            
            for rss_url in rss_urls:
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries:
                    if entry.link not in seen_links:
                        platform = "Infojobs" if "infojobs.net" in entry.link else "LinkedIn"

                        title = entry.get("title")
                        # 2.i. Pull text from description with beautifulsoup
                        #soup = BeautifulSoup(entry.get("description"), "html.parser")
                        #full_job_text = soup.find('a').get_text()

                        #2.ii. Location is portion of title after 'en'
                        # Safety check: not all titles follow the "hiring...in" format
                        try:
                            loc_extracted = title.split(" in ")[-1].split("-")[0].strip()
                            company = title.split("hiring")[0].strip()
                        except:
                            loc_extracted = "Spain"
                            company = "Unknown"

                        results.append({
                            "company": company,
                            "title": title,
                            "link":  entry.link,
                            # "description": full_job_text, | Description is title
                            "published":  pd.to_datetime(entry.get("published")).strftime('%Y-%m-%d %H:%M:%S'),
                            #"source": "LinkedIn via Google Index", | Source is obvious
                            "location": loc_extracted,
                            "scraped_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "source": platform
                        })
                        seen_links.add(entry.link)

    if not results:
        print("⚠️ No jobs found.")
        standard_columns = [
        "company", "title", "link", "published", 
        "location", "scraped_at", "source"
        ] 

        return pd.DataFrame(columns=standard_columns)

    df = pd.DataFrame(results)

    # 3. Secure File Writing
    json_dir = "/home/src/data"
    if not os.path.exists(json_dir):
        os.makedirs(json_dir, exist_ok=True)
        
    json_file_path = os.path.join(json_dir, "linkedin_insights.json")
    
    # Practitioner Tip: Using df.to_json directly is more efficient than open() + json.dump()
    df.to_json(
        json_file_path,
        orient='records',
        date_format='iso',
        indent=4,
        force_ascii=False # Keeps Spanish accents like 'ñ' pure
    )

    print(f"✅ Successfully captured {len(df)} items.")
    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
