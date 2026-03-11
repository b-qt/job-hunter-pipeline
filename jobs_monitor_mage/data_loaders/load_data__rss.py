import pandas as pd

import json
import os

from datetime import datetime, date, timedelta
import time

import feedparser

from bs4 import BeautifulSoup
import urllib


if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


class JobIngestor:
    def __init__(self, keywords, locations, sites, time_span=10):
        self.keywords = keywords
        self.locations = locations
        self.sites = sites
        self.time_span = time_span
        self.seen_entries = set()

    def _generate_rss_url(self, location, site) -> str:
        site = site.replace("site:","").split("/")[0]
        base = "https://news.google.com/rss/search?q="
        cutoff_date = (datetime.now() - timedelta(days=self.time_span)).strftime("%Y-%m-%d")

        for keyword in self.keywords:
            query = f'"{keyword}" "{location}" jobs site:{site}'
            encoded_query = urllib.parse.quote_plus(query).replace("%20","+")

            yield f"{base}{encoded_query}&hl=es&gl=ES&ceid=ES:es"
            yield f"{base}{encoded_query}&hl=en&gl=ES&ceid=ES:en"

    def _parse_entry(self, entry, location, site) -> dict | None:
        title = entry.get("title", "Unknown")
        link = entry.get("link", "")
        published_raw = entry.published

        cutoff_date = datetime.now() - timedelta(days=self.time_span)#.strftime("%Y-%m-%d %H:%M:%S")

        try:
            published = pd.to_datetime(published_raw).strftime("%Y-%m-%d %H:%M:%S")
            if published.tz_localize(None) < cutoff_date.tz_localize(None):
                return None
        except:
            published = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "title": title,
            "link" : link,
            "published": published,
            "location": location,
            "platform": site.replace("site:","").split("/")[0],
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def execute_refinery(self):
        results = []
        
        for site in self.sites:
            for location in self.locations:
                for url in self._generate_rss_url(location, site):
                    try:
                        time.sleep(1) # Error handling for --- API rate limiting
                        feed = feedparser.parse(url)
                        
                        if feed.bozo: # Error handling for --- Malformed feed or parsing issues
                            raise Exception(f"⚠️ Error parsing feed: {feed.bozo_exception}")

                        for entry in feed.entries:
                            link = entry.link
                            if link not in self.seen_entries:
                                parsed = self._parse_entry(entry, location, site)

                                if parsed:
                                    results.append(parsed)
                                    self.seen_entries.add(link)
                    
                    except Exception as e:
                        raise e

        return results

@data_loader
def load_data_from_api(*args, **kwargs):
    
    ingestor = JobIngestor(
        keywords = kwargs.get('keywords', 
                            [
                                'Data Engineer',
                                'Data Practitioner'
                            ]),
        locations = kwargs.get('location', 
                            [
                                'Bizkaia', 
                                'Zamudio', 
                                'IDOM', 
                                'Bilbao', 
                                'Vizcaya', 
                                'Basque Country'
                            ]),
        sites = kwargs.get('site', 
                            [
                                'site:linkedin.com/jobs', 
                                'site:infojobs.net',
                                'site:indeed.com',
                                'site:hiring.cafe'
                            ]),
        time_span = kwargs.get('time_span', 10))

    data = ingestor.execute_refinery()
    if not data:
        return pd.DataFrame(columns=["title","link","published","location","platform","scraped_at"])
    df = pd.DataFrame(data)

    json_path = "/home/src/data/linkedin_insights.json"
    try: # Error handling for --- Environment issues 
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        df.to_json(json_path, orient="records", indent=4, force_ascii=False)
        print(f"✅ Successfully captured {len(df)} items.")
    except Exception as e:
        print(f"❌ Storage error: {e}") 

    return df


@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert isinstance(output, pd.DataFrame), "Output should be a pandas Dataframe"
    assert len(output) > 1 , 'The dataframe is empty, no data collected'
    # Check for expected columns
    expected_columns = {"title", "link", "published", "location", "platform", "scraped_at"}
    assert expected_columns.issubset(set(output.columns)), f"Missing expected columns: {expected_columns - set(output.columns)}"
    # Check for non-empty values in key columns
    for col in ["title", "link", "published"]:
        assert output[col].notnull().all(), f"Column '{col}' contains null values"
        assert (output[col].str.strip() != "").all(), f"Column '{col}' contains empty strings"
    # Check for non-empty values in the 'scraped_at' column
    assert output["scraped_at"].notnull().all(), f"Column 'scraped_at' contains null values"
    assert (output["scraped_at"].str.strip() != "").all(), f"Column 'scraped_at' contains empty strings"
    