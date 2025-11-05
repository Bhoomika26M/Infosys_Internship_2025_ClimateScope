# This script performs comprehensive statistical analysis for the ClimateScope project.
# Results are computed and displayed in the Streamlit dashboard (app.py).
# No console output here to keep the terminal clean.

import pandas as pd
import numpy as np

# Load cleaned data
df = pd.read_csv("cleaned_weather_data.csv")
monthly_df = pd.read_csv("monthly_weather_data.csv")

# Precompute all analysis results (used in dashboard)
key_vars = ['temperature_celsius', 'humidity', 'precip_mm', 'wind_kph', 'pressure_mb', 'uv_index']
basic_stats = df[key_vars].describe()
distributions = {var: {'skewness': df[var].skew(), 'kurtosis': df[var].kurtosis()} for var in key_vars}
corr_matrix = df[key_vars].corr()
monthly_df['month_num'] = pd.to_datetime(monthly_df['month'].astype(str)).dt.month
seasonal_avg = monthly_df.groupby('month_num')[key_vars].mean()
trends = {}
for country in monthly_df['country'].unique()[:5]:
    country_data = monthly_df[monthly_df['country'] == country].sort_values('month_num')
    if len(country_data) > 1:
        slope = np.polyfit(country_data['month_num'], country_data['temperature_celsius'], 1)[0]
        trends[country] = slope
hot_threshold = df['temperature_celsius'].quantile(0.95)
hot_events = df[df['temperature_celsius'] >= hot_threshold]
precip_threshold = df['precip_mm'].quantile(0.95)
precip_events = df[df['precip_mm'] >= precip_threshold]
wind_threshold = df['wind_kph'].quantile(0.95)
wind_events = df[df['wind_kph'] >= wind_threshold]
regional_avg = df.groupby('country')[key_vars].mean()

# Analysis complete - all results integrated into dashboard
