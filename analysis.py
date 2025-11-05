import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from statsmodels.tsa.seasonal import seasonal_decompose

# Load cleaned data
df = pd.read_csv('Cleaned_GlobalWeatherRepository.csv', parse_dates=['last_updated'])
df.rename(columns={'last_updated': 'date'}, inplace=True)
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year
df['country'] = df['country'].apply(lambda x: x.encode('ascii', 'ignore').decode())

# Sidebar filters
st.sidebar.header("Filters")
selected_country = st.sidebar.selectbox("Select Country", df['country'].unique())
date_range = st.sidebar.date_input("Select Date Range", [df['date'].min(), df['date'].max()])

# Validate date input
if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = df[
        (df['country'] == selected_country) &
        (df['date'] >= start_date) &
        (df['date'] <= end_date)
    ]
else:
    st.warning("Please select both start and end dates to proceed.")
    st.stop()

# Summary & correlation
summary = filtered_df[['temperature_celsius', 'humidity', 'precip_mm', 'wind_kph']].describe()
correlations = filtered_df[['temperature_celsius', 'humidity', 'precip_mm', 'wind_kph']].corr()

# Extreme events
extreme_temp = filtered_df[filtered_df['temperature_celsius'] > filtered_df['temperature_celsius'].quantile(0.99)]
extreme_precip = filtered_df[filtered_df['precip_mm'] > filtered_df['precip_mm'].quantile(0.99)]
extreme_wind = filtered_df[filtered_df['wind_kph'] > filtered_df['wind_kph'].quantile(0.99)]
extreme_events = pd.concat([extreme_temp, extreme_precip, extreme_wind]).drop_duplicates()

# Dashboard layout
st.title("Global Weather Dashboard")

# Tabs for layout
tab1, tab2, tab3 = st.tabs(["📊 Summary", "📈 Visualizations", "⚠️ Extreme Events"])

with tab1:
    st.subheader("Summary Statistics")
    st.write(summary)
    st.subheader("Correlation Matrix")
    st.write(correlations)

with tab3:
    st.subheader("Extreme Weather Events")
    st.write(extreme_events[['date', 'country', 'temperature_celsius', 'precip_mm', 'wind_kph']])

with tab2:
    st.subheader("Global Temperature Trend")
    daily_avg = filtered_df.groupby('date')['temperature_celsius'].mean()
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(daily_avg.index, daily_avg.values, color='tomato')
    ax1.set_title('Global Temperature Trend Over Time')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Temperature (°C)')
    ax1.grid(True)
    st.pyplot(fig1)
    plt.close(fig1)

    st.subheader("Temperature vs Humidity")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.scatter(filtered_df['temperature_celsius'], filtered_df['humidity'], alpha=0.5, c='royalblue')
    ax2.set_title('Temperature vs Humidity')
    ax2.set_xlabel('Temperature (°C)')
    ax2.set_ylabel('Humidity (%)')
    ax2.grid(True)
    st.pyplot(fig2)
    plt.close(fig2)

    st.subheader("Monthly Temperature Trends Across Years")
    monthly_trend = filtered_df.groupby(['year', 'month'])['temperature_celsius'].mean().unstack()
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    sns.heatmap(monthly_trend, cmap='YlOrRd', annot=True, fmt=".1f", ax=ax3)
    ax3.set_title('Monthly Temperature Trends Across Years')
    ax3.set_xlabel('Month')
    ax3.set_ylabel('Year')
    st.pyplot(fig3)
    plt.close(fig3)

    st.subheader("Average Monthly Temperature (Global)")
    monthly_avg_temp = filtered_df.groupby('month')['temperature_celsius'].mean()
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    ax4.plot(monthly_avg_temp.index, monthly_avg_temp.values, marker='o', color='teal')
    ax4.set_title('Average Monthly Temperature (Global)')
    ax4.set_xlabel('Month')
    ax4.set_ylabel('Temperature (°C)')
    ax4.grid(True)
    st.pyplot(fig4)
    plt.close(fig4)

    st.subheader("Monthly Temperature Heatmap by Country")
    monthly_avg = filtered_df.groupby(['country', 'month'])['temperature_celsius'].mean().unstack()
    fig5, ax5 = plt.subplots(figsize=(14, 8))
    sns.heatmap(monthly_avg, cmap='coolwarm', annot=False, ax=ax5)
    ax5.set_title('Monthly Temperature Heatmap by Country')
    ax5.set_xlabel('Month')
    ax5.set_ylabel('Country')
    st.pyplot(fig5)
    plt.close(fig5)

    # scatterplot
    st.subheader("Custom Scatterplot")
    numeric_cols = ['temperature_celsius', 'humidity', 'precip_mm', 'wind_kph']
    x_var = st.selectbox("X-axis Variable", numeric_cols, index=0)
    y_var = st.selectbox("Y-axis Variable", numeric_cols, index=1)
    fig6, ax6 = plt.subplots(figsize=(8, 5))
    ax6.scatter(filtered_df[x_var], filtered_df[y_var], alpha=0.6, c='darkgreen')
    ax6.set_xlabel(x_var)
    ax6.set_ylabel(y_var)
    ax6.set_title(f"{x_var} vs {y_var}")
    ax6.grid(True)
    st.pyplot(fig6)
    plt.close(fig6)

    # Histogram
    st.subheader("Histogram")
    hist_var = st.selectbox("Histogram Variable", numeric_cols)
    bins = st.slider("Number of Bins", min_value=10, max_value=100, value=30)
    fig7, ax7 = plt.subplots(figsize=(8, 5))
    sns.histplot(filtered_df[hist_var], bins=bins, kde=True, ax=ax7, color='orange')
    ax7.set_title(f"Distribution of {hist_var}")
    st.pyplot(fig7)
    plt.close(fig7)

    # Boxplot
    st.subheader("Boxplot of Weather Variables")
    fig8, ax8 = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=filtered_df[numeric_cols], ax=ax8)
    ax8.set_title("Boxplot of Weather Variables")
    st.pyplot(fig8)
    plt.close(fig8)


# Download buttons
st.header("Download Data")
st.download_button("Download Filtered Data", filtered_df.to_csv(index=False), "filtered_weather.csv", "text/csv")
st.download_button("Download Summary Stats", summary.to_csv(), "summary_stats.csv", "text/csv")