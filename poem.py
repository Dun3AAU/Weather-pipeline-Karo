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
            <td>{temperature} °C</td>
            <td>{humidity} %</td>
            <td>{wind_speed} km/h</td>
        </tr>
        """

    # ---- SPLIT POEM (case-insensitive) ----
    split_keywords = ["Wersja polska", "Wersja Polska", "Polish Version", "Polish:"]
    english_part = poem
    polish_part = ""

    for keyword in split_keywords:
        if keyword.lower() in poem.lower():
            idx = poem.lower().index(keyword.lower())
            english_part = poem[:idx]
            polish_part = poem[idx + len(keyword):]
            break

    # ---- CLEAN HELPER ----
    def clean(text):
        for marker in [
            "**English Version**", "English Version:", "English Version",
            "**Wersja Polska**", "Wersja Polska:", "Wersja Polska",
            "**Wersja polska**", "Wersja polska:", "Wersja polska",
            "Polish Version:", "Polish Version", "Polish:", "Version", "**"
        ]:
            text = text.replace(marker, "")
        if "Note:" in text:
            text = text.split("Note:")[0]
        text = text.strip().lstrip(":")
        return text.strip()

    english_part = clean(english_part)
    polish_part = clean(polish_part)

    # ---- HTML ----
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weather Poem</title>

<style>
body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #e0f2fe, #fdf4ff);
    color: #1f2937;
}}

.container {{
    max-width: 900px;
    margin: 40px auto;
    padding: 20px;
}}

.card {{
    background: white;
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}}

h1 {{
    text-align: center;
    color: #2563eb;
    margin-top: 0;
}}

h2 {{
    color: #7c3aed;
    margin-top: 0;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 16px;
}}

th, td {{
    padding: 12px;
    text-align: left;
}}

th {{
    background: #2563eb;
    color: white;
}}

tr:nth-child(even) {{
    background: #f1f5f9;
}}

.poem-box {{
    background: #f8fafc;
    padding: 16px;
    border-radius: 12px;
    margin-top: 10px;
    white-space: pre-wrap;
    line-height: 1.6;
    border-left: 5px solid #7c3aed;
}}

.section-title {{
    text-align: center;
    margin: 26px 0 18px 0;
}}

.section-title h2 {{
    color: #2563eb;
    margin: 0;
}}

.footer {{
    text-align: center;
    color: #64748b;
}}
</style>
</head>

<body>

<div class="container">

    <div class="card">
        <h1>Tomorrow's Weather Forecast</h1>
        <p><strong>Date:</strong> {forecast_date}</p>

        <table>
            <tr>
                <th>Location</th>
                <th>Temperature</th>
                <th>Humidity</th>
                <th>Wind Speed</th>
            </tr>
            {table_rows}
        </table>
    </div>

    <div class="section-title">
        <h2> Daily Poems</h2>
    </div>

    <div class="card">
        <h2>🇬🇧 English Poem</h2>
        <div class="poem-box">{english_part}</div>
    </div>

    <div class="card">
        <h2>🇵🇱 Polish Poem</h2>
        <div class="poem-box">{polish_part}</div>
    </div>

    <p class="footer">
        Updated daily via GitHub Actions
    </p>

</div>

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