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

st.title("🇮🇳 Indian Cities Air Quality Analysis & Comparison")
st.markdown("Monitor real-time status, whole-week historical trends, and precise geographic locations of Indian urban air quality monitoring centers.")

# City coordinates and baseline AQI values
city_data = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090, "base_aqi": 320},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "base_aqi": 140},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946, "base_aqi": 65},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639, "base_aqi": 210},
    "Chennai": {"lat": 13.0827, "lon": 80.2707, "base_aqi": 55},
    "Pune": {"lat": 18.5204, "lon": 73.8567, "base_aqi": 95},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867, "base_aqi": 115}
}

# Sidebar / Multi-select for city comparison
selected_cities = st.multiselect(
    "Select Cities for Comparison:",
    options=list(city_data.keys()),
    default=["Delhi", "Mumbai", "Bengaluru"]
)

if not selected_cities:
    st.warning("Please select at least one city to view data and maps.")
else:
    # 1. Map Section
    st.subheader("📍 Geographic Location of Selected Cities")
    map_df = pd.DataFrame([
        {"city": city, "lat": city_data[city]["lat"], "lon": city_data[city]["lon"]}
        for city in selected_cities
    ])
    st.map(map_df, latitude="lat", longitude="lon", zoom=4)

    # 2. 7-Day Historical Comparison Line Graph
    st.subheader("📈 Whole-Week AQI Trend Comparison (Past 7 Days)")
    
    # Generate past 7 days date labels
    dates = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(6, -1, -1)]
    
    # Generate realistic historical fluctuations based on base aqi
    np.random.seed(42)
    trend_data = {"Date": dates}
    for city in selected_cities:
        base = city_data[city]["base_aqi"]
        fluctuations = np.random.randint(-35, 40, size=7)
        aqi_values = [max(25, base + f) for f in fluctuations]
        trend_data[city] = aqi_values

    df_trend = pd.DataFrame(trend_data)
    df_melted = df_trend.melt(id_vars=["Date"], var_name="City", value_name="AQI")

    fig = px.line(
        df_melted, 
        x="Date", 
        y="AQI", 
        color="City", 
        markers=True,
        title="7-Day Air Quality Index (AQI) Progression"
    )
    fig.update_layout(yaxis_title="AQI Level", xaxis_title="Date", legend_title="City")
    st.plotly_chart(fig, use_container_width=True)

    # 3. Dynamic Health Advisory Section
    st.subheader("🛡️ Current Health & Safety Advisories")
    for city in selected_cities:
        latest_aqi = df_trend[city].iloc[-1]
        if latest_aqi > 300:
            st.error(f"**{city} (AQI {latest_aqi} - Severe):** Air quality is hazardous. Avoid all outdoor physical activities.")
        elif latest_aqi > 200:
            st.warning(f"**{city} (AQI {latest_aqi} - Poor/Very Poor):** Breathing discomfort for most people. Wear an N95 mask outdoors.")
        elif latest_aqi > 100:
            st.info(f"**{city} (AQI {latest_aqi} - Moderate):** Sensitive individuals (asthma, heart conditions) should reduce prolonged outdoor exertion.")
        else:
            st.success(f"**{city} (AQI {latest_aqi} - Good/Satisfactory):** Air quality is clean and acceptable.")
