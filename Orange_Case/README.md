
# Orange Egypt Data Engineering Task — Social Media Analytics Pipeline

## Transparency & AI Disclosure

In the interest of academic and professional honesty, the following should be noted:

- The **PySpark ETL script** (`etl.py`), **dbt models** (3 SQL files), **Airflow DAG** (`social_media_pipeline.py`), and **Docker configuration** (`docker-compose.yaml`, `Dockerfile`) were written by me, then **reviewed, debugged, and enriched with comments** using the **DeepSeek** AI agent.
- The **`README.md`** file and **schema documentation** were generated with the assistance of the AI agent and updated step-by-step throughout the project.
- The **PostgreSQL database** was run inside a Docker container on my **external hard drive** (`/Volumes/IDEP`), securely storing all raw data and aggregated marts.

---

## Overview

This project builds a **complete data engineering pipeline** for social media analytics. It extracts data from a large, nested JSON file (500+ MB), transforms it using **PySpark**, loads it into a **PostgreSQL** data warehouse, and builds analytical **data marts** using **dbt**. The entire workflow is orchestrated by **Apache Airflow** running inside a multi-container Docker environment.

For a detailed step-by-step walkthrough, see the schema documentation below.

---

## Project Files

| File / Folder | Description |
| :--- | :--- |
| `spark_code/etl.py` | Full PySpark ETL — extracts JSON, flattens nested structures, loads into PostgreSQL |
| `dags/social_media_pipeline.py` | Airflow DAG — orchestrates ETL + dbt execution daily |
| `dbt_project/models/*.sql` | dbt models — 3 data marts (user engagement, content performance, tag analysis) |
| `dbt_project/dbt_project.yml` | dbt project configuration |
| `dbt_project/profiles.yml` | PostgreSQL connection profile for dbt |
| `docker-compose.yaml` | Multi-container environment (Airflow, PySpark, dbt, PostgreSQL) |
| `Dockerfile` | Custom Airflow image — includes Docker CLI + dbt |
| `drivers/postgresql-42.7.3.jar` | PostgreSQL JDBC driver for PySpark |
| `README.md` | This file |

---

## Prerequisites

- **Docker Desktop** installed and running

---


### 1. Start the environment

```bash
cd /your/path/here
./init.sh
```

### 2. Check your JSON file

Ensure your `social_media_info.json` file is inside the `/home/jovyan/work/social_media_info.json` (mounted from `./spark_code`), note that it *will* be in a zip.

```bash
cp datasets/social_media_info.json spark_code/
```

### 4. Run the pipeline via Airflow (recommended)

1. Open Airflow UI: [http://localhost:8080](http://localhost:8080)
   - Username: `airflow`
   - Password: `airflow`
2. Find the DAG `social_media_pipeline`.
3. Toggle the DAG "On" and click the "Play" button to trigger a manual run.
4. Monitor the logs for `run_pyspark_etl` and `run_dbt_marts` — both should turn green.

### 5. Or run manually (alternative)

```bash
# Run PySpark ETL
docker exec pyspark spark-submit --jars /home/jovyan/drivers/postgresql-42.7.3.jar /home/jovyan/work/etl.py

# Run dbt models
docker exec dbt dbt run --profiles-dir /app --project-dir /app
```

### 6. Verify the results

Connect to the PostgreSQL warehouse:

```bash
docker exec -it postgres_warehouse psql -U warehouse -d warehouse
```

Run queries to inspect the data marts:

```sql
\dt
SELECT * FROM tag_analysis_mart ORDER BY post_count DESC LIMIT 10;
SELECT * FROM user_engagement_mart LIMIT 5;
SELECT * FROM content_performance_mart LIMIT 5;
```

---

## Database Schema

The schema is built in two distinct layers to balance **storage efficiency** and **analytical performance**:

- **Raw tables (`users`, `posts`, `comments`)** are normalised to eliminate redundancy (e.g., user details are stored once) and to closely mirror the nested JSON structure. Tags are flattened directly into `posts` as strings.
- **Data marts** are denormalised and pre‑aggregated to serve specific business questions (user engagement, content performance, tag popularity). This shifts complex `GROUP BY` and `COUNT` operations from ad‑hoc queries to scheduled dbt builds, making dashboards and reports significantly faster.

The data warehouse globally consists of **six tables** in the `public` schema:

### Raw Tables (Loaded by PySpark)

| Table      | Description                                                         |
| ---------- | ------------------------------------------------------------------- |
| `users`    | User‑level attributes (65,000 rows)                                 |
| `posts`    | Post‑level data incl. reaction counts and tags array (324,508 rows) |
| `comments` | Individual comment events (813,211 rows)                            |

### Data Marts (Built by dbt)

| Table                      | Description                                                           |
| -------------------------- | --------------------------------------------------------------------- |
| `user_engagement_mart`     | Aggregated per user — total posts, shares, reactions                  |
| `content_performance_mart` | Aggregated per post — total reactions, comments, engagement score     |
| `tag_analysis_mart`        | Exploded tags — rank of most used tags by unique post count           |


---

## Architecture Overview

| Component               | Purpose                                                                                                    |
| ----------------------- | ---------------------------------------------------------------------------------------------------------- |
| **PySpark** (Jupyter)   | Reads the multi‑line JSON, flattens nested structures, and loads raw tables into PostgreSQL.               |
| **PostgreSQL** (`postgres_warehouse`) | Data warehouse storing raw tables and data marts.                             |
| **PostgreSQL** (`postgres`)           | Airflow metadata database — stores DAG runs, task states, and connections.    |
| **dbt**                 | Transforms raw tables into aggregated analytical marts using SQL.                                         |
| **Airflow**             | Orchestrates the ETL (`spark-submit`) and dbt tasks on a daily schedule.                                  |
| **Docker Compose**      | Multi‑container environment connecting all services, with persistent volumes for data.                    |
| **Docker Socket Mount** | `/var/run/docker.sock` is mounted into Airflow, allowing it to run `docker exec` commands on the host.    |

---

## Deliverables

This repository contains everything required for the task:

1. **Data Model** – Documented in the schema section above and in `dbt_project/models/sources.yml`.
2. **Airflow DAG** – `dags/social_media_pipeline.py`
3. **PySpark Script** – `spark_code/etl.py`
4. **dbt Models** – 3 `.sql` files in `dbt_project/models/`
5. **Documentation** – This README file.
6. **Environment Configuration** – `docker-compose.yaml` and `Dockerfile`.

---

## Quick Start

### 1. Navigate to the project directory

```bash
cd /Volumes/IDEP/Case-2
```

### 2. Start the Docker environment

```bash
docker compose up -d
```

Wait 30 seconds for all containers to become healthy.

### 3. Trigger the Airflow DAG

1. Open your browser and go to [http://localhost:8080](http://localhost:8080)
2. Log in with username `airflow` and password `airflow`
3. Find the DAG `social_media_pipeline`
4. Toggle it "On" and click the "Play" button to trigger a manual run

### 4. Verify the results

```bash
docker exec -it postgres_warehouse psql -U warehouse -d warehouse
```

Then:

```sql
\dt
SELECT * FROM tag_analysis_mart ORDER BY post_count DESC LIMIT 10;
```


---

## Airflow DAG 
`dags/social_media_pipeline.py`

### What it does

- **Task 1** (`run_pyspark_etl`): Runs the PySpark ETL via `docker exec`.
- **Task 2** (`run_dbt_marts`): Runs dbt models via `docker exec`.
- **Dependency**: Task 2 runs only after Task 1 completes successfully.
- **Schedule**: Runs daily at midnight (`@daily`), but can be manually triggered.

