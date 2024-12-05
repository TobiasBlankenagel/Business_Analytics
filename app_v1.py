import streamlit as st
import datetime
import pickle
import numpy as np
import requests

# Modelle laden
def load_model(model_path):
    with open(model_path, 'rb') as file:
        return pickle.load(file)

model_with_weather = load_model("./finalized_model_with_weather.sav")
model_without_weather = load_model("./finalized_model_without_weather.sav")

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
time_input = st.text_input("Match Time (e.g., 15:30):")
try:
    match_time = datetime.datetime.strptime(time_input, "%H:%M").hour if time_input else None
except ValueError:
    st.error("Please enter a valid time in HH:MM format.")
    match_time = None

# Vorhersage nur starten, wenn Button geklickt wird
if st.button("Predict Attendance"):
    if match_time is not None:
        # Berechnung direkter Features
        weekday = match_date.strftime('%A')
        month = match_date.month
        day = match_date.day
        holiday = 0  # Beispiel: Feiertage manuell prüfen oder mit einer API

        # Beispiel für Wetter-API-Aufruf (z. B. OpenWeatherMap)
        try:
            weather_api_key = "YOUR_API_KEY"
            weather_response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q=Zurich&appid={weather_api_key}")
            weather_data = weather_response.json()
            weather = weather_data['weather'][0]['main']
            temperature = weather_data['main']['temp'] - 273.15  # Kelvin zu Celsius
        except:
            weather = "Unknown"
            temperature = 20.0  # Standardwert

        # Beispiel-Eingabedaten
        input_data = np.array([[competition, matchday, match_time, home_team, away_team, 
                                weather, temperature, weekday, month, holiday, day]])
        
        # Wähle das richtige Modell
        if weather != "Unknown":
            predicted_attendance = model_with_weather.predict(input_data)
        else:
            predicted_attendance = model_without_weather.predict(input_data)

        st.success(f"Predicted Attendance Percentage: {predicted_attendance[0]:.2f}%")
    else:
        st.error("Please fill in all the fields correctly.")
