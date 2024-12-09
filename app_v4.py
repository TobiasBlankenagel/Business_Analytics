import streamlit as st
import pandas as pd
import numpy as np
import pickle
import requests
import datetime
import matplotlib
import matplotlib.pyplot as plt
import base64
import io


############################## MODELS & STREAMLIT CONFIGURATION ##############################

# Function to load a model using pickle
def load_model(model_path):
    with open(model_path, 'rb') as file:
        return pickle.load(file)

# Load models
model_with_weather = load_model("./finalized_model_with_weather.sav")
model_without_weather = load_model("./finalized_model_without_weather.sav")

# Configure Streamlit page
st.set_page_config(
    page_title="Stadium Attendance Prediction",  # Title of the app
    page_icon="🏟️",  # Icon for the app
    layout="wide"  # Use the entire width of the page
)


############################## CUSTOM STYLING (CSS) ##############################

# Add custom CSS for consistent and modern design
st.markdown("""
    <style>
    
    .stSelectbox, .stSlider, .stRadio, .stExpander {
        margin-top: 10px;
        border-radius: 12px;
        background-color: #ffffff;
        padding: 14px 22px;
        font-size: 16px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }

    .stExpander details {
        border-color: #ffffff;
    }

    .stDateInput, .stTimeInput {
        margin-top: 5px;
        border-radius: 12px;
        background-color: #ffffff;
        padding: 14px 22px;
        font-size: 16px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }

    /* Styling der Buttons */
    .stButton>button {
        background-color: #003366;
        color: white; /* Schriftfarbe wird auf weiß gesetzt */
        font-size: 18px;
        font-weight: bold;
        padding: 12px 30px;
        border-radius: 25px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: none;
        cursor: pointer;
        margin-bottom: 20px;
    }

    /* Hover-Effekt für den Button */
    .stButton>button:hover {
        background-color: #0066cc;
        color: white; /* Schriftfarbe bleibt weiß im Hover-Zustand */
        transition: all 0.3s ease;
    }


    </style>
""", unsafe_allow_html=True)


############################## APP HEADER ##############################

# Display the app's main title and description
st.markdown("""
    <h1 style="color: #003366; text-align: center; font-size: 48px; font-weight: bold; margin-top: -60px;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);">🏟️ Stadium Attendance Prediction App</h1>
    <div style="text-align: center; padding: 7px; padding-top:20px; background-color: #f9f9f9; border-radius: 15px; 
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-bottom:20px">
        <p style="font-size: 20px; color: #555555;">🎉⚽ This app predicts stadium attendance based on various factors 
        such as the teams playing, weather conditions, and matchday info. Use the inputs below to get the prediction!</p>
    </div>
""", unsafe_allow_html=True)


############################## INPUT FIELDS ##############################

# Define available teams and competitions
available_home_teams = ['FC Sion', 'FC St. Gallen', 'FC Winterthur', 'FC Zürich',
                        'BSC Young Boys', 'FC Luzern', 'Lausanne-Sport', 'Servette FC',
                        'FC Basel', 'FC Lugano', 'Grasshoppers', 'Yverdon Sport']
available_away_teams = available_home_teams
available_competitions = ['Super League', 'UEFA Conference League', 'Swiss Cup', 
                          'UEFA Europa League', 'UEFA Champions League']

# Divide input fields into two columns for better layout
col1, col2 = st.columns([2, 2])

# Left column: Home Team and Competition inputs
with col1:
    home_team = st.selectbox("🏠 Home Team:", available_home_teams)  # Home team selection
    competition = st.selectbox("🏆 Competition:", available_competitions)  # Competition selection

# Right column: Away Team and Matchday inputs
with col2:
    # Dynamisch die Liste der verfügbaren Away-Teams anpassen
    available_away_teams_dynamic = [team for team in available_home_teams if team != home_team]
    # Away team selection
    if competition == "Super League":
        away_team = st.selectbox("🌍 Away Team:", available_away_teams_dynamic)  
    elif competition == "Swiss Cup":
        away_team = st.selectbox("🌍 Away Team:", available_away_teams_dynamic)
    else:
        away_team = "Unknown"

    if competition == "Super League":
        matchday = st.slider("📅 Matchday:", min_value=1, max_value=36, step=1)  # Matchday slider for Super League
    else:
        matchday = st.radio("🏅 Matchday Type:", options=["Qualification", "Group Stage", "Knockout Stage"])  # Radio for non-league competitions

