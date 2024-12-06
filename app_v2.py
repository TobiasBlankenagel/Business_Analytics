import streamlit as st
import pandas as pd
import numpy as np
import datetime

# Streamlit-Konfiguration
st.set_page_config(
    page_title="🏟️ Stadium Attendance Prediction",
    page_icon="⚽",
    layout="wide"
)

# Titelbereich mit Subheader
st.title("⚽🏟️ Stadium Attendance Prediction App")
st.markdown(
    """
    Welcome to the **Stadium Attendance Prediction App**! 🎉  
    Predict the attendance for upcoming matches with insights from weather, team stats, and more.
    """
)

# Eingrenzung der Teams und Wettbewerbe
available_home_teams = ['FC Sion', 'FC St. Gallen', 'FC Winterthur', 'FC Zürich',
                        'BSC Young Boys', 'FC Luzern', 'Lausanne-Sport', 'Servette FC',
                        'FC Basel', 'FC Lugano', 'Grasshoppers', 'Yverdon Sport']
available_away_teams = available_home_teams + ['Unknown']
available_competitions = ['Super League', 'UEFA Conference League', 'Swiss Cup', 
                          'UEFA Europa League', 'UEFA Champions League']

# Eingabebereich (Mehrspaltig)
col1, col2 = st.columns(2)
with col1:
    home_team = st.selectbox("🏠 Home Team:", available_home_teams)
    competition = st.selectbox("🏆 Competition:", available_competitions)

with col2:
    if competition == "Super League":
        away_team = st.selectbox("🛫 Away Team:", available_home_teams)
    elif competition == "Swiss Cup":
        away_team = st.selectbox("🛫 Away Team:", available_away_teams)
    else:
        away_team = "Unknown"

# Eingabe für Datum und Uhrzeit
match_date = st.date_input("📅 Match Date:", min_value=datetime.date.today())
match_time = st.time_input("🕒 Match Time:", value=datetime.time(15, 30))
match_hour = match_time.hour

# Statistiken anzeigen
st.markdown("### 📊 Team Statistics")
stats_col1, stats_col2 = st.columns(2)

# Teamstatistiken für Heimteam
with stats_col1:
    st.subheader(f"🏠 {home_team} Statistics")
    team_stats = {
        "Metric": [
            "Ranking", "Goals Scored (Last 5 Games)", "Goals Conceded (Last 5 Games)",
            "Wins (Last 5 Games)", "Last 1 Game", "Last 2 Games", 
            "Last 3 Games", "Last 4 Games", "Last 5 Games"
        ],
        "Value": [1, 10, 5, 3, "Win", "Lose", "Tie", "Win", "Win"]  # Beispielwerte
    }
    df_home_stats = pd.DataFrame(team_stats)
    st.table(df_home_stats)

# Teamstatistiken für Auswärtsteam
with stats_col2:
    st.subheader(f"🛫 {away_team} Statistics")
    away_stats = {
        "Metric": [
            "Ranking", "Goals Scored (Last 5 Games)", "Goals Conceded (Last 5 Games)",
            "Wins (Last 5 Games)", "Last 1 Game", "Last 2 Games", 
            "Last 3 Games", "Last 4 Games", "Last 5 Games"
        ],
        "Value": [5, 8, 7, 2, "Lose", "Win", "Tie", "Lose", "Lose"]  # Beispielwerte
    }
    df_away_stats = pd.DataFrame(away_stats)
    st.table(df_away_stats)

# Wetterinformationen
st.markdown("### 🌤️ Weather Conditions at the Stadium")
st.info(
    f"""
    **Weather Forecast**:  
    - **Temperature**: 15°C  
    - **Condition**: Partly Cloudy  
    """
)

# Vorhersagebereich
st.markdown("### 🤖 Prediction")
if st.button("Predict Attendance"):
    st.success(f"🎉 The predicted attendance percentage is **85.75%**.")
    st.balloons()
