import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Indian Cities Air Quality Dashboard",
    page_icon="🇮🇳",
    layout="wide"
)

st.title("🇮🇳 Indian Cities Air Quality Analysis & Monitoring System")
st.markdown("A Python-powered web application for tracking and analyzing urban air pollution across India.")

# Comprehensive city dataset with coordinates, base AQI, and specific pollutants
city_data = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090, "base_aqi": 320, "pm25": 280, "pm10": 350, "no2": 85, "co": 2.1, "status": "Severe"},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "base_aqi": 140, "pm25": 85, "pm10": 120, "no2": 55, "co": 1.2, "status": "Moderate"},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946, "base_aqi": 65, "pm25": 35, "pm10": 55, "no2": 25, "co": 0.6, "status": "Satisfactory"},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639, "base_aqi": 210, "pm25": 160, "pm10": 220, "no2": 65, "co": 1.5, "status": "Poor"},
    "Chennai": {"lat": 13.0827, "lon": 80.2707, "base_aqi": 55, "pm25": 28, "pm10": 45, "no2": 20, "co": 0.5, "status": "Good"},
    "Pune": {"lat": 18.5204, "lon": 73.8567, "base_aqi": 95, "pm25": 50, "pm10": 80, "no2": 35, "co": 0.8, "status": "Satisfactory"},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867, "base_aqi": 115, "pm25": 70, "pm10": 95, "no2": 45, "co": 1.0, "status": "Moderate"}
}

# Create Tabs for Clean Navigation
tab1, tab2 = st.tabs(["📊 Multi-City Comparison & Map", "🏙️ Single City Deep Dive"])

with tab1:
    st.subheader("Compare Cities Across India")
    selected_cities = st.multiselect(
        "Select cities to compare:",
        options=list(city_data.keys()),
        default=["Delhi", "Mumbai", "Bengaluru", "Kolkata"]
    )

    if not selected_cities:
        st.warning("Please select at least one city.")
    else:
        # Map centered precisely on India
        st.subheader("📍 Monitoring Stations Across India")
        map_df = pd.DataFrame([
            {"city": city, "lat": city_data[city]["lat"], "lon": city_data[city]["lon"]}
            for city in selected_cities
        ])
        # Centering map on India coordinates (lat: 20.5937, lon: 78.9629) with zoom 4
        st.map(map_df, latitude=20.5937, longitude=78.9629, zoom=4)

        # 7-Day Historical Comparison Line Graph
        st.subheader("📈 Whole-Week AQI Trend Comparison (Past 7 Days)")
        dates = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(6, -1, -1)]
        
        np.random.seed(42)
        trend_data = {"Date": dates}
        for city in selected_cities:
            base = city_data[city]["base_aqi"]
            fluctuations = np.random.randint(-30, 35, size=7)
            trend_data[city] = [max(25, base + f) for f in fluctuations]

        df_trend = pd.DataFrame(trend_data)
        df_melted = df_trend.melt(id_vars=["Date"], var_name="City", value_name="AQI")

        fig = px.line(
            df_melted, x="Date", y="AQI", color="City", markers=True,
            title="7-Day Air Quality Index Progression"
        )
        fig.update_layout(yaxis_title="AQI Level", xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Detailed City Analysis")
    chosen_city = st.selectbox("Select a specific city for detailed breakdown:", options=list(city_data.keys()))
    
    city_info = city_data[chosen_city]
    
    # Metric cards for the selected city
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current AQI", city_info["base_aqi"], city_info["status"])
    col2.metric("PM2.5 (µg/m³)", city_info["pm25"])
    col3.metric("NO₂ (µg/m³)", city_info["no2"])
    col4.metric("CO (mg/m³)", city_info["co"])

    # Bar chart of individual pollutants for this city
    pollutants_df = pd.DataFrame({
        "Pollutant": ["PM2.5", "PM10", "NO₂"],
        "Concentration": [city_info["pm25"], city_info["pm10"], city_info["no2"]]
    })
    
    fig_pollutant = px.bar(
        pollutants_df, x="Pollutant", y="Concentration", color="Pollutant",
        title=f"Major Pollutant Concentrations in {chosen_city}"
    )
    st.plotly_chart(fig_pollutant, use_container_width=True)

    # Health Advisory for single city
    st.subheader(f"🛡️ Health Recommendations for {chosen_city}")
    if city_info["base_aqi"] > 300:
        st.error(f"**Hazardous Conditions:** Air quality in {chosen_city} is severe. Everyone should avoid outdoor exertion and wear N95 masks.")
    elif city_info["base_aqi"] > 200:
        st.warning(f"**Poor Air Quality:** Sensitive groups (elderly, children, asthma patients) must stay indoors.")
    elif city_info["base_aqi"] > 100:
        st.info(f"**Moderate Air Quality:** Air is acceptable, but sensitive individuals should limit heavy outdoor exertion.")
    else:
        st.success(f"**Clean Air:** Air quality is good and safe for all outdoor activities.")
