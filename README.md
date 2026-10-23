# Daily Weather ETL & Analytics Pipeline

An automated ETL pipeline that pulls live weather data for five Indian cities from the Open-Meteo API, cleans it with Pandas, and loads it into PostgreSQL. Apache Airflow runs the pipeline daily.

## Architecture

```
Open-Meteo API -> extract.py -> raw JSON (data/raw/<city>/<date>.json)
                                      |
                              transform.py -> clean CSV (data/processed/<date>.csv)
                                      |
                                 load.py -> PostgreSQL (weather_readings)

Apache Airflow DAG (weather_etl_pipeline) runs extract -> transform -> load daily.
```

## Tech stack

Python, Pandas, PostgreSQL, Apache Airflow (CeleryExecutor), Docker, Docker Compose

## Key design decisions

- **Idempotent loads:** the table has a UNIQUE (city, reading_time) constraint and the load step uses `INSERT ... ON CONFLICT DO UPDATE`, so retries never create duplicates.
- **Raw data kept separately:** raw API responses are saved as city/date-partitioned JSON, so data can be reprocessed without calling the API again.
- **Separate infrastructure:** the project's PostgreSQL warehouse and Airflow's internal metadata database run in separate Docker Compose stacks.
- **Environment-aware config:** the database host is read from `DB_HOST`, so the same `load.py` works on a laptop (`localhost`) and inside Airflow containers (`host.docker.internal`).

## Project structure

```
weather-pipeline/
├── dags/weather_dag.py            # Airflow DAG
├── scripts/
│   ├── extract.py                 # API -> raw JSON
│   ├── transform.py               # raw JSON -> clean CSV
│   └── load.py                    # CSV -> PostgreSQL (upsert)
├── docker-compose.yml             # PostgreSQL warehouse (port 5433)
├── docker-compose-airflow.yaml    # Airflow stack (UI on port 8081)
├── .env.example                   # copy to .env and fill in
└── requirements.txt
```

## How to run

1. Clone the repo and create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set your own values.
3. Start the PostgreSQL warehouse:
   ```
   docker compose up -d
   ```
4. Run the steps manually (optional):
   ```
   python scripts\extract.py
   python scripts\transform.py
   python scripts\load.py
   ```
5. Run with Airflow:
   ```
   docker compose -f docker-compose-airflow.yaml -p weather-airflow up airflow-init
   docker compose -f docker-compose-airflow.yaml -p weather-airflow up -d
   ```
   Open http://localhost:8081 (login: airflow / airflow), unpause `weather_etl_pipeline`, and trigger it.

## Possible improvements

Data quality checks, cloud storage (S3) for raw files, failure alerts, dbt for transformations, and Spark for larger data volumes.
