from datetime import datetime
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/weather_pipeline"

default_args = {
    "retries": 1,
}

with DAG(
    dag_id="weather_etl_pipeline",
    description="Daily weather ETL: extract from Open-Meteo, transform, load into Postgres",
    start_date=datetime(2026, 7, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["weather", "etl"],
) as dag:

    extract = BashOperator(
        task_id="extract",
        bash_command=f"python {PROJECT_DIR}/scripts/extract.py",
    )

    transform = BashOperator(
        task_id="transform",
        bash_command=f"python {PROJECT_DIR}/scripts/transform.py",
    )

    load = BashOperator(
        task_id="load",
        bash_command=f"python {PROJECT_DIR}/scripts/load.py",
    )

    extract >> transform >> load