# Add match date and time inputs
col3, col4 = st.columns([2, 2])

# Left column: Match date
with col3:
    match_date = st.date_input(
        "📅 Match Date:", 
        min_value=datetime.date.today(),
        key="match_date_input"
    )

# Right column: Match time
with col4:
    match_time = st.time_input(
        "🕒 Match Time:", 
        value=datetime.time(15, 30),
        help="Select the match time in HH:MM format",
        key="match_time_input"
    )
    match_hour = match_time.hour  # Extract hour from time input
    weekday = match_date.strftime("%A")  # Get the weekday name for the selected date


############################## WEATHER DATA ##############################

# Function to fetch weather data from an API
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
        # Map weather codes to human-readable conditions
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

# Define stadium coordinates
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

# Fetch weather data based on home team and match information
if home_team and match_date and match_time:
    coordinates = stadium_coordinates[home_team]
    latitude = coordinates['latitude']
    longitude = coordinates['longitude']
    temperature_at_match, weather_condition = get_weather_data(latitude, longitude, match_date, match_hour)

# Weather display and emoji mapping logic
def get_weather_emoji(weather_condition):
    weather_emoji = {
        "Clear or mostly clear": "☀️", 
        "Partly cloudy": "⛅", 
        "Rainy": "🌧️", 
        "Drizzle": "🌦️", 
        "Snowy": "❄️",  
        "Unknown": "🌫️",  
    }
    return weather_emoji.get(weather_condition, "🌫️")

# Display weather data in a styled container
if temperature_at_match is not None and weather_condition is not None and weather_condition != "Unknown":
    weather_emoji = get_weather_emoji(weather_condition)
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom:25px; margin-top:10px">
            <h3 style="color: #003366;">Weather at the Match</h3>
            <p style="font-size: 18px; color: #333333;">
                The weather at the match will be <strong style="color: #007bff;">{weather_condition} {weather_emoji}</strong> 
                with a temperature of <strong style="color: #007bff;">{temperature_at_match}°C</strong> 🌡.
            </p>
        </div>
    """, unsafe_allow_html=True)
elif temperature_at_match is not None:
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom:25px; margin-top:10px">
            <h3 style="color: #003366;">Weather at the Match</h3>
            <p style="font-size: 18px; color: #333333;">
                The temperature at the match will be <strong style="color: #007bff;">{temperature_at_match}°C</strong> 🌡.
            </p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom:25px; margin-top:10px">
            <h3 style="color: #003366;">Weather at the Match</h3>
            <p style="font-size: 18px; color: #333333;">
                Unfortunately, the weather data is unavailable at the moment. 😞
            </p>
        </div>
    """, unsafe_allow_html=True)


################### Rankings and Team Data Processing ##############################

# Load league data from a CSV file
league_data = pd.read_csv('new_league_data.csv')

# Retrieve data for the selected home team
home_team_data = league_data[league_data['Team'] == home_team]

# Handle the case where the home team is not found in the data
if home_team_data.empty:
    st.error(f"Home team '{home_team}' not found in the data.")
else:
    home_team_data = home_team_data.iloc[0]

# Handle the away team data; assign default values if "Unknown"
if away_team == "Unknown":
    ranking_away_team = 0  # Default ranking for unknown away team
else:
    away_team_data = league_data[league_data['Team'] == away_team]
    if away_team_data.empty:
        st.error(f"Away team '{away_team}' not found in the data.")
    else:
        away_team_data = away_team_data.iloc[0]
        ranking_away_team = away_team_data['Ranking']
        goals_scored_away_team = away_team_data['Goals_Scored_in_Last_5_Games']
        goals_conceded_away_team = away_team_data['Goals_Conceded_in_Last_5_Games']
        wins_away_team = away_team_data['Number_of_Wins_in_Last_5_Games']

# Retrieve relevant statistics for the home team if the data exists
if not home_team_data.empty:
    ranking_home_team = home_team_data['Ranking']
    goals_scored_home_team = home_team_data['Goals_Scored_in_Last_5_Games']
    goals_conceded_home_team = home_team_data['Goals_Conceded_in_Last_5_Games']
    wins_home_team = home_team_data['Number_of_Wins_in_Last_5_Games']


################### Preparing Input Data for the Model ##############################

