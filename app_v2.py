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
available_away_teams = available_home_teams + ['Unknown']
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

match_date = st.date_input("Match Date:", min_value=datetime.date.today())
match_time = st.time_input(
    "Match Time:", value=datetime.time(15, 30), help="Select the match time in HH:MM format"
)
match_hour = match_time.hour

# Wetterdaten abrufen
def get_weather_data(lat, lon, date, hour):
    api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={date}&end_date={date}&hourly=temperature_2m,weathercode&timezone=auto"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        weather_data = response.json()['hourly']
        temp = weather_data['temperature_2m'][hour]
        code = weather_data['weathercode'][hour]

        # Wetterbedingungen korrekt mappen
        weather_conditions = {
            0: "Clear or mostly clear",
            1: "Partly cloudy",
            2: "Partly cloudy",
            3: "Partly cloudy",
            61: "Rainy",
            63: "Rainy",
            65: "Rainy",
            80: "Rainy",
            81: "Rainy",
            82: "Rainy",
            51: "Drizzle",
            53: "Drizzle",
            55: "Drizzle",
            71: "Snowy",
            73: "Snowy",
            75: "Snowy",
            85: "Snowy",
            86: "Snowy",
            77: "Snowy"
        }
        condition = weather_conditions.get(code, "Unknown")
        return temp, condition
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

# Anzeige der Wetterdaten
if temperature_at_match is not None:
    st.info(f"**Temperature:** {temperature_at_match}°C, **Condition:** {weather_condition}")
else:
    st.warning("Weather data unavailable. Default model will be used.")

# Teamdaten laden
league_data = pd.read_csv('new_league_data.csv')

# Home Team Daten
home_team_data = league_data[league_data['Unnamed: 0'] == home_team].iloc[0]
ranking_home_team = home_team_data['Ranking']
goals_scored_home_team = home_team_data['Goals_Scored_in_Last_5_Games']
goals_conceded_home_team = home_team_data['Goals_Conceded_in_Last_5_Games']
wins_home_team = home_team_data['Number_of_Wins_in_Last_5_Games']

# Away Team Daten
if away_team != "Unknown":
    away_team_data = league_data[league_data['Unnamed: 0'] == away_team].iloc[0]
    ranking_away_team = away_team_data['Ranking']
    goals_scored_away_team = away_team_data['Goals_Scored_in_Last_5_Games']
    goals_conceded_away_team = away_team_data['Goals_Conceded_in_Last_5_Games']
    wins_away_team = away_team_data['Number_of_Wins_in_Last_5_Games']
else:
    ranking_away_team = 999
    goals_scored_away_team = 0
    goals_conceded_away_team = 0
    wins_away_team = 0

# Stadionkapazitäten
stadium_capacity = {
    'FC Sion': 16232,
    'FC St. Gallen': 20029,
    'FC Winterthur': 8550,
    'FC Zürich': 26104,
    'BSC Young Boys': 31783,
    'FC Luzern': 16800,
    'Lausanne-Sport': 12544,
    'Servette FC': 30084,
    'FC Basel': 38512,
    'FC Lugano': 6330,
    'Grasshoppers': 26104,
    'Yverdon Sport': 6600
}

# Features vorbereiten
input_features = {
    'Time': match_hour,
    'Ranking Home Team': ranking_home_team,
    'Ranking Away Team': ranking_away_team,
    'Temperature (°C)': temperature_at_match if temperature_at_match is not None else 20,
    'Month': match_date.month,
    'Day': match_date.day,
    'Goals Scored in Last 5 Games': goals_scored_home_team,
    'Goals Conceded in Last 5 Games': goals_conceded_home_team,
    'Number of Wins in Last 5 Games': wins_home_team,
}

# Umwandlung in DataFrame
input_data = pd.DataFrame([input_features])

# Vorhersage
if st.button("🎯 Predict Attendance"):
    if temperature_at_match is not None:
        prediction_percentage = model_with_weather.predict(input_data)[0]
        weather_status = "Weather data used for prediction."
    else:
        prediction_percentage = model_without_weather.predict(input_data)[0]
        weather_status = "Weather data unavailable. Prediction made without weather information."
    
    max_capacity = stadium_capacity[home_team]
    predicted_attendance = round(prediction_percentage * max_capacity)
    
    st.success(f"🎉 Predicted Attendance Percentage: **{prediction_percentage:.2f}%**")
    st.info(f"🏟️ Predicted Attendance: **{predicted_attendance}** out of {max_capacity} seats.")
    st.warning(weather_status)
