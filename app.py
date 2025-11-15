# app.py — ClimateScope Dashboard Analysis (Final Warning-Free & Complete Version)
# Author: Thesika S N
# Run using: streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import os
import pycountry

# ----------------------------------
# 🌦️ Page Configuration
# ----------------------------------
st.set_page_config(page_title="ClimateScope Dashboard Analysis 🌎",
                   page_icon="🌍", layout="wide")

# ----------------------------------
# 📘 Guidelines Page
# ----------------------------------
if "show_guidelines" not in st.session_state:
    st.session_state.show_guidelines = True

if st.session_state.show_guidelines:
    st.title("📘 Welcome to ClimateScope Dashboard 🌦️")
    st.markdown("""
    ### 🔍 About This Application
    ClimateScope Dashboard is an **interactive AI-powered climate analytics tool** that helps you visualize
    and understand global weather and environmental parameters.

    This dashboard provides **real-time insights** into:
    - 🌡️ Temperature variation across countries  
    - 💧 Humidity and precipitation trends  
    - ☁️ Air quality index (AQI) & pollution impact  
    - ⚙️ Atmospheric pressure and UV index levels  
    - 🌪️ Extreme events (hottest & coldest days)  
    - 🔥 Heat index showing perceived temperature  

    ---

    ### 🧭 How to Use
    1. **Use the sidebar filters** to select:
       - Date range  
       - Countries/Regions  
       - Visualization mode (Global or Local Map)
    2. **Explore the tabs** to view detailed analyses:
       - **Overview:** Quick climate metrics summary  
       - **Map Visualization:** Temperature maps & geospatial data  
       - **Air Quality Index:** Pollution health indicators  
       - **Extreme Events:** Top hottest & coldest events  
       - **Climate Parameter Analysis:** Deep dives into temperature, UV, humidity & pressure  
       - **Summary:** Data statistics and export options  

    ---

    ### 💡 Insights You’ll Gain
    - Identify climate change patterns globally  
    - Compare atmospheric stability and rainfall trends  
    - Understand human-perceived heat and air quality  
    - Discover how different regions behave under extreme conditions  
    """, unsafe_allow_html=True)

    if st.button("🚀 Launch Dashboard"):
        st.session_state.show_guidelines = False
        st.rerun()

    st.stop()

