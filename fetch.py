import sqlite3
import requests

locations = [
    {"name": "Miastko", "lat": 54.017, "lon": 16.983},
    {"name": "Denver", "lat": 39.7392, "lon": -104.9850},
    {"name": "Aalborg", "lat": 57.050, "lon": 9.917},
]

db_name = "weather.db"


def create_table():
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            location TEXT,
            forecast_date TEXT,
            temperature REAL,
            humidity REAL,
            wind_speed REAL
        )
    """)

    conn.commit()
    conn.close()


def fetch_weather_for_city(city):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "daily": "temperature_2m_max,relative_humidity_2m_mean,wind_speed_10m_max",
        "forecast_days": 2,
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    data = response.json()

    # index 1 = tomorrow
    forecast_date = data["daily"]["time"][1]
    temperature = data["daily"]["temperature_2m_max"][1]
    humidity = data["daily"]["relative_humidity_2m_mean"][1]
    wind_speed = data["daily"]["wind_speed_10m_max"][1]

    return (city["name"], forecast_date, temperature, humidity, wind_speed)


def save_to_db(row):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO weather (location, forecast_date, temperature, humidity, wind_speed)
        VALUES (?, ?, ?, ?, ?)
    """, row)

    conn.commit()
    conn.close()


def main():
    create_table()

    # optional: remove old rows so database stays clean
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("DELETE FROM weather")
    conn.commit()
    conn.close()

    for city in locations:
        row = fetch_weather_for_city(city)
        save_to_db(row)
        print("Saved:", row)


if __name__ == "__main__":
    main()