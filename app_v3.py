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
    page_icon="🏆",
    layout="wide"
)

# Hintergrundbild und Farben
st.markdown("""
    <style>
    body {
        background-color: #f4f5f7;
        font-family: 'Helvetica', sans-serif;
    }
    .stButton>button {
        background-color: #003366;
        color: white;
        font-size: 18px;
        padding: 15px 40px;
        border-radius: 10px;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #005b8c;
    }
    h1 {
        color: #003366;
        font-size: 50px;
    }
    h2 {
        color: #005b8c;
    }
    .stSelectbox>label {
        font-size: 16px;
        font-weight: bold;
    }
    .stSlider>label, .stRadio>label {
        font-size: 16px;
        font-weight: bold;
    }
    .stMarkdown {
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# Titel der App
st.title("🏟️ Stadium Attendance Prediction App")
st.markdown("🎉⚽ This app predicts stadium attendance based on match data, teams, and weather conditions!")

# Eingrenzung der Teams und Wettbewerbe
available_home_teams = ['FC Sion', 'FC St. Gallen', 'FC Winterthur', 'FC Zürich',
                        'BSC Young Boys', 'FC Luzern', 'Lausanne-Sport', 'Servette FC',
                        'FC Basel', 'FC Lugano', 'Grasshoppers', 'Yverdon Sport']
available_away_teams = available_home_teams
available_competitions = ['Super League', 'UEFA Conference League', 'Swiss Cup', 
                          'UEFA Europa League', 'UEFA Champions League']

# Eingabefelder
home_team = st.selectbox("🏠 Home Team:", available_home_teams)
competition = st.selectbox("🏆 Competition:", available_competitions)

if competition == "Super League":
    away_team = st.selectbox("🛫 Away Team:", available_home_teams)
elif competition == "Swiss Cup":
    away_team = st.selectbox("🛫 Away Team:", available_away_teams)
else:
    away_team = "Unknown"

if competition == "Super League":
    matchday = st.slider("🗓️ Matchday:", min_value=1, max_value=36, step=1)
else:
    matchday = st.radio("📋 Match Type:", options=["Group Stage", "Knockout"])

match_date = st.date_input("📅 Match Date:", min_value=datetime.date.today())
match_time = st.time_input(
    "🕒 Match Time:", value=datetime.time(15, 30), help="Select the match time in HH:MM format"
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

# Erstelle DataFrame aus input_features
input_features = {
    'Competition': competition,
    'Matchday': matchday,
    'Time': match_hour,
    'Home Team': home_team,
    'Ranking Home Team': 10,  # Beispielwert
    'Away Team': away_team,
    'Ranking Away Team': 5,  # Beispielwert
    'Weather': weather_condition,
    'Temperature (°C)': temperature_at_match,
    'Weekday': weekday,
    'Month': match_date.month,
    'Day': match_date.day,
    'Goals Scored in Last 5 Games': 12,  # Beispielwert
    'Goals Conceded in Last 5 Games': 5,  # Beispielwert
    'Number of Wins in Last 5 Games': 3,  # Beispielwert
}

# Umwandlung in DataFrame
input_df = pd.DataFrame([input_features])

# Dummy-Encode der kategorischen Spalten
categorical_columns = ["Competition", "Matchday", "Home Team", "Away Team", "Weather", "Weekday"]
input_df = pd.get_dummies(input_df, columns=categorical_columns)

# Fehlende Spalten ergänzen
for col in expected_columns:
    if col not in input_df.columns:
        input_df[col] = 0

# Vorhersage
if st.button("Predict Attendance"):
    prediction = model_with_weather.predict(input_df)[0]
    st.success(f"Predicted Attendance Percentage: {prediction:.2f}%")