# ----------------------------------
# 🎨 Custom CSS — Gradient Boxes
# ----------------------------------
st.markdown("""
<style>
body {
  background: linear-gradient(120deg, #E3F2FD, #E0F7FA, #E8EAF6);
  font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3 {
  color: #0D47A1;
  font-family: 'Segoe UI Semibold', sans-serif;
}
.feature-box {
  background: linear-gradient(90deg, #3949AB, #8E24AA);
  color: white;
  padding: 10px 15px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 18px;
  letter-spacing: 0.5px;
  margin-top: 20px;
  margin-bottom: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}
.plot-desc {
  color: #1A237E;
  font-weight: 600;
  font-size: 15px;
  background: linear-gradient(90deg, #E1F5FE, #E8EAF6);
  padding: 10px 15px;
  border-left: 6px solid #283593;
  border-radius: 10px;
  margin-top: 10px;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}
th, td {
  border: 1px solid #999;
  text-align: center;
  padding: 8px;
  font-weight: 500;
}
th {
  background-color: #1A237E;
  color: white;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# 🏷️ Title
# ----------------------------------
st.title("🌦️ ClimateScope Dashboard Analysis")
st.markdown("""
An interactive, multi-dimensional climate analytics platform visualizing global temperature, humidity, 
air quality, and extreme weather patterns with professional data storytelling.
""")

# ----------------------------------
# 📂 Load Data
# ----------------------------------
@st.cache_data
def load_data():
    for f in ["processed/cleaned_weather.csv", "cleaned_weather.csv", "data/cleaned_weather.csv"]:
        if os.path.exists(f):
            return pd.read_csv(f)
    return None

df = load_data()
if df is None:
    uploaded = st.file_uploader("Upload cleaned_weather.csv", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
    else:
        st.stop()

# ----------------------------------
# 🧩 Data Preparation
# ----------------------------------
# Keep original parsing attempts, but handle safely
if "last_updated" in df.columns:
    df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
elif "date" in df.columns:
    df["last_updated"] = pd.to_datetime(df["date"], errors="coerce")
else:
    df["last_updated"] = pd.to_datetime(datetime.now())

def find_col(df, keywords):
    for key in keywords:
        for c in df.columns:
            if key.lower() in c.lower():
                return c
    return None

col_temp = find_col(df, ["temperature", "temp"])
col_hum = find_col(df, ["humidity"])
col_wind = find_col(df, ["wind"])
col_precip = find_col(df, ["precip"])
col_pressure = find_col(df, ["pressure"])
col_country = find_col(df, ["country"])
col_condition = find_col(df, ["condition"])
col_aqi = find_col(df, ["air_quality", "aqi", "pm2.5", "us-epa"])
col_uv = find_col(df, ["uv", "uv_index"])
col_cloud = find_col(df, ["cloud", "cloudcover"])

# ----------------------------------
# 🎛️ Sidebar Filters
# ----------------------------------
st.sidebar.header("🌍 Filters")
countries = sorted(df[col_country].dropna().unique()) if col_country else []
selected_countries = st.sidebar.multiselect("Select Countries", countries, default=countries[:5] if countries else [])
min_date = df["last_updated"].min().date()
max_date = df["last_updated"].max().date()
start_date, end_date = st.sidebar.slider("Date Range", min_value=min_date, max_value=max_date,
                                         value=(min_date, max_date))
start_ts, end_ts = pd.to_datetime(start_date), pd.to_datetime(end_date) + pd.Timedelta(days=1)
mask = (df["last_updated"] >= start_ts) & (df["last_updated"] <= end_ts)
if selected_countries and col_country:
    mask &= df[col_country].isin(selected_countries)
df_f = df[mask].copy()

# =========================
# Fix pyarrow / streamlit serialization:
# - Streamlit's dataframe serialization to Arrow sometimes fails with datetime objects.
# - Keep a string version of 'last_updated' for display (df_f_str) and a datetime column for plotting (df_plot).
# =========================
df_f = df_f.reset_index(drop=True)
df_plot = df_f.copy()
# ensure datetime for plotting
df_plot["last_updated_dt"] = pd.to_datetime(df_plot["last_updated"], errors="coerce")
# string version for Streamlit dataframes / download
df_f["last_updated"] = df_f["last_updated"].dt.strftime("%Y-%m-%d %H:%M:%S")

map_type = st.sidebar.radio("Map Type", ["🌎 Global Temperature View", "🌡 Localized Bubble Map"])

# ----------------------------------
# 🧭 Tabs Navigation
# ----------------------------------
tabs = st.tabs([
    "🏠 Overview",
    "🌍 Map Visualization",
    "☁️ Air Quality Index",
    "⚠️ Extreme Events",
    "🌡️ Climate Parameter Analysis",
    "📋 Summary"
])

# ----------------------------------
# 🏠 Overview
# ----------------------------------
with tabs[0]:
    st.markdown("<div class='feature-box'>🏠 Global Weather Overview</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Records", f"{len(df_f):,}")
    c2.metric("Avg Temp (°C)", f"{df_plot[col_temp].mean():.2f}" if col_temp else "N/A")
    c3.metric("Avg Humidity (%)", f"{df_plot[col_hum].mean():.2f}" if col_hum else "N/A")
    c4.metric("Avg Wind (kph)", f"{df_plot[col_wind].mean():.2f}" if col_wind else "N/A")

    st.markdown("<h3>📆 Data Collected Over Time</h3>", unsafe_allow_html=True)
    if "last_updated_dt" in df_plot.columns:
        fig_timeline = px.histogram(df_plot.dropna(subset=["last_updated_dt"]), x="last_updated_dt", nbins=50,
                                    color_discrete_sequence=["#283593"], template="plotly_white")
    else:
        fig_timeline = px.histogram(df_plot, x="last_updated", nbins=50,
                                    color_discrete_sequence=["#283593"], template="plotly_white")
    st.plotly_chart(fig_timeline, use_container_width=True)
    st.markdown("""
    <div class="plot-desc">
    This plot shows how the dataset has grown across time for selected regions.  
    Higher bars indicate days with more recorded observations.
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------
# 🌍 Map Visualization
# ----------------------------------

with tabs[1]:
    st.markdown("<div class='feature-box'>🌍 Global Weather Map</div>", unsafe_allow_html=True)

    # Convert country names to ISO-3 codes safely (for robust choropleth)
    def to_iso3(name):
        try:
            return pycountry.countries.lookup(name).alpha_3
        except Exception:
            return None

    if col_country in df_f.columns:
        df_plot["iso_code"] = df_plot[col_country].apply(lambda x: to_iso3(x) if pd.notna(x) else None)

    if map_type == "🌡 Localized Bubble Map" and "latitude" in df_plot.columns and "longitude" in df_plot.columns and col_temp in df_plot.columns:
        df_map = df_plot.dropna(subset=["latitude", "longitude", col_temp])
        if not df_map.empty:
            df_map["size_norm"] = (df_map[col_temp] - df_map[col_temp].min()) + 1
            # ✅ New API: scatter_map replaces scatter_mapbox
            fig_map = px.scatter_map(
                df_map,
                lat="latitude",
                lon="longitude",
                color=col_temp,
                size="size_norm",
                color_continuous_scale="Inferno",
                hover_name=col_country,
                zoom=1
            )
            fig_map.update_layout(map=dict(style="carto-darkmatter"), margin={"r":0, "t":0, "l":0, "b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No geolocation data available for the selected filters to render the localized bubble map.")
    else:
        # For choropleth use ISO3 codes to avoid future location-name deprecation issues
        if "iso_code" in df_plot.columns and col_temp in df_plot.columns:
            df_avg = df_plot.dropna(subset=["iso_code", col_temp]).groupby(["iso_code", col_country], as_index=False)[col_temp].mean()
            if not df_avg.empty:
                fig_choro = px.choropleth(
                    df_avg, locations="iso_code", color=col_temp, hover_name=col_country,
                    color_continuous_scale="Inferno"
                )
                fig_choro.update_layout(geo_showframe=False, geo_showcoastlines=True, geo_projection_type="natural earth")
                st.plotly_chart(fig_choro, use_container_width=True)
            else:
                st.info("No country-level temperature data available for the selected filters to render the choropleth.")
        else:
            st.info("Country / temperature columns not available for choropleth. Ensure your dataset has country and temperature columns.")

    st.markdown("""
    <div class="plot-desc">
    The global map provides temperature intensity visualization using choropleth or localized bubbles.  
    Each country is now highlighted and labeled properly for better interpretation.
    </div>
    """, unsafe_allow_html=True)


# ----------------------------------
# ☁️ Air Quality Index
# ----------------------------------
with tabs[2]:
    st.markdown("<div class='feature-box'>☁️ Air Quality Index (AQI) by Country</div>", unsafe_allow_html=True)
    st.markdown("<h3>📊 AQI Range and Health Categories</h3>", unsafe_allow_html=True)
    st.markdown("""
    <table>
        <tr><th>AQI Range</th><th>Category</th><th>Color</th></tr>
        <tr><td>0 - 50</td><td>Good</td><td style='background-color:#00E400;'></td></tr>
        <tr><td>51 - 100</td><td>Moderate</td><td style='background-color:#FFFF00;'></td></tr>
        <tr><td>101 - 150</td><td>Unhealthy for Sensitive Groups</td><td style='background-color:#FF7E00;'></td></tr>
        <tr><td>151 - 200</td><td>Unhealthy</td><td style='background-color:#FF0000;'></td></tr>
        <tr><td>201 - 300</td><td>Very Unhealthy</td><td style='background-color:#8F3F97;'></td></tr>
        <tr><td>301 - 500</td><td>Hazardous</td><td style='background-color:#7E0023;'></td></tr>
    </table>
    """, unsafe_allow_html=True)

    if col_aqi and col_country:
        df_aqi = df_plot.dropna(subset=[col_aqi, col_country])
        if not df_aqi.empty:
            df_country_aqi = df_aqi.groupby(col_country, as_index=False)[col_aqi].mean()
            st.markdown("<h3>🌍 Average AQI by Country</h3>", unsafe_allow_html=True)
            fig_pie = px.pie(df_country_aqi, names=col_country, values=col_aqi,
                             color_discrete_sequence=["#00E400", "#FFFF00", "#FF7E00", "#FF0000", "#8F3F97", "#7E0023"],
                             hole=0.35)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("""
            <div class="plot-desc">
            The pie chart shows the distribution of AQI across countries, indicating air pollution intensity and its category.  
            It visually identifies regions with the cleanest and most polluted air.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("AQI and/or country data not available for the selected filters.")
    else:
        st.info("AQI and/or country columns not detected in the dataset.")

# ----------------------------------
# ⚠️ Extreme Events
# ----------------------------------
with tabs[3]:
    st.markdown("<div class='feature-box'>⚠️ Extreme Weather Events</div>", unsafe_allow_html=True)
    st.markdown("<h3>🔥 Hottest & ❄️ Coldest Days</h3>", unsafe_allow_html=True)
    if col_temp:
        hot = df_plot.nlargest(10, col_temp)
        cold = df_plot.nsmallest(10, col_temp)
        if not hot.empty:
            st.dataframe(hot[[col_country, "last_updated", col_temp, col_condition]].style.format({col_temp: "{:.2f}"}))
        if not cold.empty:
            st.dataframe(cold[[col_country, "last_updated", col_temp, col_condition]].style.format({col_temp: "{:.2f}"}))
    else:
        st.info("Temperature column not detected for extreme event tables.")

    st.markdown("<h3>🌪️ Temperature Extremes Distribution</h3>", unsafe_allow_html=True)
    if col_temp:
        fig_extreme = px.histogram(df_plot.dropna(subset=[col_temp]), x=col_temp, nbins=50, color=col_country if col_country else None,
                                   color_discrete_sequence=px.colors.sequential.Reds)
        st.plotly_chart(fig_extreme, use_container_width=True)
        st.markdown("""
        <div class="plot-desc">
        This histogram displays how temperature extremes vary across selected countries.  
        It helps identify frequency patterns of extreme heat and cold conditions.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Temperature column not available for extremes histogram.")

# ----------------------------------
# 🌡️ Climate Parameter Analysis
# ----------------------------------
with tabs[4]:
    st.markdown("<div class='feature-box'>🌡️ Climate Parameter Analysis</div>", unsafe_allow_html=True)

    # 🌧️ Precipitation
    if col_precip:
        st.markdown("<h3>🌧️ Precipitation Analysis</h3>", unsafe_allow_html=True)
        fig_precip = px.box(df_plot.dropna(subset=[col_precip, col_country]) if col_country else df_plot.dropna(subset=[col_precip]),
                            x=col_country if col_country else None, y=col_precip, color=col_country if col_country else None)
        st.plotly_chart(fig_precip, use_container_width=True)
        st.markdown('<div class="plot-desc">Shows rainfall variation across countries and identifies high precipitation regions.</div>', unsafe_allow_html=True)
    else:
        st.info("Precipitation column not found in dataset.")

    # 💧 Humidity
    if col_hum:
        st.markdown("<h3>💧 Humidity Analysis</h3>", unsafe_allow_html=True)
        fig_hum = px.histogram(df_plot.dropna(subset=[col_hum]), x=col_hum, nbins=40, color=col_country if col_country else None)
        st.plotly_chart(fig_hum, use_container_width=True)
        st.markdown('<div class="plot-desc">Shows humidity distribution and its effect on air moisture balance.</div>', unsafe_allow_html=True)
    else:
        st.info("Humidity column not found.")

    # 🌡️ Temperature Range
    if col_temp:
        st.markdown("<h3>🌡️ Temperature Range Analysis</h3>", unsafe_allow_html=True)
        fig_temp_range = px.box(df_plot.dropna(subset=[col_temp]), x=col_country if col_country else None, y=col_temp, color=col_country if col_country else None)
        st.plotly_chart(fig_temp_range, use_container_width=True)
        st.markdown('<div class="plot-desc">Box plot showing range, median, and outliers of temperature by country.</div>', unsafe_allow_html=True)
    else:
        st.info("Temperature column not found.")

    # 💨 Wind Speed
    if col_wind:
        st.markdown("<h3>💨 Wind Speed Analysis</h3>", unsafe_allow_html=True)
        fig_wind = px.violin(df_plot.dropna(subset=[col_wind]), x=col_country if col_country else None, y=col_wind, color=col_country if col_country else None,
                             box=True, points="all", template="plotly_white")
        st.plotly_chart(fig_wind, use_container_width=True)
        st.markdown('<div class="plot-desc">Analyzes distribution of wind speeds across regions, highlighting variability and extremes.</div>', unsafe_allow_html=True)
    else:
        st.info("Wind column not present in dataset.")

    # ⚙️ Pressure
    if col_pressure:
        st.markdown("<h3>⚙️ Atmospheric Pressure Analysis</h3>", unsafe_allow_html=True)
        if "last_updated_dt" in df_plot.columns:
            fig_pressure = px.line(df_plot.dropna(subset=["last_updated_dt", col_pressure]), x="last_updated_dt", y=col_pressure, color=col_country if col_country else None)
        else:
            fig_pressure = px.line(df_plot.dropna(subset=[col_pressure]), x="last_updated", y=col_pressure, color=col_country if col_country else None)
        st.plotly_chart(fig_pressure, use_container_width=True)
        st.markdown('<div class="plot-desc">Line graph showing daily atmospheric pressure changes and stability trends.</div>', unsafe_allow_html=True)
    else:
        st.info("Pressure column not found.")

    # 🌞 UV
    if col_uv:
        st.markdown("<h3>🌞 UV Index Analysis</h3>", unsafe_allow_html=True)
        fig_uv = px.histogram(df_plot.dropna(subset=[col_uv]), x=col_uv, nbins=30, color=col_country if col_country else None)
        st.plotly_chart(fig_uv, use_container_width=True)
        st.markdown('<div class="plot-desc">Represents UV exposure intensity indicating potential skin risk levels.</div>', unsafe_allow_html=True)
    else:
        st.info("UV column not found.")

    # 🔥 Heat Map
    if col_temp and col_hum:
        st.markdown("<h3>🔥 Heat Map Analysis</h3>", unsafe_allow_html=True)
        df_plot["heat_index"] = df_plot[col_temp].astype(float) + 0.1 * df_plot[col_hum].astype(float)
        fig_heatmap = px.density_heatmap(df_plot.dropna(subset=[col_temp, col_hum, "heat_index"]), x=col_temp, y=col_hum, z="heat_index",
                                         color_continuous_scale="Inferno")
        st.plotly_chart(fig_heatmap, use_container_width=True)
        st.markdown('<div class="plot-desc">Shows the combined impact of temperature and humidity to visualize perceived heat intensity.</div>', unsafe_allow_html=True)
    else:
        st.info("Insufficient data for heat map (needs temperature and humidity).")

# ----------------------------------
# 📋 Summary
# ----------------------------------
with tabs[5]:
    st.markdown("<div class='feature-box'>📋 Summary & Insights</div>", unsafe_allow_html=True)
    # Use df_f (string-typed last_updated) for safe display/download
    try:
        st.dataframe(df_f.describe().style.format("{:.2f}"))
    except Exception:
        # fallback: show a trimmed summary if describe() has serialization trouble
        st.write(df_f.head(100))
    st.download_button("📥 Download Filtered Data", df_f.to_csv(index=False).encode("utf-8"),
                       "filtered_weather_data.csv", "text/csv")
    st.markdown("""
    <div class="plot-desc">
    Summary provides quick statistical measures — mean, min, max, std deviation for each parameter.  
    Download the processed data to perform further offline analysis.
    </div>
    """, unsafe_allow_html=True)
