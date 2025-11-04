# ============================================
# 🌦️ ClimateScope - Milestone 2 (Enhanced)
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from io import StringIO

# --------------------------------------------
# Streamlit Page Setup
# --------------------------------------------
st.set_page_config(page_title="ClimateScope Milestone 2", layout="wide")
st.title("🌍 ClimateScope: Global Weather Trends & Patterns (Milestone 2)")

# --------------------------------------------
# Step 1: Load Dataset
# --------------------------------------------
st.header("📂 Load Cleaned Dataset")

dataset_path = r"C:\Users\nithi\Downloads\GlobalWeatherRepository_Cleaned.csv"
df = pd.read_csv(dataset_path)
st.success(f"✅ Dataset Loaded Successfully from: {dataset_path}")
st.write("**Shape:**", df.shape)
st.write("**Columns:**", df.columns.tolist())

# --------------------------------------------
# Step 2: Data Preparation
# --------------------------------------------
st.header("🧹 Data Preparation")

df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')
df['Year'] = df['last_updated'].dt.year
df['Month'] = df['last_updated'].dt.month
df['Day'] = df['last_updated'].dt.day

# Clean duplicates / missing values
df = df.drop_duplicates()
df = df.dropna(subset=['temperature_celsius', 'humidity', 'precip_mm'])

st.write("**Data Types:**")
st.dataframe(df.dtypes)

st.write("**Missing Values:**")
st.dataframe(df.isnull().sum())

# --------------------------------------------
# Step 3: Descriptive Statistics
# --------------------------------------------
st.header("📊 Descriptive Statistics")

col1, col2 = st.columns(2)
with col1:
    st.dataframe(df.describe())
with col2:
    st.subheader("Correlation Matrix (Key Climate Variables)")

    # Select only relevant columns if present in dataset
    key_features = [
        'temperature_celsius', 'feels_like_celsius', 'humidity', 'precip_mm',
        'pressure_mb', 'wind_kph', 'visibility_kph', 'uv_index'
    ]
    selected = [c for c in key_features if c in df.columns]

    if selected:
        corr = df[selected].corr()
        fig, ax = plt.subplots(figsize=(7,5))
        sns.heatmap(
            corr, annot=True, cmap='coolwarm', center=0, fmt=".2f",
            linewidths=0.5, cbar_kws={'shrink': 0.7}, ax=ax
        )
        ax.set_title("Correlation Among Core Climate Variables", fontsize=12, pad=10)
        st.pyplot(fig)
    else:
        st.warning("No standard weather variables found for correlation analysis.")

# --------------------------------------------
# Step 4: Data Distributions
# --------------------------------------------
st.header("📈 Variable Distributions")

col1, col2, col3 = st.columns(3)
with col1:
    fig, ax = plt.subplots()
    sns.histplot(df['temperature_celsius'], bins=30, kde=True, color='red', ax=ax)
    ax.set_title("Temperature Distribution (°C)")
    st.pyplot(fig)
with col2:
    fig, ax = plt.subplots()
    sns.histplot(df['humidity'], bins=30, kde=True, color='blue', ax=ax)
    ax.set_title("Humidity Distribution (%)")
    st.pyplot(fig)
with col3:
    fig, ax = plt.subplots()
    sns.histplot(df['precip_mm'], bins=30, kde=True, color='green', ax=ax)
    ax.set_title("Precipitation Distribution (mm)")
    st.pyplot(fig)

# --------------------------------------------
# Step 5: Seasonal Trends
# --------------------------------------------
st.header("🌦️ Seasonal Trends")

monthly_avg = df.groupby('Month')[['temperature_celsius', 'humidity', 'precip_mm']].mean().reset_index()

fig = px.line(
    monthly_avg, x='Month', y=['temperature_celsius', 'humidity', 'precip_mm'],
    markers=True, title="Average Monthly Trends — Temperature, Humidity & Rainfall"
)
st.plotly_chart(fig, use_container_width=True)

# Yearly trend (temperature over years)
yearly_trend = df.groupby('Year')[['temperature_celsius', 'humidity']].mean().reset_index()
fig = px.line(
    yearly_trend, x='Year', y='temperature_celsius',
    markers=True, color_discrete_sequence=['red'], title="Average Global Temperature by Year"
)
st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------
# Step 6: Regional Comparisons
# --------------------------------------------
st.header("🌍 Regional & Country Comparisons")

region_temp = df.groupby('country')[['temperature_celsius','humidity','precip_mm']].mean().sort_values(by='temperature_celsius', ascending=False).reset_index()

# Top / Bottom countries
col1, col2 = st.columns(2)
with col1:
    st.subheader("Top 10 Hottest Countries")
    fig = px.bar(region_temp.head(10), x='country', y='temperature_celsius', color='temperature_celsius', color_continuous_scale='RdYlBu_r')
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.subheader("Top 10 Coldest Countries")
    fig = px.bar(region_temp.tail(10), x='country', y='temperature_celsius', color='temperature_celsius', color_continuous_scale='RdYlBu')
    st.plotly_chart(fig, use_container_width=True)

