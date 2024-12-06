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
weekday = match_date.strftime("%A")

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


# Matchdaten abrufen
league_data = pd.read_csv('new_league_data.csv')

# Matchdaten abrufen
home_team_data = league_data[league_data['Unnamed: 0'] == home_team]

if home_team_data.empty:
    st.error(f"Home team '{home_team}' not found in the data.")
else:
    home_team_data = home_team_data.iloc[0]

# Wenn Away Team "Unknown" ist, Standardwerte verwenden
if away_team == "Unknown":
    ranking_away_team = 999  # Beispiel: 999 als Platzhalter für unbekanntes Ranking
    goals_scored_away_team = 0
    goals_conceded_away_team = 0
    wins_away_team = 0
else:
    away_team_data = league_data[league_data['Unnamed: 0'] == away_team]
    if away_team_data.empty:
        st.error(f"Away team '{away_team}' not found in the data.")
    else:
        away_team_data = away_team_data.iloc[0]
        ranking_away_team = away_team_data['Ranking']
        goals_scored_away_team = away_team_data['Goals_Scored_in_Last_5_Games']
        goals_conceded_away_team = away_team_data['Goals_Conceded_in_Last_5_Games']
        wins_away_team = away_team_data['Number_of_Wins_in_Last_5_Games']


# Fortfahren, wenn Home Team gefunden wurde
if not home_team_data.empty:
    ranking_home_team = home_team_data['Ranking']
    goals_scored_home_team = home_team_data['Goals_Scored_in_Last_5_Games']
    goals_conceded_home_team = home_team_data['Goals_Conceded_in_Last_5_Games']
    wins_home_team = home_team_data['Number_of_Wins_in_Last_5_Games']

    # Beispiel-Features erstellen
    input_features = {
        'Competition': competition,
        'Matchday': matchday,
        'Time': match_hour,
        'Home Team': home_team,
        'Ranking Home Team': ranking_home_team,
        'Away Team': away_team,
        'Ranking Away Team': ranking_away_team,
        'Weather': weather_condition,
        'Temperature (°C)': temperature_at_match,
        'Weekday': weekday,
        'Month': match_date.month,
        'Day': match_date.day,
        'Goals Scored in Last 5 Games': goals_scored_home_team,
        'Goals Conceded in Last 5 Games': goals_conceded_home_team,
        'Number of Wins in Last 5 Games': wins_home_team,
    }

    # Dummy-coding vorbereiten
    input_data = pd.DataFrame([input_features])
    expected_columns = model_with_weather.feature_names_in_

    # Fehlende Spalten hinzufügen
    for col in expected_columns:
        if col not in input_data.columns:
            input_data[col] = 0

    # Zusätzliche Spalten entfernen
    input_data = input_data[expected_columns]

    st.write(wins_home_team)


    # Vorhersage
    if st.button("Predict Attendance"):
        if temperature_at_match is not None:
            prediction = model_with_weather.predict(input_data)[0]
        else:
            prediction = model_without_weather.predict(input_data)[0]
        
        st.success(f"Predicted Attendance Percentage: {prediction:.2f}%")



















# Tabelle mit Rankings und den letzten 5 Spielen
def color_results(val):
    if val == "Win":
        return "background-color: green; color: white;"
    elif val == "Lose":
        return "background-color: red; color: white;"
    elif val == "Tie":
        return "background-color: grey; color: white;"
    return ""  # Keine Farbe für leere Zellen


# Teamstatistiken für Heimteam anzeigen
if not home_team_data.empty:
    st.write("### Home Team Statistics")
    team_stats = {
        "Ranking": [ranking_home_team],
        "Goals Scored in Last 5 Games": [goals_scored_home_team],
        "Goals Conceded in Last 5 Games": [goals_conceded_home_team],
        "Number of Wins in Last 5 Games": [wins_home_team],
        "Last 1 Game Result": [home_team_data['Last_1_Game_Result']],
        "Last 2 Game Result": [home_team_data['Last_2_Game_Result']],
        "Last 3 Game Result": [home_team_data['Last_3_Game_Result']],
        "Last 4 Game Result": [home_team_data['Last_4_Game_Result']],
        "Last 5 Game Result": [home_team_data['Last_5_Game_Result']],
    }
    team_stats_df = pd.DataFrame(team_stats)
    st.dataframe(
        team_stats_df.style.applymap(color_results, subset=[
            "Last 1 Game Result", "Last 2 Game Result", 
            "Last 3 Game Result", "Last 4 Game Result", 
            "Last 5 Game Result"
        ])
    )

# Teamstatistiken für Auswärtsteam anzeigen, wenn nicht "Unknown"
if away_team != "Unknown" and not away_team_data.empty:
    st.write("### Away Team Statistics")
    away_stats = {
        "Ranking": [ranking_away_team],
        "Goals Scored in Last 5 Games": [goals_scored_away_team],
        "Goals Conceded in Last 5 Games": [goals_conceded_away_team],
        "Number of Wins in Last 5 Games": [wins_away_team],
        "Last 1 Game Result": [away_team_data['Last_1_Game_Result']],
        "Last 2 Game Result": [away_team_data['Last_2_Game_Result']],
        "Last 3 Game Result": [away_team_data['Last_3_Game_Result']],
        "Last 4 Game Result": [away_team_data['Last_4_Game_Result']],
        "Last 5 Game Result": [away_team_data['Last_5_Game_Result']],
    }
    away_stats_df = pd.DataFrame(away_stats)
    st.dataframe(
        away_stats_df.style.applymap(color_results, subset=[
            "Last 1 Game Result", "Last 2 Game Result", 
            "Last 3 Game Result", "Last 4 Game Result", 
            "Last 5 Game Result"
        ])
    )
