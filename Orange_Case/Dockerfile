# Use the official Airflow image as base
FROM apache/airflow:2.9.1

# Switch to root to install system packages
USER root

# Install Docker CLI (for Airflow to run docker exec)
RUN apt-get update && \
    apt-get install -y --no-install-recommends docker.io && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch to airflow user to install Python packages
USER airflow

# Install dbt (this must be run as the airflow user)
RUN pip install dbt-postgres==1.5.0

# Switch back to airflow user (already there, but kept for clarity)
USER airflow