# Define the input features for the prediction model
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
    'Weekday': match_date.strftime("%A"),
    'Month': match_date.month,
    'Day': match_date.day,
    'Goals Scored in Last 5 Games': goals_scored_home_team,
    'Goals Conceded in Last 5 Games': goals_conceded_home_team,
    'Number of Wins in Last 5 Games': wins_home_team,
}

# Convert the input features into a DataFrame
input_df = pd.DataFrame([input_features])

# List of expected columns for the model
expected_columns = [
    'Time', 'Ranking Home Team', 'Ranking Away Team', 'Temperature (°C)', 'Month', 'Day',
    'Goals Scored in Last 5 Games', 'Goals Conceded in Last 5 Games', 'Number of Wins in Last 5 Games',
    'Competition_Super League', 'Competition_Swiss Cup', 'Competition_UEFA Champions League',
    'Competition_UEFA Conference League', 'Competition_UEFA Europa League', 'Matchday_10', 'Matchday_11', 'Matchday_12', 'Matchday_13',
    'Matchday_14', 'Matchday_15', 'Matchday_16', 'Matchday_17', 'Matchday_18', 'Matchday_19',
    'Matchday_2', 'Matchday_20', 'Matchday_21', 'Matchday_22', 'Matchday_23', 'Matchday_24', 'Matchday_25',
    'Matchday_26', 'Matchday_27', 'Matchday_28', 'Matchday_29', 'Matchday_3', 'Matchday_30', 'Matchday_31',
    'Matchday_32', 'Matchday_33', 'Matchday_34', 'Matchday_35', 'Matchday_36', 'Matchday_37', 'Matchday_38', 
    'Matchday_4', 'Matchday_5', 'Matchday_6', 'Matchday_7',
    'Matchday_8', 'Matchday_9', 
    'Matchday_Group Stage',
    'Matchday_Knockout Stage', 'Matchday_Qualification', 'Home Team_FC Basel', 'Home Team_FC Lugano',
    'Home Team_FC Luzern', 'Home Team_FC Sion', 'Home Team_FC St. Gallen', 'Home Team_FC Winterthur',
    'Home Team_FC Zürich', 'Home Team_Grasshoppers', 'Home Team_Lausanne-Sport', 'Home Team_Servette FC',
    'Home Team_Yverdon Sport', 'Away Team_FC Basel', 'Away Team_FC Lugano', 'Away Team_FC Luzern',
    'Away Team_FC Sion', 'Away Team_FC St. Gallen', 'Away Team_FC Winterthur', 'Away Team_FC Zürich',
    'Away Team_Grasshoppers', 'Away Team_Lausanne-Sport', 'Away Team_Servette FC', 'Away Team_Unknown',
    'Away Team_Yverdon Sport', 'Weather_Drizzle', 'Weather_Partly cloudy', 'Weather_Rainy',
    'Weather_Snowy', 'Weekday_Monday', 'Weekday_Saturday', 'Weekday_Sunday', 'Weekday_Thursday',
    'Weekday_Tuesday', 'Weekday_Wednesday'
]

# Perform one-hot encoding for categorical columns
categorical_columns = [
    "Competition", "Matchday", "Home Team", "Away Team", "Weather", "Weekday"
]

# Apply one-hot encoding to input DataFrame
input_df = pd.get_dummies(pd.DataFrame([input_features]), columns=categorical_columns, drop_first=False)


# Add missing columns as zeros for any expected columns not generated during one-hot encoding
for col in expected_columns:
    if col not in input_df.columns:
        input_df[col] = 0

# Ensure the DataFrame columns are in the correct order
input_df = input_df[expected_columns]

# Ensure all values are of type float for compatibility with the model
input_df = input_df.astype(float)

# Check for any missing columns that could break the model
missing_columns = [col for col in expected_columns if col not in input_df.columns]
if missing_columns:
    raise ValueError(f"Fehlende Spalten in den Eingabedaten: {missing_columns}")


################### Predicting Attendance ##############################

