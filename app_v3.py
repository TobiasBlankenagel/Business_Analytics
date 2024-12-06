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

st.markdown("""
    <style>
    /* Hintergrundfarbe der gesamten Seite */
    body {
        background-color: #f4f7fc;
        font-family: 'Arial', sans-serif;
    }

    /* Titel und Hauptüberschrift */
    h1 {
        color: #003366;
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        margin-top: 50px;
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    }

    /* Beschreibungstext */
    .markdown-text-container {
        font-size: 18px;
        color: #333333;
        text-align: center;
        padding: 0 20px;
        margin-top: 20px;
    }

    /* Auswahlboxen und Buttons */
    .stSelectbox, .stSlider, .stRadio, .stButton, .stDateInput, .stTimeInput {
        margin-bottom: 20px;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        padding: 15px;
        font-size: 16px;
    }

    .stSelectbox:hover, .stSlider:hover, .stRadio:hover {
        border: 2px solid #003366;
        transition: all 0.3s ease;
    }

    /* Farben für Vorhersage und Info */
    .stSuccess {
        color: #28a745;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
    }

    .stInfo {
        color: #17a2b8;
        font-size: 18px;
        text-align: center;
    }

    /* Design der DataFrame-Tabellen */
    .stDataFrame {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
        padding: 15px;
    }

    /* Spezifische Stiländerungen für die Tabellenzellen */
    .stDataFrame table {
        width: 100%;
        border-collapse: collapse;
    }

    .stDataFrame th, .stDataFrame td {
        padding: 12px;
        text-align: center;
        border-bottom: 2px solid #ddd;
    }

    .stDataFrame th {
        background-color: #003366;
        color: white;
    }

    .stDataFrame td {
        background-color: #f9f9f9;
        color: #333333;
    }

    .stDataFrame tr:hover {
        background-color: #f1f1f1;
    }

    /* Styling der Buttons */
    .stButton>button {
        background-color: #003366;
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 15px 30px;
        border-radius: 25px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        border: none;
        cursor: pointer;
    }

    .stButton>button:hover {
        background-color: #0066cc;
        transition: all 0.3s ease;
    }

    /* Bereich für die Eingabefelder */
    .stSelectbox, .stSlider, .stRadio, .stButton, .stDateInput, .stTimeInput {
        margin-top: 15px;
        margin-bottom: 15px;
    }

    /* Titel der Sektionen */
    h3 {
        color: #003366;
        font-size: 24px;
        font-weight: bold;
        margin-top: 40px;
        text-align: center;
    }
    
    /* Tooltip Styling */
    .stTooltip {
        font-size: 14px;
        color: #666;
        padding: 5px 10px;
        background-color: #f1f1f1;
        border-radius: 5px;
    }

    </style>
""", unsafe_allow_html=True)

st.title("🏟️ Stadium Attendance Prediction App")
st.markdown("🎉⚽ This app predicts stadium attendance.")

# Eingrenzung der Teams und Wettbewerbe
available_home_teams = ['FC Sion', 'FC St. Gallen', 'FC Winterthur', 'FC Zürich',
                        'BSC Young Boys', 'FC Luzern', 'Lausanne-Sport', 'Servette FC',
                        'FC Basel', 'FC Lugano', 'Grasshoppers', 'Yverdon Sport']
available_away_teams = available_home_teams
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

# Vorhersage ausführen
if st.button("Predict Attendance"):
    if temperature_at_match is not None:
        prediction = model_with_weather.predict(input_df)[0]
        weather_status = "Weather data used for prediction."
    else:
        # Droppen der Wetter-bezogenen Spalten
        weather_columns_to_drop = [
            'Weather_Drizzle', 'Weather_Snowy', 'Weather_Partly cloudy', 
            'Temperature (°C)', 'Weather_Rainy'
        ]
        
        # Entferne die Spalten, die das Wetter betreffen, falls sie existieren
        input_df = input_df.drop(columns=[col for col in weather_columns_to_drop if col in input_df.columns])
        
        # Verwende das Modell ohne Wetterdaten
        prediction = model_without_weather.predict(input_df)[0]
        weather_status = "Weather data unavailable. Prediction made without weather information."
    
    st.success(f"Predicted Attendance Percentage: {prediction:.2f}%")
    st.info(weather_status)

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