# Country humidity vs temperature scatter
st.subheader("💧 Humidity vs Temperature by Country")
fig = px.scatter(region_temp, x='temperature_celsius', y='humidity', hover_name='country',
                 color='precip_mm', size='precip_mm', color_continuous_scale='Viridis',
                 title="Country-wise Temperature, Humidity & Rainfall Intensity")
st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------
# Step 7: Interactive World Maps
# --------------------------------------------
st.header("🗺️ Interactive Global Weather Maps")

map_choice = st.radio("Choose a variable to visualize:", ["temperature_celsius", "humidity", "precip_mm"])

fig = px.choropleth(
    region_temp,
    locations="country",
    locationmode="country names",
    color=map_choice,
    hover_name="country",
    color_continuous_scale='RdYlBu_r' if map_choice=="temperature_celsius" else 'Viridis',
    title=f"Average {map_choice.replace('_',' ').title()} by Country"
)
st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------
# Step 8: Extreme Events & Anomalies
# --------------------------------------------
st.header("⚠️ Extreme Weather Events")

temp_threshold = df['temperature_celsius'].quantile(0.95)
rain_threshold = df['precip_mm'].quantile(0.95)

extreme_temp = df[df['temperature_celsius'] > temp_threshold]
extreme_rain = df[df['precip_mm'] > rain_threshold]

st.write(f"🔥 Extreme Temperature Threshold (95th %ile): {temp_threshold:.2f} °C")
st.write(f"🌧️ Extreme Rainfall Threshold (95th %ile): {rain_threshold:.2f} mm")

# Trend over time for extremes
extreme_temp_trend = extreme_temp.groupby('Year')['temperature_celsius'].count().reset_index()
extreme_rain_trend = extreme_rain.groupby('Year')['precip_mm'].count().reset_index()

fig = px.line(extreme_temp_trend, x='Year', y='temperature_celsius', markers=True, color_discrete_sequence=['red'],
              title="🔥 Number of Extreme Temperature Events per Year")
st.plotly_chart(fig, use_container_width=True)

fig = px.line(extreme_rain_trend, x='Year', y='precip_mm', markers=True, color_discrete_sequence=['blue'],
              title="🌧️ Number of Extreme Rainfall Events per Year")
st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------
# Step 9: Correlation & Pairwise Relationships
# --------------------------------------------
st.header("🔗 Correlations and Relationships")

fig = sns.pairplot(df[['temperature_celsius','humidity','precip_mm']], diag_kind='kde')
st.pyplot(fig)

corr_value = df['temperature_celsius'].corr(df['humidity'])
st.metric("📈 Correlation (Temp vs Humidity)", f"{corr_value:.2f}")

# --------------------------------------------
# Step 10: Insights Summary
# --------------------------------------------
st.header("🧠 Insights Summary")

avg_temp = df['temperature_celsius'].mean()
avg_humidity = df['humidity'].mean()
avg_rain = df['precip_mm'].mean()

hottest = region_temp.iloc[0]
coldest = region_temp.iloc[-1]

col1, col2, col3 = st.columns(3)
col1.metric("🌡️ Global Avg Temperature", f"{avg_temp:.2f} °C")
col2.metric("💧 Global Avg Humidity", f"{avg_humidity:.2f} %")
col3.metric("🌧️ Global Avg Precipitation", f"{avg_rain:.2f} mm")

st.write(f"🔥 **Hottest Country:** {hottest['country']} ({hottest['temperature_celsius']:.2f} °C)")
st.write(f"❄️ **Coldest Country:** {coldest['country']} ({coldest['temperature_celsius']:.2f} °C)")
st.write(f"📉 **Temp vs Humidity Correlation:** {corr_value:.2f}")
st.write(f"🌦️ Extreme Temperature Events Detected:** {len(extreme_temp):,}")
st.write(f"🌧️ Extreme Rainfall Events Detected:** {len(extreme_rain):,}")

# --------------------------------------------
# Step 11: Export Summary
# --------------------------------------------
summary = {
    "Average Temperature (°C)": avg_temp,
    "Average Humidity (%)": avg_humidity,
    "Average Precipitation (mm)": avg_rain,
    "Hottest Country": hottest['country'],
    "Coldest Country": coldest['country'],
    "Temp-Humidity Correlation": corr_value,
    "Extreme Temp Events": len(extreme_temp),
    "Extreme Rain Events": len(extreme_rain)
}

summary_df = pd.DataFrame([summary])
csv = summary_df.to_csv(index=False)

st.download_button(
    label="⬇️ Download Analysis Summary",
    data=csv,
    file_name="milestone2_analysis_summary.csv",
    mime="text/csv"
)

st.success("🎯 Enhanced Milestone 2 Analysis Complete Successfully!")