# Define team-specific data, including stadium capacity and attendance thresholds
team_data = {
    "BSC Young Boys": {"max_capacity": 31783, "attendance_30th_percentile": 25282.1, "attendance_70th_percentile": 31120.0},
    "FC Basel": {"max_capacity": 38512, "attendance_30th_percentile": 19527.0, "attendance_70th_percentile": 22666.5},
    "FC Lugano": {"max_capacity": 6330, "attendance_30th_percentile": 2843.5, "attendance_70th_percentile": 3509.6},
    "FC Luzern": {"max_capacity": 16800, "attendance_30th_percentile": 10105.5, "attendance_70th_percentile": 13171.9},
    "FC Sion": {"max_capacity": 16232, "attendance_30th_percentile": 6500.0, "attendance_70th_percentile": 9480.0},
    "FC St. Gallen": {"max_capacity": 20029, "attendance_30th_percentile": 15683.8, "attendance_70th_percentile": 18482.3},
    "FC Winterthur": {"max_capacity": 8550, "attendance_30th_percentile": 5100.0, "attendance_70th_percentile": 8400.0},
    "FC Zürich": {"max_capacity": 26104, "attendance_30th_percentile": 10870.0, "attendance_70th_percentile": 15393.0},
    "Grasshoppers": {"max_capacity": 26104, "attendance_30th_percentile": 4049.6, "attendance_70th_percentile": 5879.0},
    "Lausanne-Sport": {"max_capacity": 12544, "attendance_30th_percentile": 3773.6, "attendance_70th_percentile": 5728.0},
    "Servette FC": {"max_capacity": 30084, "attendance_30th_percentile": 6076.6, "attendance_70th_percentile": 10860.1},
    "Yverdon Sport": {"max_capacity": 6600, "attendance_30th_percentile": 712.6, "attendance_70th_percentile": 2400.0}
}

