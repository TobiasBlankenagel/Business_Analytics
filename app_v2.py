import streamlit as st
import pandas as pd
import pickle
import datetime
import requests

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

# Dynamische Liste der Auswärtsteams erstellen (ohne Heimteam)
def get_filtered_away_teams(home_team, available_teams):
    return [team for team in available_teams if team != home_team] + ['Unknown']

# Eingabe: Home Team und Wettbewerb
col1, col2 = st.columns(2)
with col1:
    home_team = st.selectbox("🏠 Home Team:", available_home_teams)
    competition = st.selectbox("🏆 Competition:", available_competitions)

# Dynamische Filterung der Auswärtsteams basierend auf der Auswahl des Heimteams
filtered_away_teams = get_filtered_away_teams(home_team, available_home_teams)

# Eingabe: Away Team und Matchday/Modus
with col2:
    if competition == "Super League":
        away_team = st.selectbox("🛫 Away Team:", filtered_away_teams)
        matchday = st.slider("🗓️ Matchday:", min_value=1, max_value=36, step=1)
    else:
        away_team = st.selectbox("🛫 Away Team:", filtered_away_teams)
        matchday = st.radio("📋 Match Type:", options=["Group Stage", "Knockout Stage"])

# Optional: Hinweis anzeigen, wenn keine gültige Auswahl möglich ist
if away_team == home_team:
    st.warning("The home team and away team cannot be the same. Please select a different away team.")

# Datum und Uhrzeit
match_date = st.date_input("📅 Match Date:", min_value=datetime.date.today())
match_time = st.time_input("🕒 Match Time:", value=datetime.time(15, 30))
match_hour = match_time.hour

# Wetterdaten abrufen
st.markdown("### 🌤️ Weather Information")

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

        # Sicherstellen, dass die Stunde im Datensatz vorhanden ist
        if match_hour < len(hourly_data['temperature_2m']):
            temperature_at_match = hourly_data['temperature_2m'][match_hour]
            weather_code_at_match = hourly_data['weathercode'][match_hour]

            # Wetterbedingungen basierend auf WeatherCode bestimmen
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
        else:
            return None, None
    except Exception:
        return None, None

# Koordinaten des Heimstadions
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

# Wetterdaten abrufen, falls verfügbar
if home_team and match_date and match_time:
    coordinates = stadium_coordinates[home_team]
    latitude = coordinates['latitude']
    longitude = coordinates['longitude']
    temperature_at_match, weather_condition = get_weather_data(latitude, longitude, match_date, match_hour)
else:
    temperature_at_match, weather_condition = None, None

# Wetteranzeige in der App
if temperature_at_match is not None:
    st.info(f"**Temperature**: {temperature_at_match}°C, **Condition**: {weather_condition}")
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
    
    # Maximal mögliche Zuschauerzahl berechnen
    max_capacity = stadium_capacity[home_team]
    predicted_attendance = round(prediction_percentage * max_capacity)
    
    # Ergebnisse anzeigen
    st.success(f"🎉 Predicted Attendance Percentage: **{prediction_percentage:.2f}%**")
    st.info(f"🏟️ Predicted Attendance: **{predicted_attendance}** out of {max_capacity} seats.")
    st.warning(weather_status)

