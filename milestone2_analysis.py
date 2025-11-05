# milestone2_analysis.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st

# -----------------------------
# 1. Load the cleaned dataset
# -----------------------------
data = pd.read_csv("Clean_GlobalWeatherRepository.csv")

# Convert 'last_updated' to datetime
data['last_updated'] = pd.to_datetime(data['last_updated'])

# -----------------------------
# 2. Statistical Analysis
# -----------------------------
st.title("Climate Analysis Dashboard")

st.header("1. Statistical Summary")
st.write(data.describe())

# Correlation heatmap
st.header("Correlation Matrix")
corr = data[['temperature_celsius','wind_kph','pressure_mb']].corr()
st.write(corr)
sns.heatmap(corr, annot=True, cmap='coolwarm')
st.pyplot()

# -----------------------------
# 3. Distributions
# -----------------------------
st.header("2. Distributions")

# Temperature distribution
fig, ax = plt.subplots()
sns.histplot(data['temperature_celsius'], bins=30, kde=True)
ax.set_title("Temperature Distribution")
st.pyplot(fig)

# Wind speed distribution
fig, ax = plt.subplots()
sns.histplot(data['wind_kph'], bins=30, kde=True, color='orange')
ax.set_title("Wind Speed Distribution")
st.pyplot(fig)

# -----------------------------
# 4. Extreme Weather Events
# -----------------------------
st.header("3. Extreme Weather Events")
extreme_temp = data[(data['temperature_celsius'] > 45) | (data['temperature_celsius'] < -20)]
extreme_wind = data[data['wind_kph'] > 100]

st.subheader("Extreme Temperature Events")
st.dataframe(extreme_temp)

st.subheader("Extreme Wind Events")
st.dataframe(extreme_wind)

# -----------------------------
# 5. Comparisons Across Regions
# -----------------------------
st.header("4. Regional Comparisons")

country_avg = data.groupby('country')[['temperature_celsius','wind_kph']].mean().sort_values(by='temperature_celsius', ascending=False)
st.write(country_avg)

# Bar chart for top 10 countries by avg temperature
fig, ax = plt.subplots(figsize=(10,5))
country_avg['temperature_celsius'].head(10).plot(kind='bar', ax=ax, color='green')
ax.set_ylabel("Average Temperature (°C)")
ax.set_title("Top 10 Countries by Average Temperature")
st.pyplot(fig)

# -----------------------------
# 6. Time Series Analysis
# -----------------------------
st.header("5. Time Series Trends")

daily_temp = data.set_index('last_updated')['temperature_celsius'].resample('D').mean()
fig, ax = plt.subplots(figsize=(10,5))
daily_temp.plot(ax=ax)
ax.set_title("Daily Average Temperature Over Time")
st.pyplot(fig)

# -----------------------------
# 7. Choropleth Map (Interactive)
# -----------------------------
st.header("6. Choropleth Map: Avg Temperature by Country")
fig = px.choropleth(country_avg.reset_index(),
                    locations='country',
                    locationmode='country names',
                    color='temperature_celsius',
                    color_continuous_scale='Oranges',
                    title="Average Temperature by Country")
st.plotly_chart(fig)

# -----------------------------
# 8. Scatter Plot: Temperature vs Wind
# -----------------------------
st.header("7. Temperature vs Wind Speed")
fig = px.scatter(data, x='temperature_celsius', y='wind_kph', color='country', hover_data=['location_name'])
st.plotly_chart(fig)

# -----------------------------
# 9. Dashboard Layout Notes
# -----------------------------
st.markdown("""
### Dashboard Layout Suggestion:
- Top-left: Line chart of daily average temperature  
- Top-right: Scatter plot of temperature vs wind speed  
- Bottom-left: Choropleth map of avg temperature by country  
- Bottom-right: Table of extreme weather events
""")