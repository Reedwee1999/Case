from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'you',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'social_media_pipeline',
    default_args=default_args,
    description='ETL + dbt pipeline for social media analytics',
    schedule_interval='@daily',
    catchup=False,
)

run_etl = BashOperator(
    task_id='run_pyspark_etl',
    bash_command='docker exec pyspark spark-submit --jars /home/jovyan/drivers/postgresql-42.7.3.jar /home/jovyan/work/etl.py',
    dag=dag,
)

run_dbt = BashOperator(
    task_id='run_dbt_marts',
    bash_command='docker exec dbt dbt run --profiles-dir /app --project-dir /app',
    dag=dag,
)

run_etl >> run_dbt
