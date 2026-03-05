import pandas as pd

import json
import os

from datetime import datetime, date, timedelta
import time
import urllib

import feedparser

from bs4 import BeautifulSoup


if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

class JobMarketIngestor:
    """
    An ingestor to handle multi-source job feeds,
    it encapsulates configuration and provides clean abstraction for scaling.
    """
    def __init__(self, keywords, locations, sites, time_span=10):
        self.keywords = keywords
        self.locations = locations
        self.sites = sites
        self.time_span = time_span
        self.start_date = (datetime.now() - timedelta(days=time_span)).strftime('%Y-%m-%d')
        self.seen_entries = set()

    def _generate_rss_url(self, location, site):
        """ Builds localized endpoints"""
        
        base = "https://news.google.com/rss/search?q="
        
        for keyword in self.keywords:
            query = f'"{keyword}" {location} {site} after:{self.start_date}'
            encoded_query = urllib.parse.quote_plus(query)
        
            yield f"{base}{encoded_query}&hl=es&gl=ES&ceid=ES:es"
            yield f"{base}{encoded_query}&hl=en&gl=ES&ceid=ES:en"

    def _parse_entry(self, entry, location, site):
        """Extract metadata from raw entry"""
        title = entry.get("title","Unknown")   
        published_raw = entry.get("published")
        cutoff_date = (datetime.now() - timedelta(days=time_span)).strftime('%Y-%m-%d')
        try:
            published = pd.to_datetime(published_raw).strftime("%Y-%m-%d %H:%M:%S")
            if published < cutoff_date:
                return None
        except:
            published = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #?platform ?company

        return {
            "title":title,
            "link": entry.link,
            "published": published,
            "location": location,
            "platform": site.replace("site",""),
            "scraped-at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def execute_refinery(self):
        results = []
        
        for site in self.sites:
            for location in self.locations:
                for url in self._generate_rss_url(location, site):
                    time.sleep(1)
                    feed = feedparser.parse(url)
                    print(f"📡 Refining: {location} | {site.replace('site:','')} | {len(feed.entries)} | {url}")

                    if not feed.entries:
                        continue

                    for entry in feed.entries:
                        link = entry.link
                        if link not in self.seen_entries:
                            parsed = self._parse_entry(entry, location, site)

                            if parsed:
                                results.append(self._parse_entry(entry, location, site))
                                self.seen_entries.add(link)
        
        return results


@data_loader
def load_data_from_api(*args, **kwargs):
    # 1. Instantiate 
    ingestor = JobMarketIngestor(
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
                        'site:hiring.cafe'
                      ]),
        time_span=10
    )

    #2. Run the refiner
    data = ingestor.execute_refinery()

    #3. handle output
    if not data:
        print("⚠️ No new jobs found.")
        return pd.DataFrame(columns = ["title","link","published","location","scraped-at"])
    df = pd.DataFrame(data)

    #4. Persistence
    json_path = "/data/linkedin_insights.json"
    try:
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        df.to_json(
            json_path,
            orient="records",
            indent=4,
            force_ascii=False
        )
        print(f"✅ Successfully captured {len(df)} items.")
    except Exception as e:
        print(f"❌ Failed to save JSON: {e}")

    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
    assert isinstance(output, pd.DataFrame), "Output should be a dataframe"