# Predict attendance when the user clicks the button
if st.button("🎯 Predict Attendance"):
    # Use weather-based model if weather data is available
    if temperature_at_match is not None:
        prediction = model_with_weather.predict(input_df)[0] * 100
        weather_status = "Weather data used for prediction."

    # Drop weather-related columns for the fallback model
    else:
        weather_columns_to_drop = [
            'Weather_Drizzle', 'Weather_Snowy', 'Weather_Partly cloudy', 
            'Temperature (°C)', 'Weather_Rainy'
        ]
        input_df = input_df.drop(columns=[col for col in weather_columns_to_drop if col in input_df.columns])
        prediction = model_without_weather.predict(input_df)[0] * 100
        weather_status = "Weather data unavailable. Prediction made without weather information."
    
    # Calculate absolute attendance based on prediction percentage and stadium capacity
    home_team_name = home_team
    team_info = team_data.get(home_team_name, None)

    if team_info:
        max_capacity = team_info["max_capacity"]
        predicted_attendance = min(((prediction / 100) * max_capacity).round(), max_capacity)
        attendance_30th = team_info["attendance_30th_percentile"]
        attendance_70th = team_info["attendance_70th_percentile"]

        # Determine attendance status based on thresholds
        if predicted_attendance < attendance_30th:
            attendance_status = "Low attendance 🚶‍♂️"
        elif predicted_attendance > attendance_70th:
            attendance_status = "High attendance 🏟️"
        else:
            attendance_status = "Normal attendance ⚖️"

        # Display attendance status in Streamlit
        st.success(f"Attendance Status: {attendance_status}")

        # Create a horizontal bar chart to visualize attendance prediction
        fig, ax = plt.subplots(figsize=(10, 2.5))  # Adjust figure size for better integration
        ax.barh(
            y=[0], 
            width=[predicted_attendance / max_capacity], 
            height=0.5,  # Slightly thinner bar for a sleek look
            color="#28a745", 
            edgecolor="black",
            alpha=0.8  # Add transparency for softer appearance
        )

        # Add vertical lines for attendance thresholds
        ax.axvline(x=attendance_30th / max_capacity, color="red", linestyle="--", label="30th Percentile", linewidth=1.2)
        ax.axvline(x=attendance_70th / max_capacity, color="blue", linestyle="--", label="70th Percentile", linewidth=1.2)

        # Customize the chart background and frame
        fig.patch.set_facecolor("#f8f9fa")  # Match Streamlit's light gray background
        ax.set_facecolor("#ffffff")  # Set chart background to white
        ax.spines['top'].set_visible(False)  
        ax.spines['right'].set_visible(False) 

        # Configure axis limits and labels
        ax.set_xlim(0, 1) 
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1])  # Define tick positions
        ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=12) 
        ax.set_yticks([])

        # Add a legend and adjust its position
        ax.legend(
            loc="lower center", 
            bbox_to_anchor=(0.5, -0.4),  # Move the legend below the chart
            ncol=2, 
            fontsize=12,
            frameon=False 
        )

        # Add a clear title for the chart
        ax.set_title(
            f"Predicted Attendance: {predicted_attendance:.0f} of {max_capacity} ({prediction:.2f}%)", 
            fontsize=14,
            pad=15,
            color="#333333" 
        )

        # Save the chart to a buffer for embedding
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=100) 
        buf.seek(0)
        encoded_image = base64.b64encode(buf.read()).decode("utf-8")

        # Embed the chart into the Streamlit app
        st.markdown(
            f"""
            <div style="background-color: #f9f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; 
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <h3 style="text-align: center; color: #003366;">Attendance Prediction Details</h3>
                <img src="data:image/png;base64,{encoded_image}" style="display: block; margin: auto;"/>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.info(weather_status)


################### Additional Information: League Table #################################

# Function to generate icons for game results
def game_result_icons(row):
    # Map result to an emoji
    result_mapping = {"Win": "✅", "Lose": "❌", "Tie": "➖"}
    # Create a string of icons for the last 5 game results
    return "".join(result_mapping.get(row[col], "❓") for col in [
        "Last_1_Game_Result",
        "Last_2_Game_Result",
        "Last_3_Game_Result",
        "Last_4_Game_Result",
        "Last_5_Game_Result"
    ])

# Add a column with icons for the last 5 games
league_data["Last_5_Games_Icons"] = league_data.apply(game_result_icons, axis=1)

# Create a filtered league table with selected columns
league_table = league_data[[
    "Ranking", "Team", "Points", "Games_Played", 
    "Total_Goals_Scored", "Total_Goals_Conceded", 
    "Last_5_Games_Icons"
]]

# Sort the league table by ranking (ascending order)
league_table = league_table.sort_values(by="Ranking", ascending=True)

# Rename columns to include emojis for better readability
league_table = league_table.rename(columns={
    "Ranking": "🏅 Ranking",
    "Team": "🏟️ Team",
    "Points": "🎯 Points",
    "Games_Played": "🕒 Games Played",
    "Total_Goals_Scored": "⚽ Total Goals Scored",
    "Total_Goals_Conceded": "🛡️ Total Goals Conceded",
    "Last_5_Games_Icons": "📊 Last 5 Games"
})


################### Styling and HTML for League Table #################################

# Define CSS for styling the table
table_css = """
<style>
    table {
        width: 100%;
        border-collapse: collapse;
        border: 1px solid #ddd;
        font-family: Arial, sans-serif;
        margin: 20px 0;
        border-radius: 8px;  /* Abgeflachte Ecken */
        overflow: hidden;    /* Verhindert Überlauf */
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }
    th {
        background-color: #f4f4f4;
        font-weight: bold;
        font-size: 14px;
        color: #333;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    tr:nth-child(odd) {
        background-color: #ffffff;
    }
    tr:hover {
        background-color: #f1f1f1;
    }
    td {
        font-size: 13px;
        color: #555;
    }
    .highlight-home {
        background-color: rgba(0, 123, 255, 0.4) !important;
        font-weight: bold !important;
    }
    .highlight-away {
        background-color: rgba(0, 123, 255, 0.15) !important;
    }
</style>
"""

# Function to add a CSS class to highlight rows for home or away teams
def highlight_teams_html(row):
    if row["🏟️ Team"] == home_team:
        return '<tr class="highlight-home">'
    elif row["🏟️ Team"] == away_team:
        return '<tr class="highlight-away">'
    return "<tr>"

# Generate HTML table with CSS styling and highlighted rows
table_html = '<table>'
table_html += '<thead><tr>' + ''.join(f'<th>{col}</th>' for col in league_table.columns) + '</tr></thead>'
table_html += '<tbody>'
for _, row in league_table.iterrows():
    table_html += highlight_teams_html(row)  # Add highlight classes for home/away teams
    table_html += ''.join(f'<td>{row[col]}</td>' for col in league_table.columns)
    table_html += '</tr>'
table_html += '</tbody></table>'

# Combine CSS and HTML
styled_table_html = table_css + table_html


################### Toggle Button for League Table #################################

# Create an expander for the league table
with st.expander("🏆 Show League Table"):
    # Render the styled HTML table inside the expander
    st.markdown(styled_table_html, unsafe_allow_html=True)

