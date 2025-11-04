# app.py — ClimateScope Dashboard Analysis (Final Restored Version)
# Author: Thesika S N
# Run using: streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

# ----------------------------------
# 🌦️ Streamlit Page Config
# ----------------------------------
st.set_page_config(page_title="ClimateScope Dashboard Analysis 🌎",
                   page_icon="🌍", layout="wide")

# ----------------------------------
# 🎨 Custom CSS (Gradient Fix + Professional Look)
# ----------------------------------
st.markdown("""
<style>
body {
  background: linear-gradient(120deg, #E3F2FD, #E8EAF6, #E0F7FA);
}
h1, h2, h3 {
  color: #0D47A1;
  font-family: 'Segoe UI Semibold', sans-serif;
}
.section {
  background-color: rgba(255,255,255,0.96);
  padding: 22px;
  border-radius: 14px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
  margin-bottom: 28px;
}
.plot-desc {
  color: #4A148C;
  font-weight: 600;
  font-size: 15.5px;
  background: linear-gradient(90deg, #F3E5F5, #E1F5FE);
  padding: 10px 15px;
  border-left: 6px solid #7E57C2;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.stTabs [role="tablist"] {
  background: linear-gradient(90deg, #1565C0, #512DA8, #8E24AA);
  border-radius: 12px;
  padding: 10px;
}
.stTabs [role="tab"] {
  color: white;
  font-weight: 600;
  padding: 10px 25px;
  border-radius: 8px;
}
.stTabs [role="tab"][aria-selected="true"] {
  background-color: rgba(255,255,255,0.3);
  text-shadow: 0px 0px 8px #FFF;
}
thead th {
  font-weight: bold !important;
  color: #0D47A1 !important;
  background-color: #E3F2FD !important;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# 🏷️ Title
# ----------------------------------
st.title("🌦️ ClimateScope Dashboard Analysis")
st.markdown("""
An intelligent multi-page interactive weather dashboard visualizing global weather trends, 
air quality, correlations, and extreme events — built with rich analytics and vibrant design.
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
if selected_countries:
    mask &= df[col_country].isin(selected_countries)
df_f = df[mask].copy()

# ----------------------------------
# 🧭 Tabs Navigation
# ----------------------------------
tabs = st.tabs([
    "🏠 Overview",
    "📊 Statistical Analysis",
    "🌡️ Trends & Seasonality",
    "🌍 Regional Map",
    "📈 Correlation Insights",
    "☁️ Air Quality Index",
    "⚠️ Extreme Events",
    "📋 Summary"
])

# ----------------------------------
# 🏠 Overview
# ----------------------------------
with tabs[0]:
    st.header("🏠 Global Weather Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Records", f"{len(df_f):,}")
    c2.metric("Avg Temp (°C)", f"{df_f[col_temp].mean():.2f}" if col_temp else "N/A")
    c3.metric("Avg Humidity (%)", f"{df_f[col_hum].mean():.2f}" if col_hum else "N/A")
    c4.metric("Avg Wind (kph)", f"{df_f[col_wind].mean():.2f}" if col_wind else "N/A")

    st.subheader("📆 Data Records Over Time")
    fig_timeline = px.histogram(df_f, x="last_updated", nbins=50, color_discrete_sequence=["#8E24AA"], template="plotly_white")
    st.plotly_chart(fig_timeline, use_container_width=True)
    st.markdown('<div class="plot-desc">📅 **Description:** Number of weather data records collected over time for the selected regions.</div>', unsafe_allow_html=True)

# ----------------------------------
# 📊 Statistical Analysis
# ----------------------------------
with tabs[1]:
    st.header("📊 Statistical Analysis")
    st.subheader("🌡️ Temperature Distribution")
    if col_temp:
        fig_temp = px.histogram(df_f, x=col_temp, nbins=70, color=col_country,
                                color_discrete_sequence=px.colors.sequential.Sunset, template="plotly_white")
        st.plotly_chart(fig_temp, use_container_width=True)
        st.markdown('<div class="plot-desc">Temperature spread across countries reveals frequent and extreme ranges.</div>', unsafe_allow_html=True)

    st.subheader("📉 Correlation Matrix of Numeric Variables")
    numeric = df_f.select_dtypes(include=[np.number]).columns
    if len(numeric) > 1:
        corr = df_f[numeric].corr()
        fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale="RdYlBu", zmin=-1, zmax=1, template="plotly_white")
        st.plotly_chart(fig_corr, use_container_width=True)
        st.markdown('<div class="plot-desc">Correlation matrix highlights interrelations — warm tones = positive correlation, cool = negative.</div>', unsafe_allow_html=True)

# ----------------------------------
# 🌡️ Trends & Seasonality
# ----------------------------------
with tabs[2]:
    st.header("🌡️ Temperature Trends & Seasonality")
    df_f["month"] = df_f["last_updated"].dt.month
    st.subheader("📈 Temperature Trend Over Time")
    fig_line = px.line(df_f, x="last_updated", y=col_temp, color=col_country,
                       color_discrete_sequence=px.colors.sequential.Plasma, template="plotly_white")
    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown('<div class="plot-desc">Shows how temperature evolves over time, identifying warming or cooling phases.</div>', unsafe_allow_html=True)

    st.subheader("📅 Monthly Temperature Variation")
    fig_box = px.box(df_f, x="month", y=col_temp, color=col_country,
                     color_discrete_sequence=px.colors.sequential.Viridis, template="plotly_white")
    st.plotly_chart(fig_box, use_container_width=True)
    st.markdown('<div class="plot-desc">Boxplot reveals monthly variation and outliers, useful for seasonal pattern analysis.</div>', unsafe_allow_html=True)

