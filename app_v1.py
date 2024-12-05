import streamlit as st
import datetime
import pickle
import numpy as np
import requests
import sklearn

# Modelle laden
def load_model(model_path):
    with open(model_path, 'rb') as file:
        return pickle.load(file)

model_with_weather = load_model("./finalized_model_with_weather.sav")
model_without_weather = load_model("./finalized_model_without_weather.sav")

st.set_page_config(
    page_title="Stadium Capacity Prediction",
    page_icon="🏟️",
    layout="wide"
)

st.title("🏟️ Stadium Capacity Prediction App")
st.markdown("🎉⚽ This app predicts stadium capacity utilization.")

# Eingrenzung der Teams und Wettbewerbe
available_home_teams = ['FC Sion', 'FC St. Gallen', 'FC Winterthur', 'FC Zürich',
                        'BSC Young Boys', 'FC Luzern', 'Lausanne-Sport', 'Servette FC',
                        'FC Basel', 'FC Lugano', 'Grasshoppers', 'Yverdon Sport']
available_away_teams = available_home_teams + ['Unknown']
available_competitions = ['Super League', 'UEFA Conference League', 'Swiss Cup', 
                          'UEFA Europa League', 'UEFA Champions League']

home_team = st.selectbox("Home Team:", available_home_teams)
competition = st.selectbox("Competition:", available_competitions)
if competition == "Super League":
    away_team = st.selectbox("Away Team:", available_home_teams)
elif competition == "Swiss Cup":
    away_team = st.selectbox("Away Team:", available_away_teams)
else:
    away_team = "Unknown"

if competition == "Super League":
    matchday = st.slider("Matchday:", min_value=1, max_value=36, step=1)
else:
    matchday = st.radio("Matchday Type:", options=["Group", "Knockout"])

match_date = st.date_input("Match Date:", min_value=datetime.date.today())
# Uhrzeit auswählen
match_time = st.time_input(
    "Match Time:",
    value=datetime.time(15, 30),  # Standardwert auf 15:30 setzen
    help="Select the match time in HH:MM format"
)

















# home_team

import requests
import streamlit as st

# Wetterdaten abrufen
def get_weather_data(latitude, longitude, match_date, match_time):
    # Open-Meteo API-URL mit nur den relevanten Parametern
    api_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}&start_date={match_date}&end_date={match_date}"
        f"&hourly=temperature_2m,weathercode"
        f"&timezone=auto"  # Automatische Zeitzone
    )

    try:
        # API-Anfrage senden
        response = requests.get(api_url)
        response.raise_for_status()
        
        # JSON-Antwort parsen
        weather_data = response.json()

        # Erste Zahl der Uhrzeit als Index verwenden
        match_hour = match_time.hour  # Holt nur die Stunde aus der Zeit

        # Temperatur und Wettercode zum Match-Zeitpunkt abrufen
        hourly_data = weather_data['hourly']
        temperature_at_match = hourly_data['temperature_2m'][match_hour]
        weather_code_at_match = hourly_data['weathercode'][match_hour]
        if weather_code_at_match in [0]:
            weather_condition = "Clear or mostly clear"
        elif weather_code_at_match in [1, 2, 3]:
            weather_condition = "Partly cloudy"
        elif weather_code_at_match in [61, 63, 65, 80, 81, 82]:
            weather_condition = "Rainy"
        elif weather_code_at_match in [51, 53, 55]:
            weather_condition = "Drizzle"
        elif weather_code_at_match in [71, 73, 75, 85, 86, 77]:
            weather_condition = "Snowy"
        else:
            weather_condition = "Unknown"

        # Wetterdetails anzeigen
        st.write(f"Temperature at {match_time}: {temperature_at_match}°C")
        st.write(f"Weather at {match_time}: {weather_condition}")
        return temperature_at_match, weather_condition
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch weather data: {e}")
        return None, None


# Koordinaten der Stadien
stadium_coordinates = {
    'FC Sion': {'stadium': 'Stade de Tourbillon', 'latitude': 46.233333, 'longitude': 7.376389},
    'FC St. Gallen': {'stadium': 'Kybunpark', 'latitude': 47.408333, 'longitude': 9.310278},
    'FC Winterthur': {'stadium': 'Stadion Schützenwiese', 'latitude': 47.505278, 'longitude': 8.724167},
    'FC Zürich': {'stadium': 'Letzigrund', 'latitude': 47.382778, 'longitude': 8.504167},
    'BSC Young Boys': {'stadium': 'Stade de Suisse', 'latitude': 46.963056, 'longitude': 7.464722},
    'FC Luzern': {'stadium': 'Swissporarena', 'latitude': 47.035833, 'longitude': 8.310833},
    'Lausanne-Sport': {'stadium': 'Stade de la Tuilière', 'latitude': 46.537778, 'longitude': 6.614444},
    'Servette FC': {'stadium': 'Stade de Genève', 'latitude': 46.1875, 'longitude': 6.128333},
    'FC Basel': {'stadium': 'St. Jakob-Park', 'latitude': 47.541389, 'longitude': 7.620833},
    'FC Lugano': {'stadium': 'Stadio di Cornaredo', 'latitude': 46.0225, 'longitude': 8.960278},
    'Grasshoppers': {'stadium': 'Letzigrund', 'latitude': 47.382778, 'longitude': 8.504167},
    'Yverdon Sport': {'stadium': 'Stade Municipal', 'latitude': 46.778056, 'longitude': 6.641111}
}

# Beispiel für die Benutzung
if home_team and match_date and match_time:
    coordinates = stadium_coordinates[home_team]
    latitude = coordinates['latitude']
    longitude = coordinates['longitude']

    st.write(f"Fetching weather data for {home_team} ({coordinates['stadium']})...")
    temperature_at_match, weather_condition = get_weather_data(latitude, longitude, match_date, match_time)

    if temperature_at_match is not None:
        st.success(f"Temperature at match time ({match_time}): {temperature_at_match}°C")
        st.success(f"Weather at match time ({match_time}): {weather_condition}")
else:
    st.error("Please fill in all fields.")


















# Vorhersage nur starten, wenn Button geklickt wird
if st.button("Predict Attendance"):
    if match_time is not None:
        # Berechnung direkter Features
        weekday = match_date.strftime('%A')
        month = match_date.month
        day = match_date.day
        holiday = 0  # Beispiel: Feiertage manuell prüfen oder mit einer API

        # Beispiel für Wetter-API-Aufruf (z. B. OpenWeatherMap)
        try:
            weather_api_key = "YOUR_API_KEY"
            weather_response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q=Zurich&appid={weather_api_key}")
            weather_data = weather_response.json()
            weather = weather_data['weather'][0]['main']
            temperature = weather_data['main']['temp'] - 273.15  # Kelvin zu Celsius
        except:
            weather = "Unknown"
            temperature = 20.0  # Standardwert

        # Beispiel-Eingabedaten
        input_data = np.array([[competition, matchday, match_time, home_team, away_team, 
                                weather, temperature, weekday, month, holiday, day]])
        
        # Wähle das richtige Modell
        if weather != "Unknown":
            predicted_attendance = model_with_weather.predict(input_data)
        else:
            predicted_attendance = model_without_weather.predict(input_data)

        st.success(f"Predicted Attendance Percentage: {predicted_attendance[0]:.2f}%")
    else:
        st.error("Please fill in all the fields correctly.")
