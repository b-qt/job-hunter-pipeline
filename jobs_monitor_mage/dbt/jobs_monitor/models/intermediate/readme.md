# Intermediate Layer - The "Refinery" of Job Data

## 🌟 Vision
The purpose of this layeris to take raw, messy job data from the ingestion layer (Mage) and transform it into a structured, tested, and high-purity format ready for the business intelligence dashboard. 

---

## 🍽️ Functionality & Logic

### 1. Injestion to PostgreSQL
We have moved away from loose JSON files into a structured **PostgreSQL** landing zone. 
*   **Logic:** The Mage Data Exporter identifies the target schema and table via environment variables (`.env`).
*   **Integrity:** It utilizes an `APPEND` strategy to ensure we build a historical archive of the Northern Spain job market rather than just a snapshot of today.

### 2. The Alphanumeric Bouncer (Custom Macro)
To handle the "noise" of the internet (emojis, HTML artifacts, symbols), I developed a reusable logic component.
*   **File:** `macros/clean_alphanumeric.sql`
*   **Logic:** Uses a **Negative Regex Set** (`REGEXP_REPLACE`) to strip anything that isn't a standard letter, number, or space.
*   **Cultural Edge:** The logic is "Spanish-Aware," specifically preserving accents and the `ñ` which are semantic markers for local Bilbao/Gijón postings.

### 3. Data Integrity & "Purity" Tests
We don't trust the data; we verify it. I implemented a two-tier testing suite in **dbt**:
*   **Generic Tests:** Automated checks for `unique` links and `not_null` titles.
*   **Singular Integrity Test:** A bespoke SQL test specifically designed to verify that the `clean_alphanumeric` macro worked. It flags any titles that still contain "illegal" characters.

---

## 🛠️ Maintenance Guide

| Task | Command / Action | Why? |
| :--- | :--- | :--- |
| **Daily Refresh** | `dbt build` | Runs the logic and the bouncers (tests) in one shot. |
| **Adding a Site** | Update `src_postgres.yml` | To bring a new source (e.g., JobFluent) into the refinery. |
| **Fixing Typos** | Edit the Staging Model | Ensures the "Source of Truth" stays clean. |

---