# ----------------------------------
# 🌍 Regional Map
# ----------------------------------
with tabs[3]:
    st.header("🌍 Regional Temperature Comparison")
    df_avg = df_f.groupby(col_country)[col_temp].mean().reset_index()
    fig_map = px.choropleth(df_avg, locations=col_country, locationmode="country names",
                            color=col_temp, color_continuous_scale="Turbo",
                            template="plotly_white", title="Average Temperature by Country")
    fig_map.update_layout(height=550)
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown('<div class="plot-desc">Choropleth highlights geographical temperature distribution — warmer tones indicate hotter climates.</div>', unsafe_allow_html=True)

# ----------------------------------
# 📈 Correlation Insights
# ----------------------------------
with tabs[4]:
    st.header("📈 Dual-Axis Correlation Insights")
    options = [col_temp, col_hum, col_wind, col_precip, col_pressure]
    param1 = st.selectbox("Primary variable (Y1)", options)
    param2 = st.selectbox("Secondary variable (Y2)", [p for p in options if p != param1])
    df_rel = df_f.dropna(subset=[param1, param2])
    fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
    fig_dual.add_trace(go.Scatter(x=df_rel["last_updated"], y=df_rel[param1], name=param1,
                                  line=dict(color="#1976D2", width=3)), secondary_y=False)
    fig_dual.add_trace(go.Scatter(x=df_rel["last_updated"], y=df_rel[param2], name=param2,
                                  line=dict(color="#E64A19", width=3, dash="dot")), secondary_y=True)
    fig_dual.update_layout(title=f"{param1} vs {param2} — Dual-Axis Time Series",
                           template="plotly_white", height=600)
    st.plotly_chart(fig_dual, use_container_width=True)
    st.markdown(f'<div class="plot-desc">Compares {param1} and {param2} trends using a dual-axis view to spot dependencies.</div>', unsafe_allow_html=True)

# ----------------------------------
# ☁️ Air Quality Index
# ----------------------------------
with tabs[5]:
    st.header("☁️ Air Quality Index (AQI) by Country")
    if col_aqi and col_country:
        df_aqi = df_f.dropna(subset=[col_aqi, col_country])
        df_country_aqi = df_aqi.groupby(col_country)[col_aqi].mean().reset_index()

        # AQI Table Above Chart
        st.subheader("📋 AQI Classification Table")
        aqi_table = pd.DataFrame({
            "AQI Range": ["0–50", "51–100", "101–150", "151–200", "201–300", "301–500"],
            "Category": ["Good", "Moderate", "Unhealthy (Sensitive)", "Unhealthy", "Very Unhealthy", "Hazardous"],
            "Color Code": ["🟩 Green", "🟨 Yellow", "🟧 Orange", "🟥 Red", "🟪 Purple", "⬛ Maroon"]
        })
        st.dataframe(aqi_table, use_container_width=True)

        # Pie Chart (aligned colors)
        aqi_colors = ["#00E400", "#FFFF00", "#FF7E00", "#FF0000", "#8F3F97", "#7E0023"]
        fig_pie = px.pie(df_country_aqi, names=col_country, values=col_aqi,
                         color_discrete_sequence=aqi_colors,
                         hole=0.35, title="Average AQI Distribution by Country")
        fig_pie.update_layout(height=550, width=650)
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("""
        <div class="plot-desc">
        ☁️ **Air Quality Insight:** AQI table defines official ranges. The pie chart uses the same color coding, highlighting pollution variations across regions.
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------
# ⚠️ Extreme Events (Fixed Headings)
# ----------------------------------
with tabs[6]:
    st.header("⚠️ Extreme Weather Events")
    hot = df_f.nlargest(10, col_temp)
    cold = df_f.nsmallest(10, col_temp)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔥 Hottest Days")
        st.dataframe(hot[[col_country, "last_updated", col_temp, col_condition]]
                     .style.set_table_styles([{'selector': 'th', 'props': [('font-weight', 'bold')]}]))

    with col2:
        st.subheader("❄️ Coldest Days")
        st.dataframe(cold[[col_country, "last_updated", col_temp, col_condition]]
                     .style.set_table_styles([{'selector': 'th', 'props': [('font-weight', 'bold')]}]))

    st.subheader("🌬️ Wind Speed Distribution")
    fig_wind = px.histogram(df_f, x=col_wind, nbins=50, color_discrete_sequence=px.colors.sequential.Viridis, template="plotly_white")
    st.plotly_chart(fig_wind, use_container_width=True)
    st.markdown('<div class="plot-desc">Shows the frequency of different wind speeds. High peaks indicate storm-prone or gusty climates.</div>', unsafe_allow_html=True)

# ----------------------------------
# 📋 Summary
# ----------------------------------
with tabs[7]:
    st.header("📋 Summary & Insights")
    st.dataframe(df_f.describe().style.format("{:.2f}"))
    st.download_button("📥 Download Filtered Data", df_f.to_csv(index=False).encode("utf-8"),
                       "filtered_weather_data.csv", "text/csv")
    st.markdown("""
    <div class="plot-desc">
    🌎 <b>Summary Highlights:</b><br>
    • Strong <b>seasonal temperature cycles</b> detected.<br>
    • <b>Humidity-temperature inverse</b> relationship visible.<br>
    • <b>Air Quality disparities</b> evident across countries.<br>
    • <b>Extreme events</b> identified for climate anomaly study.<br>
    • <b>Dual-axis correlation</b> reveals deep variable connections.<br>
    </div>
    """, unsafe_allow_html=True)
