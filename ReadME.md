# 📰 (Northern) Spain Job Monitor 2026

![Status](https://img.shields.io/badge/Status-Live%20Refinery-success?style=for-the-badge&logo=statuspage)
![Market](https://img.shields.io/badge/Focus-Bilbao%20%26%20Gijón-blue?style=for-the-badge&logo=googlemaps)
![Orchestration](https://img.shields.io/badge/Orchestration-Mage.ai-green?style=for-the-badge&logo=python)
![DBT](https://img.shields.io/badge/Transformation-dbt-orange?style=for-the-badge&logo=dbt)
![Visualization](https://img.shields.io/badge/Visualization-Streamlit-red?style=for-the-badge&logo=streamlit)


> **"Turning the noise of the Spanish market into high-purity insights."**

---

### 🌟 The Vision
In a world of information overload, this project acts as a **Digital Refinery**. It automatically monitors the pulse of the Spanish news cycle and the tech job market (specifically for my upcoming move to **Bilbao**), using AI to distinguish between "Market Noise" and "Market Mood."

---

### 🍽️ The "Data Kitchen" (How it works)
*For the non-techies: Imagine a high-end restaurant in the 22@ district.*

<details>
<summary><b>Step 1: The Ingestion (The Head Chef) 👨‍🍳</b></summary>
Our system goes to the markets (LinkedIn, InfoJobs, Google News) every 6 hours to find the freshest headlines.
</details>

<details>
<summary><b>Step 2: The Transformation (The Bouncer) 🕴️</b></summary>
Using <b>dbt</b>, we run 13 different quality tests. We remove duplicates and fix messy dates. If the data isn't "Pure" (per 1 Timothy 4:12), it doesn't get served.
</details>

<details>
<summary><b>Step 3: The Visualization (The Waiter) 🍷</b></summary>
A clean <b>Streamlit</b> dashboard serves the final insights on a silver platter.
</details>

---

### 🛠️ The Tech Stack (The Machinery)

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Automation** | **Mage.ai** | The heartbeat of the factory. |
| **Integrity** | **dbt** | Ensuring every row is tested and unique. |
| **Storage** | **PostgreSQL** | Fast, sustainable, local-first database. |
| **Interface** | **Streamlit** | Turning data into a story. |

---

### 💡 Objective Comparison: The Value Add

> "Why did I build this instead of just using a spreadsheet?"

*   **⚡ Speed:** Manual checking takes hours. This takes **milliseconds**.
*   **⚖️ Integrity:** Spreadshots have human bias. Our **dbt-tests** ensure 100% logic consistency.
*   **🌍 Scalability:** This system can monitor all of Spain, not just the North, with zero extra effort.
*   **🌱 Sustainability:** Built with a **Lean Docker** footprint to minimize compute waste.

---

### 🚀 Launch the Refinery
If you want to see the pipes under the floorboards:

1.  **Clone the Repo**
2.  **Start the Container:**
    ```bash
    docker-compose up -d
    ```
3.  **Check the Dashboard:** `localhost:8501`

---

### 🏛️ Architect's Note
> This project represents a commitment to **Ethics in Engineering** built in the winter of 2026 in Barcelona as a strategic bridge to the industrial powerhouses of **Northern Spain**.

<sub> 
Built with ☕ in :blossom: BCN ... Relocating to 🌲 Bilbao soon.
</sub>

---


