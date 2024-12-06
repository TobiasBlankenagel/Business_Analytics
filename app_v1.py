import streamlit as st
import datetime
import pickle
import numpy as np
import pandas as pd
import requests

# Modelle laden
def load_model(model_path):
    with open(model_path, 'rb') as file:
        return pickle.load(file)

model_with_weather = load_model("finalized_model_with_weather.sav")
model_without_weather = load_model("finalized_model_without_weather.sav")

st.set_page_config(
    page_title="Stadium Capacity Prediction",
    page_icon="🏟️",
    layout="wide"
)

st.title("🏟️ Stadium Capacity Prediction App")
st.markdown("🎉⚽ This app predicts stadium capacity utilization.")

# Eingabe für Teams und andere Parameter
available_home_teams = [
    'FC Sion', 'FC St. Gallen', 'FC Winterthur', 'FC Zürich',
    'BSC Young Boys', 'FC Luzern', 'Lausanne-Sport', 'Servette FC',
    'FC Basel', 'FC Lugano', 'Grasshoppers', 'Yverdon Sport'
]
available_away_teams = available_home_teams + ['Unknown']
available_competitions = [
    'Super League', 'UEFA Conference League', 'Swiss Cup',
    'UEFA Europa League', 'UEFA Champions League'
]

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
match_time = st.time_input(
    "Match Time:",
    value=datetime.time(15, 30),  # Standardwert auf 15:30 setzen
    help="Select the match time in HH:MM format"
)
match_hour = match_time.hour

# Stadionkoordinaten
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

        return temperature_at_match, weather_condition
    except:
        return None, None

# Wetterdaten für das Heimteam abrufen
if home_team and match_date and match_time:
    coordinates = stadium_coordinates[home_team]
    temperature_at_match, weather_condition = get_weather_data(
        coordinates['latitude'], coordinates['longitude'], match_date, match_hour
    )
else:
    temperature_at_match, weather_condition = None, None

# Zusätzliche Daten aus CSV
league_data = pd.read_csv("new_league_data.csv")
home_team_data = league_data[league_data['Unnamed: 0'] == home_team].iloc[0]
away_team_data = league_data[league_data['Unnamed: 0'] == away_team].iloc[0]

# Eingabedaten vorbereiten
ranking_home_team = home_team_data['Ranking']
ranking_away_team = away_team_data['Ranking']
goals_scored_home_team = home_team_data['Goals_Scored_in_Last_5_Games']
goals_conceded_home_team = home_team_data['Goals_Conceded_in_Last_5_Games']
wins_home_team = home_team_data['Number_of_Wins_in_Last_5_Games']

goals_scored_away_team = away_team_data['Goals_Scored_in_Last_5_Games']
goals_conceded_away_team = away_team_data['Goals_Conceded_in_Last_5_Games']
wins_away_team = away_team_data['Number_of_Wins_in_Last_5_Games']

weekday = match_date.strftime('%A')
month = match_date.month
day = match_date.day

# Vorhersage
if st.button("Predict Attendance"):
    input_data = {
        "Time": match_hour,
        "Ranking Home Team": ranking_home_team,
        "Ranking Away Team": ranking_away_team,
        "Temperature (°C)": temperature_at_match or 20,  # Standardtemperatur
        "Month": month,
        "Day": day,
        "Goals Scored in Last 5 Games": goals_scored_home_team,
        "Goals Conceded in Last 5 Games": goals_conceded_home_team,
        "Number of Wins in Last 5 Games": wins_home_team
    }
    # Dummy-Codierung einfügen
    # Vorhersage starten
    if temperature_at_match is not None:
        prediction = model_with_weather.predict(np.array([list(input_data.values())]))
    else:
        prediction = model_without_weather.predict(np.array([list(input_data.values())]))
    
    st.success(f"Predicted Attendance Percentage: {prediction[0]:.2f}%")
