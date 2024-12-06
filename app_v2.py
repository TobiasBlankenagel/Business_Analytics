import streamlit as st
import pandas as pd
import pickle
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

# Titelbereich
st.title("⚽🏟️ Stadium Attendance Prediction App")
st.markdown("🎉 Welcome to the ultimate tool for predicting stadium attendance! Let’s get started.")

# Eingrenzung der Teams und Wettbewerbe
available_home_teams = ['FC Sion', 'FC St. Gallen', 'FC Winterthur', 'FC Zürich',
                        'BSC Young Boys', 'FC Luzern', 'Lausanne-Sport', 'Servette FC',
                        'FC Basel', 'FC Lugano', 'Grasshoppers', 'Yverdon Sport']
available_away_teams = available_home_teams + ['Unknown']
available_competitions = ['Super League', 'UEFA Conference League', 'Swiss Cup', 
                          'UEFA Europa League', 'UEFA Champions League']

# Eingabe: Home Team und Wettbewerb
col1, col2 = st.columns(2)
with col1:
    home_team = st.selectbox("🏠 Home Team:", available_home_teams)
    competition = st.selectbox("🏆 Competition:", available_competitions)

# Eingabe: Away Team und Matchday/Modus
with col2:
    if competition == "Super League":
        away_team = st.selectbox("🛫 Away Team:", available_home_teams)
        matchday = st.slider("🗓️ Matchday:", min_value=1, max_value=36, step=1)
    else:
        away_team = st.selectbox("🛫 Away Team:", available_away_teams)
        matchday = st.radio("📋 Match Type:", options=["Group Stage", "Knockout Stage"])

# Datum und Uhrzeit
match_date = st.date_input("📅 Match Date:", min_value=datetime.date.today())
match_time = st.time_input("🕒 Match Time:", value=datetime.time(15, 30))
match_hour = match_time.hour

# Wetterdaten abrufen (Dummy-Wetterdaten hier als Platzhalter)
st.markdown("### 🌤️ Weather Information")
temperature_at_match = 15  # Beispielwert
weather_condition = "Partly Cloudy"
st.info(f"**Temperature**: {temperature_at_match}°C, **Condition**: {weather_condition}")

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
    ranking_away_team = 999  # Platzhalter für unbekanntes Team
    goals_scored_away_team = 0
    goals_conceded_away_team = 0
    wins_away_team = 0

# Features für das Modell vorbereiten
input_features = {
    'Time': match_hour,
    'Ranking Home Team': ranking_home_team,
    'Ranking Away Team': ranking_away_team,
    'Temperature (°C)': temperature_at_match,
    'Month': match_date.month,
    'Day': match_date.day,
    'Goals Scored in Last 5 Games': goals_scored_home_team,
    'Goals Conceded in Last 5 Games': goals_conceded_home_team,
    'Number of Wins in Last 5 Games': wins_home_team,
}

# Input-Daten für das Modell
input_data = pd.DataFrame([input_features])
expected_columns = model_with_weather.feature_names_in_

# Fehlende Spalten auffüllen
for col in expected_columns:
    if col not in input_data.columns:
        input_data[col] = 0
input_data = input_data[expected_columns]

# Vorhersage
if st.button("🎯 Predict Attendance"):
    if temperature_at_match:
        prediction = model_with_weather.predict(input_data)[0]
    else:
        prediction = model_without_weather.predict(input_data)[0]
    st.success(f"🎉 Predicted Attendance Percentage: **{prediction:.2f}%**")
    st.balloons()

