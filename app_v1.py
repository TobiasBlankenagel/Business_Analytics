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

# Eingabefelder
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
    "Match Time:", value=datetime.time(15, 30), help="Select the match time in HH:MM format"
)
match_hour = match_time.hour  # Holt nur die Stunde aus der Zeit

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

# Matchdaten abrufen
league_data = pd.read_csv('new_league_data.csv')
# Matchdaten abrufen
home_team_data = league_data[league_data['Unnamed: 0'] == home_team]
away_team_data = league_data[league_data['Unnamed: 0'] == away_team]

if home_team_data.empty:
    st.error(f"Home team '{home_team}' not found in the data.")
else:
    home_team_data = home_team_data.iloc[0]

if away_team_data.empty:
    st.error(f"Away team '{away_team}' not found in the data.")
else:
    away_team_data = away_team_data.iloc[0]

# Fortfahren, wenn beide Teams vorhanden sind
if not home_team_data.empty and not away_team_data.empty:
    # Daten extrahieren und Vorhersage durchführen
    ranking_home_team = home_team_data['Ranking']
    ranking_away_team = away_team_data['Ranking']
    goals_scored_home_team = home_team_data['Goals_Scored_in_Last_5_Games']
    goals_scored_away_team = away_team_data['Goals_Scored_in_Last_5_Games']
    goals_conceded_home_team = home_team_data['Goals_Conceded_in_Last_5_Games']
    goals_conceded_away_team = away_team_data['Goals_Conceded_in_Last_5_Games']
    wins_home_team = home_team_data['Number_of_Wins_in_Last_5_Games']
    wins_away_team = away_team_data['Number_of_Wins_in_Last_5_Games']
else:
    st.error("Prediction could not be performed due to missing data.")


# Features vorbereiten
input_features = {
    'Time': match_hour,
    'Ranking Home Team': home_team_data['Ranking'],
    'Ranking Away Team': away_team_data['Ranking'],
    'Temperature (°C)': temperature_at_match if temperature_at_match else 20,
    'Month': match_date.month,
    'Day': match_date.day,
    'Goals Scored in Last 5 Games': home_team_data['Goals_Scored_in_Last_5_Games'],
    'Goals Conceded in Last 5 Games': home_team_data['Goals_Conceded_in_Last_5_Games'],
    'Number of Wins in Last 5 Games': home_team_data['Number_of_Wins_in_Last_5_Games'],
}

# Dummy-coding für Features
input_data = pd.DataFrame([input_features])
input_data = pd.get_dummies(input_data)

# Vorhersage
if st.button("Predict Attendance"):
    # Berechnung der Features
    input_features = {
        'Time': match_hour,
        'Ranking Home Team': home_team_data['Ranking'],
        'Ranking Away Team': away_team_data['Ranking'],
        'Temperature (°C)': temperature_at_match if temperature_at_match else 20,
        'Month': match_date.month,
        'Day': match_date.day,
        'Goals Scored in Last 5 Games': home_team_data['Goals_Scored_in_Last_5_Games'],
        'Goals Conceded in Last 5 Games': home_team_data['Goals_Conceded_in_Last_5_Games'],
        'Number of Wins in Last 5 Games': home_team_data['Number_of_Wins_in_Last_5_Games'],
        f'Competition_{competition}': 1,  # Dummy-Encode Wettbewerb
        f'Matchday_{matchday}' if isinstance(matchday, int) else f'Matchday_{matchday}': 1,  # Matchday-Dummy
        f'Home Team_{home_team}': 1,  # Home Team Dummy
        f'Away Team_{away_team}': 1,  # Away Team Dummy
        f'Weather_{weather_condition}' if weather_condition else 'Weather_Unknown': 1,  # Wetter Dummy
    }

    # Konvertiere die Features in einen DataFrame
    input_data = pd.DataFrame([input_features])

    # Alle erwarteten Spalten sicherstellen
    expected_columns = model_with_weather.feature_names_in_
    for col in expected_columns:
        if col not in input_data.columns:
            input_data[col] = 0  # Fehlende Spalten initialisieren

    # Zusätzliche Spalten entfernen
    input_data = input_data[expected_columns]

    # Vorhersage durchführen
    if temperature_at_match is not None:
        prediction = model_with_weather.predict(input_data)[0]
    else:
        prediction = model_without_weather.predict(input_data)[0]

    st.success(f"Predicted Attendance Percentage: {prediction:.2f}%")

