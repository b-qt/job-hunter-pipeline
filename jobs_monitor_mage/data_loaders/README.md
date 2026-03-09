# 🏗️ Job Market Ingestor: Documentation

## 🌟 Overview
The `JobMarketRefinery` is a Python-based data ingestion engine designed to monitor the Spanish IT market. It bypasses the traditional "walled gardens" of job boards by utilizing a Google News RSS loophole to find indexed job postings.

## 🍽️ Core Functionality
The ingestor follows an **Object-Oriented (OOP)** structure to ensure the code is modular, testable, and "Pure."

### 1. Multi-Source Looping
Unlike a single-search script, this engine cycles through a list of **synonyms** (e.g., Bizkaia vs. Vizcaya) and **platforms** (LinkedIn, InfoJobs, Indeed). Each combination gets its own dedicated "slot" in the search results, ensuring maximum recall.

### 2. Semantic Deduplication
Because the same job often appears on multiple sites or in different languages (Spanish vs. English feeds), the engine uses a **Set-based Registry**. It identifies jobs by their `link`, preventing the duplicates from reaching the database.

### 3. Date Purity
The ingestor implements a strict `time_span` filter. It calculates a `cutoff_date` and automatically ignores any "stale" job postings that are older than the specified limit.

---

## 🛠️ Usage

### Configuration Parameters
These variables are set in the `load_data_from_api` block and can be overridden via Mage UI `kwargs`:

*   **`keywords`**: List of job titles (e.g., `['Data Engineer', 'Analytics Engineer']`).
*   **`location`**: Target regions or companies (e.g., `['Bilbao', 'IDOM']`).
*   **`site`**: Targeted job boards using Google's `site:` operator.
*   **`time_span`**: How many days back to look (Default: `10`).

### Execution
The main entry point is the `execute_refinery()` method. 
1.  **URL Generation:** Generates localized RSS URLs for both Spanish and English versions.
2.  **Polite Fetching:** Implements a `time.sleep(1)` to respect server rate limits (Sustainable AI).
3.  **Parsing:** Converts raw XML into a cleaned dictionary.
4.  **Persistence:** Saves the final unique batch into `/home/src/data/linkedin_insights.json`.

---

## 🔧 Maintenance & Troubleshooting

| Common Issue | The Bouncer's Fix |
| :--- | :--- |
| **TypeError (Date comparison)** | Ensure `published` is converted to a `datetime` object before comparing it to `cutoff_date`. |
| **Missing Columns** | If `scraped_at` is missing, check for the common "scarped" typo in the `_parse_entry` dictionary. |
| **Empty Results** | Google may have not indexed the jobs yet. Increase the `time_span`. |
| **Permission Denied** | Run `chmod -R 777 data/` to ensure the Docker container can write the JSON file. |