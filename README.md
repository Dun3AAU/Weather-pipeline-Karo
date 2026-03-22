# Automated Weather Pipeline

This project automatically collects weather forecasts for three locations and generates a bilingual (English + Polish) poem based on the data.

## Locations
- Miastko, Poland (place of birth)
- Denver, USA (previous residence)
- Aalborg, Denmark

## How it works

1. `fetch.py`
   - Fetches tomorrow’s weather from Open-Meteo API
   - Stores the data in a SQLite database (`weather.db`)

2. `poem.py`
   - Reads weather data from the database
   - Uses Groq API to generate a bilingual poem
   - Saves output to `docs/index.html`

3. GitHub Actions
   - Runs the pipeline automatically every day at 20:00
   - Updates the weather data and poem

4. GitHub Pages
   - Displays the result as a webpage


## How to run locally

```bash
pip install -r requirements.txt
python fetch.py
python poem.py