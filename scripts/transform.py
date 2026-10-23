import json
import pandas as pd
from datetime import datetime
from pathlib import Path

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

# WMO weather codes -> human-readable description (common subset)
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}


def load_raw_file(city_name: str, run_date: str) -> dict | None:
    """Read one city's raw JSON file for a given date. Returns None if missing."""
    file_path = RAW_DATA_DIR / city_name / f"{run_date}.json"
    if not file_path.exists():
        print(f"Skipping {city_name}: no raw file found for {run_date}")
        return None
    with open(file_path, "r") as f:
        return json.load(f)


def extract_fields(city_name: str, raw_data: dict) -> dict:
    """Pull out only the fields we care about, and flatten them into one row."""
    current = raw_data["current"]
    weather_code = current.get("weather_code")
    return {
        "city": city_name.title(),
        "timestamp": current["time"],
        "temperature_c": current.get("temperature_2m"),
        "humidity_pct": current.get("relative_humidity_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "weather_code": weather_code,
        "weather_description": WEATHER_CODES.get(weather_code, "Unknown"),
    }


def transform(run_date: str) -> pd.DataFrame:
    """Read every city's raw file for run_date and return one clean DataFrame."""
    city_folders = [p.name for p in RAW_DATA_DIR.iterdir() if p.is_dir()]

    rows = []
    for city_name in city_folders:
        raw_data = load_raw_file(city_name, run_date)
        if raw_data is not None:
            rows.append(extract_fields(city_name, raw_data))

    return pd.DataFrame(rows)


def save_processed_data(df: pd.DataFrame, run_date: str) -> Path:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = PROCESSED_DATA_DIR / f"{run_date}.csv"
    df.to_csv(file_path, index=False)
    return file_path


def main():
    run_date = datetime.now().strftime("%Y-%m-%d")
    print(f"Transforming data for {run_date}")

    df = transform(run_date)

    if df.empty:
        print("No data found — did you run extract.py for this date yet?")
        return

    print(df.to_string(index=False))

    file_path = save_processed_data(df, run_date)
    print(f"\nSaved clean data to: {file_path}")


if __name__ == "__main__":
    main()