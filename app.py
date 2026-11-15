import streamlit as st
import requests
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="India Air Quality Analyzer",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App Title & Intro
st.title("🌫️ India Air Quality Intelligence")
st.markdown("Monitor real-time air pollution levels, health risks, and pollutant trends across major Indian cities.")
st.divider()

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
        return "Good", "🟢", "Air quality is satisfactory and poses little or no risk."
    elif aqi <= 100:
        return "Moderate", "🟡", "Acceptable quality; sensitive individuals may experience minor irritation."
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "🟠", "Elderly and children should reduce outdoor exertion."
    elif aqi <= 200:
        return "Unhealthy", "🔴", "Everyone may begin to experience health effects."
    elif aqi <= 300:
        return "Very Unhealthy", "🟣", "Health alert: everyone may experience more serious health effects."
    else:
        return "Hazardous", "🟤", "Health warning of emergency conditions. Stay indoors."

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎛️ Control Panel")
selected_city = st.sidebar.selectbox("Select City for Deep Dive", list(CITIES.keys()))
compare_cities = st.sidebar.multiselect(
    "Select Cities for Comparison", 
    list(CITIES.keys()), 
    default=["New Delhi", "Mumbai", "Bengaluru", "Kolkata"]
)

# --- CREATE CLEAN TABS ---
tab1, tab2 = st.tabs(["📍 City Deep Dive", "🏙️ Multi-City Comparison"])

# ================= TAB 1: CITY DEEP DIVE =================
with tab1:
    st.subheader(f"Live Status: {selected_city}")
    
    lat, lon = CITIES[selected_city]
    data = fetch_air_quality(lat, lon)
    current = data["current"]

    aqi_val = current["us_aqi"]
    category, icon, advice = get_aqi_category(aqi_val)

    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("US AQI Index", f"{aqi_val} {icon}", category)
    col2.metric("PM2.5 (Fine Particles)", f"{current['pm2_5']} µg/m³")
    col3.metric("PM10 (Coarse Dust)", f"{current['pm10']} µg/m³")
    col4.metric("Nitrogen Dioxide (NO₂)", f"{current['nitrogen_dioxide']} µg/m³")

    # Health Advisory Box
    st.info(f"💡 **Health Advisory:** {advice}")

    # Hourly Trend Chart
    st.markdown("### 📈 24-Hour Pollutant Trend")
    hourly_df = pd.DataFrame({
        "Time": pd.to_datetime(data["hourly"]["time"]),
        "PM2.5 (µg/m³)": data["hourly"]["pm2_5"],
        "PM10 (µg/m³)": data["hourly"]["pm10"]
    }).set_index("Time")

    st.line_chart(hourly_df, use_container_width=True)

# ================= TAB 2: MULTI-CITY COMPARISON =================
with tab2:
    st.subheader("City-by-City Air Quality Comparison")
    
    if not compare_cities:
        st.warning("Please select at least one city from the sidebar to compare.")
    else:
        comp_list = []
        for city in compare_cities:
            c_lat, c_lon = CITIES[city]
            c_data = fetch_air_quality(c_lat, c_lon)["current"]
            cat, _, _ = get_aqi_category(c_data["us_aqi"])
            comp_list.append({
                "City": city,
                "lat": c_lat,
                "lon": c_lon,
                "AQI": c_data["us_aqi"],
                "Status": cat,
                "PM2.5": c_data["pm2_5"],
                "PM10": c_data["pm10"],
                "CO": c_data["carbon_monoxide"],
                "SO₂": c_data["sulphur_dioxide"]
            })
        
        comp_df = pd.DataFrame(comp_list)
        
        # Side-by-side layout for chart and table
        col_left, col_right = st.columns([1.2, 1])
        
        with col_left:
            st.markdown("#### AQI Levels Bar Chart")
            st.bar_chart(comp_df.set_index("City")["AQI"], use_container_width=True)
            
        with col_right:
            st.markdown("#### Detailed Data Table")
            st.dataframe(comp_df.drop(columns=["lat", "lon"]), use_container_width=True)

        # Geographic Map View
        st.markdown("#### 🗺️ Geographic Distribution")
        st.map(comp_df[["lat", "lon"]], zoom=4, use_container_width=True)
