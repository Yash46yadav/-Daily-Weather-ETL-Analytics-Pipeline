import os
import pandas as pd
import psycopg2
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

load_dotenv(PROJECT_ROOT / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": 5433,  # matches the "5433:5432" mapping in docker-compose.yml
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS weather_readings (
    id SERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    reading_time TIMESTAMP NOT NULL,
    temperature_c NUMERIC,
    humidity_pct NUMERIC,
    wind_speed_kmh NUMERIC,
    weather_code INTEGER,
    weather_description TEXT,
    loaded_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (city, reading_time)
);
"""

UPSERT_SQL = """
INSERT INTO weather_readings (
    city, reading_time, temperature_c, humidity_pct,
    wind_speed_kmh, weather_code, weather_description
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (city, reading_time)
DO UPDATE SET
    temperature_c = EXCLUDED.temperature_c,
    humidity_pct = EXCLUDED.humidity_pct,
    wind_speed_kmh = EXCLUDED.wind_speed_kmh,
    weather_code = EXCLUDED.weather_code,
    weather_description = EXCLUDED.weather_description,
    loaded_at = now();
"""


def load_processed_csv(run_date: str) -> pd.DataFrame:
    file_path = PROCESSED_DATA_DIR / f"{run_date}.csv"
    if not file_path.exists():
        raise FileNotFoundError(f"No processed file for {run_date} — run transform.py first.")
    return pd.read_csv(file_path)


def ensure_table_exists(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)
    conn.commit()


def upsert_rows(conn, df: pd.DataFrame) -> None:
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute(UPSERT_SQL, (
                row["city"],
                row["timestamp"],
                row["temperature_c"],
                row["humidity_pct"],
                row["wind_speed_kmh"],
                int(row["weather_code"]) if pd.notna(row["weather_code"]) else None,
                row["weather_description"],
            ))
    conn.commit()


def main():
    run_date = datetime.now().strftime("%Y-%m-%d")
    print(f"Loading data for {run_date}")

    df = load_processed_csv(run_date)

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        ensure_table_exists(conn)
        upsert_rows(conn, df)
        print(f"Loaded {len(df)} rows into weather_readings.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
    