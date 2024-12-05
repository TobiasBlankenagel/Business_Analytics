import streamlit as st
import pandas as pd
import datetime
import pickle

# Streamlit-Seitenkonfiguration
st.set_page_config(
    page_title="Stadium Capacity Prediction",
    page_icon="🏟️",
    layout="wide"
)




# Titel und Beschreibung der App
st.title("🏟️ Stadium Capacity Prediction App")
st.markdown(
    "🎉⚽ This application predicts the stadium capacity utilization based on the home team, away team, and match date. "
    "Predictions include weather factors if the match is within 2 weeks."
)

#### Inputs for the Prediction
st.header("Match Prediction Input")



# Eingrenzung der Teams
available_home_teams = [
    'FC Sion', 'FC St. Gallen', 'FC Winterthur', 'FC Zürich',
    'BSC Young Boys', 'FC Luzern', 'Lausanne-Sport', 'Servette FC',
    'FC Basel', 'FC Lugano', 'Grasshoppers', 'Yverdon Sport'
]

# Away Teams hinzufügen mit "Unbekannt"
available_away_teams = available_home_teams + ['Unknown']

# Eingrenzung der Wettbewerbe (Challenge League ausgeschlossen)
available_competitions = [
    'Super League', 'UEFA Conference League', 'Swiss Cup', 
    'UEFA Europa League', 'UEFA Champions League'
]


# Input-Felder für Benutzer (neue Struktur)
# Home Team wählen
home_team = st.selectbox("Home Team:", available_home_teams) #hier aktuelle Liga Position abrufen mit API

# Wettbewerb auswählen
competition = st.selectbox("Competition:", available_competitions)


# Away Team: Eingabefeld oder automatisch "Unknown"
if competition == "Super League":
    away_team = st.selectbox("Away Team:", available_home_teams)
elif competition == "Swiss Cup":
    away_team = st.selectbox("Away Team:", available_away_teams)
else:
    st.info("Away Team is automatically set to 'Unknown' for international competitions.")
    away_team = "Unknown"

# Matchday auswählen
if competition == "Super League":
    matchday = st.slider("Matchday:", min_value=1, max_value=36, step=1)
elif competition == "Swiss Cup":
    matchday = "Knockout"
    st.info("Matchday is automatically set to 'Knockout' for the Swiss Cup.")
else:
    matchday = st.radio("Matchday Type:", options=["Group", "Knockout"])

# Datum auswählen
match_date = st.date_input(
    "Match Date:", 
    min_value=datetime.date.today(),  # Min: Heute   # hir mit API abfragen ob Ferien
    max_value=datetime.date.today() + datetime.timedelta(days=90)  # Maximal 3 Monate in der Zukunft
)

# Uhrzeit auswählen
time_input = st.text_input("Match Time (e.g., 15:30):", placeholder="Enter match time in HH:MM format")
## Uhrzeit (Format zwar in zb 20:30, aber es wird immer nur die erste Zahl, also hier 20 genommen) abfragen
# Überprüfen, ob die Zeit gültig ist
try:
    match_time = datetime.datetime.strptime(time_input, "%H:%M").time() if time_input else None
    valid_time = True
except ValueError:
    st.error("Please enter a valid time in HH:MM format.")
    valid_time = False

# Temporäre Logik für Vorhersagen
if home_team and away_team and match_date:
    today = datetime.date.today()
    days_until_match = (match_date - today).days

    if days_until_match <= 14:
        st.success(f"Prediction (with weather): The capacity utilization is estimated for **{home_team}** vs **{away_team}** on **{match_date}**.")
        ## mit API abfragen wie Wetter am Datum ist
    else:
        st.success(f"Prediction (without weather): The capacity utilization is estimated for **{home_team}** vs **{away_team}** on **{match_date}**.")
else:
    st.info("Please fill in all the fields to make a prediction.")

#### Batch Prediction Section
st.header("Batch Predictions")

uploaded_data = st.file_uploader("Upload a CSV file with match data for batch predictions")

if uploaded_data is not None:
    st.write("Processing uploaded data...")
    # Temporär anzeigen, was hochgeladen wurde (ohne Verarbeitung)
    uploaded_df = pd.read_csv(uploaded_data)
    st.write(uploaded_df)

# Hinweis für die Benutzer
st.caption("Note: Predictions for games more than 3 months in advance are not supported.")
