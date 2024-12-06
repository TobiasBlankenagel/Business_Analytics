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

# CSS Styling
st.markdown("""
    <style>
        .main-container {
            background-color: #f7f7f7;
            padding: 20px;
            border-radius: 10px;
        }
        .header {
            text-align: center;
            color: #333;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .dataframe-table {
            border: 2px solid #ddd;
            border-radius: 10px;
            margin-bottom: 20px;
            font-family: Arial, sans-serif;
        }
        th {
            background-color: #f4f4f4;
            font-weight: bold;
            color: #333;
            padding: 10px;
        }
        td {
            padding: 10px;
            text-align: center;
        }
        .highlight-win {
            background-color: green !important;
            color: white !important;
        }
        .highlight-lose {
            background-color: red !important;
            color: white !important;
        }
        .highlight-tie {
            background-color: grey !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="header">🏟️ Stadium Attendance Prediction App</div>', unsafe_allow_html=True)

# Eingrenzung der Teams und Wettbewerbe
available_home_teams = ['FC Sion', 'FC St. Gallen', 'FC Winterthur', 'FC Zürich',
                        'BSC Young Boys', 'FC Luzern', 'Lausanne-Sport', 'Servette FC',
                        'FC Basel', 'FC Lugano', 'Grasshoppers', 'Yverdon Sport']
available_away_teams = available_home_teams + ['Unknown']
available_competitions = ['Super League', 'UEFA Conference League', 'Swiss Cup', 
                          'UEFA Europa League', 'UEFA Champions League']

# Eingabefelder
with st.container():
    home_team = st.selectbox("Home Team:", available_home_teams)
    competition = st.selectbox("Competition:", available_competitions)

    if competition == "Super League":
        away_team = st.selectbox("Away Team:", available_home_teams)
        matchday = st.slider("Matchday:", min_value=1, max_value=36, step=1)
    elif competition == "Swiss Cup":
        away_team = st.selectbox("Away Team:", available_away_teams)
        matchday = st.radio("Matchday Type:", options=["Group", "Knockout"])
    else:
        away_team = "Unknown"
        matchday = st.radio("Matchday Type:", options=["Group", "Knockout"])

    match_date = st.date_input("Match Date:", min_value=datetime.date.today())
    match_time = st.time_input("Match Time:", value=datetime.time(15, 30))
    match_hour = match_time.hour

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

        weather_condition = {
            0: "Clear",
            1: "Partly cloudy",
            2: "Rainy",
            3: "Snowy",
            51: "Drizzle"
        }.get(weather_code_at_match, "Unknown")

        return temperature_at_match, weather_condition
    except Exception:
        return None, None

if home_team:
    coordinates = stadium_coordinates[home_team]
    latitude = coordinates['latitude']
    longitude = coordinates['longitude']
    temperature_at_match, weather_condition = get_weather_data(latitude, longitude, match_date, match_hour)

# Button für Vorhersage
if st.button("Predict Attendance"):
    league_data = pd.read_csv('new_league_data.csv')

    home_team_data = league_data[league_data['Unnamed: 0'] == home_team].iloc[0]
    if away_team != "Unknown":
        away_team_data = league_data[league_data['Unnamed: 0'] == away_team].iloc[0]
    else:
        away_team_data = {
            'Ranking': 999,
            'Goals_Scored_in_Last_5_Games': 0,
            'Goals_Conceded_in_Last_5_Games': 0,
            'Number_of_Wins_in_Last_5_Games': 0
        }

    # Modellvorhersage
    prediction = model_with_weather.predict([[match_hour]])[0]

    st.success(f"Predicted Attendance: {prediction:.2f} %")

    # Zeige Tabellen
    st.dataframe(league_data)
