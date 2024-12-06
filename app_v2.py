import streamlit as st
import pandas as pd
import numpy as np
import pickle
import requests
import datetime

# Modelle laden
def load_model(model_path):
    with open(model_path, 'rb') as file:
        return pickle.load(file)

model_with_weather = load_model("./finalized_model_with_weather.sav")
model_without_weather = load_model("./finalized_model_without_weather.sav")

# Streamlit-Konfiguration
st.set_page_config(
    page_title="Stadium Attendance Prediction",
    page_icon="🏟️",
    layout="wide"
)

st.title("🏟️ Stadium Attendance Prediction App")
st.markdown("🎉⚽ This app predicts stadium attendance.")

# Eingrenzung der Teams und Wettbewerbe
available_home_teams = ['FC Sion', 'FC St. Gallen', 'FC Winterthur', 'FC Zürich',
                        'BSC Young Boys', 'FC Luzern', 'Lausanne-Sport', 'Servette FC',
                        'FC Basel', 'FC Lugano', 'Grasshoppers', 'Yverdon Sport']
available_competitions = ['Super League', 'UEFA Conference League', 'Swiss Cup', 
                          'UEFA Europa League', 'UEFA Champions League']

# Eingabefelder
col1, col2 = st.columns(2)
with col1:
    home_team = st.selectbox("🏠 Home Team:", available_home_teams)
    competition = st.selectbox("🏆 Competition:", available_competitions)
with col2:
    available_away_teams = [team for team in available_home_teams if team != home_team] + ['Unknown']
    away_team = st.selectbox("🛫 Away Team:", available_away_teams)

if competition == "Super League":
    matchday = st.slider("🗓️ Matchday:", min_value=1, max_value=36, step=1)
else:
    matchday = st.radio("📋 Match Type:", options=["Group Stage", "Knockout Stage"])

match_date = st.date_input("📅 Match Date:", min_value=datetime.date.today())
match_time = st.time_input("⏰ Match Time:", value=datetime.time(15, 30))
match_hour = match_time.hour

# Wetterdaten abrufen
def get_weather_data(latitude, longitude, match_date, match_hour):
    api_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}&start_date={match_date}&end_date={match_date}"
        f"&hourly=temperature_2m,weathercode"
        f"&timezone=auto"
    )

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        weather_data = response.json()
        hourly_data = weather_data['hourly']
        temperature_at_match = hourly_data['temperature_2m'][match_hour]
        weather_code_at_match = hourly_data['weathercode'][match_hour]

        if weather_code_at_match in [0]:
            weather_condition = "Clear"
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

        return temperature_at_match, weather_condition
    except:
        return None, None

# Koordinaten der Stadien
stadium_coordinates = {
    'FC Sion': {'latitude': 46.233333, 'longitude': 7.376389},
    'FC St. Gallen': {'latitude': 47.408333, 'longitude': 9.310278},
    'FC Winterthur': {'latitude': 47.505278, 'longitude': 8.724167},
    'FC Zürich': {'latitude': 47.382778, 'longitude': 8.504167},
    'BSC Young Boys': {'latitude': 46.963056, 'longitude': 7.464722},
    'FC Luzern': {'latitude': 47.035833, 'longitude': 8.310833},
    'Lausanne-Sport': {'latitude': 46.537778, 'longitude': 6.614444},
    'Servette FC': {'latitude': 46.1875, 'longitude': 6.128333},
    'FC Basel': {'latitude': 47.541389, 'longitude': 7.620833},
    'FC Lugano': {'latitude': 46.0225, 'longitude': 8.960278},
    'Grasshoppers': {'latitude': 47.382778, 'longitude': 8.504167},
    'Yverdon Sport': {'latitude': 46.778056, 'longitude': 6.641111}
}

if home_team and match_date and match_time:
    coordinates = stadium_coordinates[home_team]
    latitude = coordinates['latitude']
    longitude = coordinates['longitude']
    temperature_at_match, weather_condition = get_weather_data(latitude, longitude, match_date, match_hour)
else:
    temperature_at_match, weather_condition = None, None

# Feature-Vorbereitung
weekday = match_date.strftime("%A")  # Wochentag
input_features = {
    'Time': match_hour,
    'Ranking Home Team': 1,  # Beispielwert
    'Ranking Away Team': 2,  # Beispielwert
    'Temperature (°C)': temperature_at_match if temperature_at_match else 20,
    'Month': match_date.month,
    'Day': match_date.day,
    'Competition': competition,
    'Home Team': home_team,
    'Away Team': away_team,
    'Weather': weather_condition if weather_condition else "Unknown",
    'Matchday': matchday,
    'Weekday': weekday,
}

# One-Hot-Encoding
categorical_columns = ['Competition', 'Home Team', 'Away Team', 'Weather', 'Matchday', 'Weekday']
encoded_features = pd.get_dummies(pd.DataFrame([input_features]), columns=categorical_columns)

# Fehlende Spalten auffüllen
expected_columns = model_with_weather.feature_names_in_
for col in expected_columns:
    if col not in encoded_features:
        encoded_features[col] = 0
encoded_features = encoded_features[expected_columns]

# Vorhersage
if st.button("🎯 Predict Attendance"):
    if temperature_at_match is not None:
        prediction_percentage = model_with_weather.predict(encoded_features)[0]
        weather_status = "Weather data used for prediction."
    else:
        prediction_percentage = model_without_weather.predict(encoded_features)[0]
        weather_status = "Weather data unavailable. Prediction made without weather information."

    st.success(f"Predicted Attendance Percentage: {prediction_percentage:.2f}%")
    st.warning(weather_status)
