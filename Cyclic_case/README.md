# Cyclistic Bike‑Share Analysis — Dashboard Project

## Transparency & AI Disclosure

In the interest of academic and professional honesty, the following should be noted:

- The **SQL queries** used to build the dashboard charts were written by me.
- The **Python data preparation script** (`analysis.py`) and **SQLite import script** (`import_to_db.py`) were written by me, then reviewed and optimized with the assistance of the DeepSeek AI agent.
- The **Metabase dashboard** was designed and assembled by me, based on the analytical insights derived from the data.
- The **database schema** and **table relationships** were designed by me
- The **readme** was created with the aid the DeepSeek AI agent and reviewed by me. 

---

## Overview

This project builds a complete analytical dashboard for Cyclistic, a Chicago‑based bike‑share company. The goal is to understand behavioral differences between casual riders and annual members, and to surface actionable insights that can drive a marketing campaign aimed at converting casual riders into members.

The project includes:
- A **15.8 million‑row** dataset loaded into a **normalized SQLite database**.
- A **Metabase dashboard** with four tabs covering rider behavior, temporal patterns, trip characteristics, and geographic hotspots.
- A set of **optimized SQL queries** that power the dashboard charts.
- A **clean, organized folder structure** on an internal SSD for fast query performance.

For a detailed step‑by‑step walkthrough, see the schema and architecture sections below.

---

## Deliverables

| File / Folder        | Description                                                                                                                   |
| :------------------- | :---------------------------------------------------------------------------------------------------------------------------- |
| `etl.py`        | Python script to load, clean, and transform the raw CSV data into a flat DataFrame.                                           |
| `importer.py`        | Python script to split the flat DataFrame into normalized tables (`rides`, `stations`, `coordinates`) and import into SQLite. |
| `Dashboard.pdf`        |  PDF containing dashboard                                                                               |
| `README.md`          | This file.                                                                                                                    |
| `cyclic_diagram.png` | Diagram representing the SQL tables.                                                                                          |

---

## Architecture Overview

| Component                     | Purpose                                                                                        |
| :---------------------------- | :--------------------------------------------------------------------------------------------- |
| **Raw CSV Data** (15.8M rows) | Original source.                                                                               |
| **Python (pandas)**           | Reads CSVs in chunks, cleans, filters, and adds computed columns (duration, distance, season). |
| **SQLite Database**           | Stores normalized tables on internal SSD for fast query performance.                           |
| **Metabase (BI Layer)**       | Connects to SQLite, runs SQL queries, and renders interactive charts.                          |
| **Dashboard**                 | Four tabs: Summary, Time Habits, Trip Behavior, and Geographic Insights.                       |

---

Performance Metrics

| Metric | Value |
| :--- | :--- |
| **Total rows loaded** | 15,819,921 |
| **Rows after cleaning** | ~15,500,000 |
| **Database file size** | 8.7 GB |
| **Unique stations** | ~500 (after aggregation) |
| **Pipeline runtime** | ~25 minutes (full ETL + import) |
| **Dashboard query time** | < 2 seconds on internal SSD with indexes |
