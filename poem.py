import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

db_name = "weather.db"
docs_path = Path("docs")
docs_path.mkdir(exist_ok=True)


def read_weather():
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute("SELECT location, forecast_date, temperature, humidity, wind_speed FROM weather")
    rows = cur.fetchall()

    conn.close()
    return rows


def generate_poem(rows):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "Groq API key is missing."

    weather_text = ""
    for row in rows:
        location, forecast_date, temperature, humidity, wind_speed = row
        weather_text += (
            f"{location}: temperature {temperature}°C, "
            f"humidity {humidity}%, "
            f"wind speed {wind_speed} km/h\n"
        )

    prompt = f"""
Write a short poem about tomorrow's weather in these three places.

Requirements:
- compare the weather in the three locations
- describe the differences
- suggest where it would be nicest to be tomorrow
- write it in two languages: English and Polish
- keep it creative and nice

Weather data:
{weather_text}
"""

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def save_html(rows, poem):
    forecast_date = rows[0][1]

    table_rows = ""
    for row in rows:
        location, _, temperature, humidity, wind_speed = row
        table_rows += f"""
        <tr>
            <td>{location}</td>
            <td>{temperature}</td>
            <td>{humidity}</td>
            <td>{wind_speed}</td>
        </tr>
        """

    html = f"""
    <html>
    <head>
        <title>Weather Poem</title>
    </head>
    <body>
        <h1>Tomorrow's Weather</h1>
        <p><b>Date:</b> {forecast_date}</p>

        <table border="1" cellpadding="8">
            <tr>
                <th>Location</th>
                <th>Temperature</th>
                <th>Humidity</th>
                <th>Wind Speed</th>
            </tr>
            {table_rows}
        </table>

        <h2>Poem</h2>
        <pre>{poem}</pre>
    </body>
    </html>
    """

    with open(docs_path / "index.html", "w", encoding="utf-8") as f:
        f.write(html)


def main():
    rows = read_weather()
    poem = generate_poem(rows)
    save_html(rows, poem)
    print("Poem and HTML saved.")


if __name__ == "__main__":
    main()