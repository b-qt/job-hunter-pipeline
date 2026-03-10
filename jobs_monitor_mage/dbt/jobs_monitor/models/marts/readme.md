# 🏅 The Marts Layer: Business Intelligence & Insights

### 🌟 Vision
The Marts layer is the final destination for our data refinery. This is where high-purity, tested data is structured into "Fact" tables designed for consumption by our **Streamlit Dashboard**. While our staging and intermediate layers focus on cleaning the "sludge," the Marts focus on answering the big questions that drive business decisions:
* Where are the most active job markets in Spain?
* Which platforms are dominating the hiring landscape?
* What is the distribution of job levels and work modes?

---

### 🍽️ Functional Breakdown (The "Dining Room")

#### 1. `fct_job_postings` (The Feed)
*   **Logic:** Acts as the primary search table. It preserves the granularity of individual postings but presents them in a "User-First" format.
*   **Business Value:** Allows us to see the exact headlines from companies in real-time.
*   **Ordering:** Strictly ordered by `published_date desc` to ensure the "Freshest Ingredients" are always at the top of the menu.

#### 2. `fct_market_insights` (The Aggregator)
*   **Logic:** Aggregates data across four critical dimensions:
    1.  **Region:** Bilbao/Vizcaya vs. Gijón/Asturias vs. Other.
    2.  **Platform:** Where is the "Local Steel" (InfoJobs) vs. "Global Tech" (LinkedIn)?
    3.  **Job Level:** The distribution of Junior, Mid, and Senior roles.
    4.  **Work Mode:** Remote vs. Onsite vs. Hybrid.
*   **Business Value:** Powers the charts that show us where the market is growing and where it is stagnating.

---

### ⚙️ Technical Architecture & Maintenance

| Feature | Implementation | Why? |
| :--- | :--- | :--- |
| **Materialization** | `TABLE` | We chose tables over views here to provide **Low Latency** for the dashboard. The compute cost happens once during the dbt run, not every time a user refreshes the page. |

#### How to maintain this layer:
*   **Refresh Strategy:** Triggered automatically via **Mage** every 6 hours.
*   **Schema Changes:** If a new category is added (e.g., "Sustainability Specialist"), update the `CASE` statements in the **Intermediate Layer**, and this Mart will automatically reflect the change.
*   **Testing:** Ensure that the tests in the intermediate layer are passing, as they directly impact the quality of data in the Marts. Additionally, consider adding tests specific to the Marts to validate aggregation logic and ensure no duplicates or null values in critical dimensions.