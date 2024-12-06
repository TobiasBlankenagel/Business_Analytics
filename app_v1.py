import streamlit as st
import datetime
import pickle
import numpy as np
import requests
import sklearn

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
# Uhrzeit auswählen
match_time = st.time_input(
    "Match Time:",
    value=datetime.time(15, 30),  # Standardwert auf 15:30 setzen
    help="Select the match time in HH:MM format"
)

# Erste Zahl der Uhrzeit als Index verwenden
match_hour = match_time.hour  # Holt nur die Stunde aus der Zeit













# home_team

import requests
import streamlit as st

# Wetterdaten abrufen
def get_weather_data(latitude, longitude, match_date, match_hour):
    # Open-Meteo API-URL mit nur den relevanten Parametern
    api_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}&start_date={match_date}&end_date={match_date}"
        f"&hourly=temperature_2m,weathercode"
        f"&timezone=auto"  # Automatische Zeitzone
    )

    try:
        # API-Anfrage senden
        response = requests.get(api_url)
        response.raise_for_status()
        
        # JSON-Antwort parsen
        weather_data = response.json()


        # Temperatur und Wettercode zum Match-Zeitpunkt abrufen
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

        # Wetterdetails anzeigen
        st.write(f"Temperature at {match_time}: {temperature_at_match}°C")
        st.write(f"Weather at {match_time}: {weather_condition}")
        return temperature_at_match, weather_condition
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch weather data: {e}")
        return None, None


# Koordinaten der Stadien
stadium_coordinates = {
    'FC Sion': {'latitude': 46.233333, 'longitude': 7.376389},
    'FC St. Gallen': {'latitude': 47.408333, 'longitude': 9.310278},
    'FC Winterthur': {'stadium': 'Stadion Schützenwiese', 'latitude': 47.505278, 'longitude': 8.724167},
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

# Beispiel für die Benutzung
if home_team and match_date and match_time:
    coordinates = stadium_coordinates[home_team]
    latitude = coordinates['latitude']
    longitude = coordinates['longitude']

    st.write(f"Fetching weather data for {home_team}...")
    temperature_at_match, weather_condition = get_weather_data(latitude, longitude, match_date, match_hour)

    if temperature_at_match is not None:
        st.success(f"Temperature at match time ({match_time}): {temperature_at_match}°C")
        st.success(f"Weather at match time ({match_time}): {weather_condition}")
else:
    st.error("Please fill in all fields.")



####### SAMMELN DER DATEN #############
## Competition -- Userangabe
## Matchday -- Userangabe
## Time -- Userangabe
## Home Team -- Userangabe
## Ranking Home Team
## Away Team -- Userangabe
## Ranking Away Team
## Weather -- API Abfrage
## Temperature (°C) -- API Abfrage
## Weekday -- Userangabe
## Month -- Userangabe
## Day -- Userangabe
## Goals Scored in Last 5 Games
## Goals Conceded in Last 5 Games
## Number of Wins in Last 5 Games

competition = competition # bereits initialisiert
matchday = matchday # bereits initialisiert
match_hour = match_hour # bereits initialisiert
home_team = home_team # bereits initialisiert
away_team = away_team # bereits initialisiert
weather_condition = weather_condition # bereits initialisiert
temperature_at_match = temperature_at_match # bereits initialisiert
Weekday = match_date.strftime('%A')  # Gibt den Wochentag als vollständigen Namen zurück (z. B. "Monday")
Month = match_date.month  # Extrahiert den Monat (1-12)
Day = match_date.day  # Extrahiert den Tag des Monats (1-31)



######## werden noch mit API oder selbst gesuchten Daten benötigt:
# Ranking Home Team
# Ranking Away Team
# Goals_Scored_in_Last_5_Games
# Goals_Conceded_in_Last_5_Games
# Number_of_Wins_in_Last_5_Games


# so guys im working on the website right now but there are still some things to do. Wir wollen ja dass 
# der User Informationen angibt (z.b. heimteam, gegner, turnier etc.) und darauf basierend die stadtion attendance schätzen. 
# die variablen auf die wir dann mit dem modell die attendance vorhersagen wollen enthalten viele "live daten" wie. zb wetter, 
# heimteam ranking, oder goals scored in the last 5 games. diese daten müssten wir entweder von einer api abfragen (das habe ich 
# fürs wetter schon eingebaut) oder selber uns daten ausdenken. Für Liga daten wie rankings oder "goals scored in the last 5 games" 
# finde ich leider keine passende api. da wir das projekt nächste woche schon präsentieren würde ich vorschlagen dass wir dafür uns 
# selber ein minidatensatz zusammenbauen, den wir dann stellvertretend daten abfragen für variablen, für die wir keine passende api 
# gefunden haben. deshalb wäre meine bitte wenn ihr mit eurer webscrapping technik die folgenden daten in einem minidatensatz aufbereitet: 
# für jedes der 12 schweizer teams die "goals scored in the last 5 games", "Goals_Conceded_in_Last_5_Games" , "Number_of_Wins_in_Last_5_Games" 
# und dann noch den aktuellen stand von jedem team. Am besten ein Datensatz






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
        input_data = np.array([[competition, matchday, match_hour, home_team, away_team, 
                                weather, temperature, weekday, month, holiday, day]])
        
        # Wähle das richtige Modell
        if weather != "Unknown":
            predicted_attendance = model_with_weather.predict(input_data)
        else:
            predicted_attendance = model_without_weather.predict(input_data)

        st.success(f"Predicted Attendance Percentage: {predicted_attendance[0]:.2f}%")
    else:
        st.error("Please fill in all the fields correctly.")
