import streamlit as st
import requests
import pandas as pd

# Page configuration
st.set_page_config(page_title="India Air Quality Analyzer", page_icon="🌫️", layout="wide")

st.title("🌫️ Air Quality Analysis of Indian Cities")
st.markdown("Real-time AQI, PM2.5, PM10, and pollutant breakdown across major Indian cities.")

# Coordinates for major Indian cities
CITIES = {
    "New Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bengaluru": (12.9716, 77.5946),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462)
}

@st.cache_data(ttl=600)  # Cache data for 10 minutes
def fetch_air_quality(lat, lon):
    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}&longitude={lon}&current=us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone"
        f"&hourly=us_aqi,pm2_5,pm10&forecast_days=1"
    )
    response = requests.get(url)
    return response.json()

def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good", "🟢"
    elif aqi <= 100:
        return "Moderate", "🟡"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "🟠"
    elif aqi <= 200:
        return "Unhealthy", "🔴"
    elif aqi <= 300:
        return "Very Unhealthy", "🟣"
    else:
        return "Hazardous", "🟤"

# Sidebar for city selection
st.sidebar.header("Dashboard Controls")
selected_city = st.sidebar.selectbox("Select Primary City for Deep Analysis", list(CITIES.keys()))
compare_cities = st.sidebar.multiselect(
    "Select Cities to Compare", list(CITIES.keys()), default=["New Delhi", "Mumbai", "Bengaluru", "Kolkata"]
)

# --- SECTION 1: Selected City Overview ---
st.header(f"📍 Live Air Quality: {selected_city}")
lat, lon = CITIES[selected_city]
data = fetch_air_quality(lat, lon)
current = data["current"]

aqi_val = current["us_aqi"]
category, icon = get_aqi_category(aqi_val)

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current AQI (US Standard)", f"{aqi_val} {icon}", category)
col2.metric("PM2.5 (µg/m³)", f"{current['pm2_5']}")
col3.metric("PM10 (µg/m³)", f"{current['pm10']}")
col4.metric("Nitrogen Dioxide (NO₂)", f"{current['nitrogen_dioxide']} µg/m³")

# Hourly Trend Chart
st.subheader(f"📈 24-Hour Pollutant Trend ({selected_city})")
hourly_df = pd.DataFrame({
    "Time": pd.to_datetime(data["hourly"]["time"]),
    "PM2.5 (µg/m³)": data["hourly"]["pm2_5"],
    "PM10 (µg/m³)": data["hourly"]["pm10"],
    "AQI": data["hourly"]["us_aqi"]
}).set_index("Time")

st.line_chart(hourly_df[["PM2.5 (µg/m³)", "PM10 (µg/m³)"]])

# --- SECTION 2: Multi-City Comparison ---
if compare_cities:
    st.divider()
    st.header("🏙️ Multi-City Comparison")
    
    comp_list = []
    for city in compare_cities:
        c_lat, c_lon = CITIES[city]
        c_data = fetch_air_quality(c_lat, c_lon)["current"]
        cat, _ = get_aqi_category(c_data["us_aqi"])
        comp_list.append({
            "City": city,
            "lat": c_lat,
            "lon": c_lon,
            "AQI": c_data["us_aqi"],
            "Status": cat,
            "PM2.5": c_data["pm2_5"],
            "PM10": c_data["pm10"],
            "CO": c_data["carbon_monoxide"],
            "SO₂": c_data["sulphur_dioxide"],
            "O₃": c_data["ozone"]
        })
    
    comp_df = pd.DataFrame(comp_list)
    
    # Bar chart & Data table side by side
    left_col, right_col = st.columns([1.2, 1])
    with left_col:
        st.subheader("AQI Comparison")
        st.bar_chart(comp_df.set_index("City")["AQI"])
    with right_col:
        st.subheader("Detailed Pollutant Breakdown")
        st.dataframe(comp_df.drop(columns=["lat", "lon"]), use_container_width=True)

    # Interactive Map
    st.subheader("🗺️ Geographic View")
    st.map(comp_df[["lat", "lon"]])
