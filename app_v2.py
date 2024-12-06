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
    page_title="🏟️ Stadium Attendance Prediction",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽🏟️ Stadium Attendance Prediction App")
st.markdown("🎉 Welcome to the ultimate tool for predicting stadium attendance!")

# Eingrenzung der Teams und Wettbewerbe
available_home_teams = ['FC Sion', 'FC St. Gallen', 'FC Winterthur', 'FC Zürich',
                        'BSC Young Boys', 'FC Luzern', 'Lausanne-Sport', 'Servette FC',
                        'FC Basel', 'FC Lugano', 'Grasshoppers', 'Yverdon Sport']
available_competitions = ['Super League', 'UEFA Conference League', 'Swiss Cup', 
                          'UEFA Europa League', 'UEFA Champions League']

# Dynamische Filterung der Auswärtsteams
def get_filtered_away_teams(home_team):
    return [team for team in available_home_teams if team != home_team] + ['Unknown']

# Eingabe: Home Team und Wettbewerb
col1, col2 = st.columns(2)
with col1:
    home_team = st.selectbox("🏠 Home Team:", available_home_teams)
    competition = st.selectbox("🏆 Competition:", available_competitions)

filtered_away_teams = get_filtered_away_teams(home_team)

# Eingabe: Away Team und Spieltag/Modus
with col2:
    away_team = st.selectbox("🛫 Away Team:", filtered_away_teams)
    if competition == "Super League":
        matchday = st.slider("🗓️ Matchday:", min_value=1, max_value=36, step=1)
    else:
        matchday = st.radio("📋 Match Type:", options=["Group Stage", "Knockout Stage"])

if away_team == home_team:
    st.warning("The home team and away team cannot be the same. Please select a different away team.")

# Datum und Uhrzeit
match_date = st.date_input("📅 Match Date:", min_value=datetime.date.today())
match_time = st.time_input("🕒 Match Time:", value=datetime.time(15, 30))
match_hour = match_time.hour

# Wetterdaten abrufen
st.markdown("### 🌤️ Weather Information")
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
        return temperature_at_match, weather_code_at_match
    except:
        return None, None

if home_team and match_date and match_time:
    coordinates = stadium_coordinates[home_team]
    temperature_at_match, weather_condition = get_weather_data(
        coordinates['latitude'], coordinates['longitude'], match_date, match_hour
    )
else:
    temperature_at_match, weather_condition = None, None

if temperature_at_match is not None:
    st.info(f"**Temperature**: {temperature_at_match}°C, **Condition**: {weather_condition}")
else:
    st.warning("Weather data unavailable. Default model will be used.")

# Daten vorbereiten
league_data = pd.read_csv('new_league_data.csv')
home_team_data = league_data[league_data['Unnamed: 0'] == home_team].iloc[0]

# Spalten dynamisch anpassen
required_columns = model_with_weather.feature_names_in_
input_features = {
    'Time': match_hour,
    'Ranking Home Team': home_team_data['Ranking'],
    'Temperature (°C)': temperature_at_match if temperature_at_match else 20,
}

input_data = pd.DataFrame([input_features])

for col in required_columns:
    if col not in input_data:
        input_data[col] = 0

if st.button("🎯 Predict Attendance"):
    model = model_with_weather if temperature_at_match else model_without_weather
    prediction_percentage = model.predict(input_data)[0]
    st.success(f"Predicted Attendance Percentage: {prediction_percentage*100:.2f}%")
