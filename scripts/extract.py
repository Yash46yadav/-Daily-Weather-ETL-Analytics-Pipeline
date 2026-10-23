import requests
import json
from datetime import datetime
from pathlib import Path

# City coordinates (latitude, longitude)
CITIES = {
    "jaipur": {"lat": 26.9124, "lon": 75.7873},
    "delhi": {"lat": 28.6139, "lon": 77.2090},
    "mumbai": {"lat": 19.0760, "lon": 72.8777},
    "bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "kolkata": {"lat": 22.5726, "lon": 88.3639},
}

# This file lives in scripts/, so go up one level to reach the project root,
# then into data/raw. Using an absolute path (not a relative one) matters
# later in Phase 5, when Airflow runs this script from a different folder.
RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def fetch_weather(lat: float, lon: float) -> dict:
    """Call the Open-Meteo API and return the current weather as a dict."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "timezone": "auto",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()  # raises an error if the API call failed
    return response.json()


def save_raw_data(city_name: str, data: dict, run_date: str) -> None:
    """Save the raw API response as-is, one JSON file per city per day."""
    city_folder = RAW_DATA_DIR / city_name
    city_folder.mkdir(parents=True, exist_ok=True)
    file_path = city_folder / f"{run_date}.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {file_path}")


def main():
    run_date = datetime.now().strftime("%Y-%m-%d")
    print(f"Starting extraction for {run_date}")

    for city_name, coords in CITIES.items():
        try:
            data = fetch_weather(coords["lat"], coords["lon"])
            save_raw_data(city_name, data, run_date)
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {city_name}: {e}")

    print("Extraction complete.")


if __name__ == "__main__":
    main()