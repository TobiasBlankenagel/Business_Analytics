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

# --- CSS-Styles für die App ---
st.markdown("""
    <style>
    /* Allgemeine Styles */
    .main {background-color: #f7f9fc;}
    .block-container {padding: 2rem;}
    h1 {color: #1f77b4;}
    h2, h3, h4 {color: #2c3e50;}
    
    /* Tabelle Stylen */
    table {
        border-collapse: collapse;
        width: 100%;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
    }
    tr:nth-child(even){background-color: #f2f2f2;}
    tr:hover {background-color: #ddd;}
    th {
        padding-top: 12px;
        padding-bottom: 12px;
        text-align: left;
        background-color: #1f77b4;
        color: white;
    }
    .highlight-home {background-color: #ffa07a !important;}
    .highlight-away {background-color: #87cefa !important;}
    .result-win {background-color: #4caf50; color: white; padding: 5px; text-align: center; border-radius: 5px;}
    .result-lose {background-color: #e74c3c; color: white; padding: 5px; text-align: center; border-radius: 5px;}
    .result-tie {background-color: #bdc3c7; color: white; padding: 5px; text-align: center; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

# --- Titelbereich ---
st.title("🏟️ Stadium Attendance Prediction App")
st.markdown("🎉 Welcome to the ultimate tool for predicting stadium attendance!")

# --- Eingabeformular ---
available_home_teams = ['FC Sion', 'FC St. Gallen', 'FC Winterthur', 'FC Zürich',
                        'BSC Young Boys', 'FC Luzern', 'Lausanne-Sport', 'Servette FC',
                        'FC Basel', 'FC Lugano', 'Grasshoppers', 'Yverdon Sport']
available_competitions = ['Super League', 'UEFA Conference League', 'Swiss Cup', 
                          'UEFA Europa League', 'UEFA Champions League']

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

col1, col2 = st.columns(2)
with col1:
    home_team = st.selectbox("🏠 Home Team:", available_home_teams)
    competition = st.selectbox("🏆 Competition:", available_competitions)
with col2:
    available_away_teams = [team for team in available_home_teams if team != home_team] + ['Unknown']
    away_team = st.selectbox("🛫 Away Team:", available_away_teams)

match_date = st.date_input("📅 Match Date:", min_value=datetime.date.today())
match_time = st.time_input("🕒 Match Time:", value=datetime.time(15, 30))
match_hour = match_time.hour

# --- Wetterdaten ---
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
    except Exception:
        return None, None


coordinates = {
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
weather_data = coordinates.get(home_team)
if weather_data:
    lat, lon = weather_data['latitude'], weather_data['longitude']
    temperature, condition = get_weather_data(lat, lon, match_date, match_hour)
else:
    temperature, condition = None, None

if temperature:
    st.info(f"🌡️ Temperature: {temperature}°C, Condition: {condition}")
else:
    st.warning("Weather data unavailable, using default model.")

# --- Liga-Daten ---
league_data = pd.read_csv('new_league_data.csv')

def process_team_data(team):
    team_data = league_data[league_data['Unnamed: 0'] == team].iloc[0]
    return {
        "Ranking": team_data['Ranking'],
        "Last 5 Games": [
            team_data[f'Last_{i}_Game_Result'] for i in range(1, 6)
        ]
    }

home_stats = process_team_data(home_team)
if away_team != "Unknown":
    away_stats = process_team_data(away_team)
else:
    away_stats = None

# --- Tabellenanzeige ---
def generate_table(home, away=None):
    cols = ["Team", "Ranking", "Last 5 Games"]
    data = [[home_team, home["Ranking"], "".join([f"<span class='result-{g.lower()}'>{g[0]}</span>" for g in home["Last 5 Games"]])]]
    if away:
        data.append([away_team, away["Ranking"], "".join([f"<span class='result-{g.lower()}'>{g[0]}</span>" for g in away["Last 5 Games"]])])
    return pd.DataFrame(data, columns=cols).to_html(escape=False, index=False)

st.write(generate_table(home_stats, away_stats), unsafe_allow_html=True)
