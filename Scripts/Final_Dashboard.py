import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import analytics module
from Analyse import (
    load_data, descriptive_stats, country_aggregates, correlation_matrix,
    monthly_trends, detect_extreme_events, region_comparisons,
    forecast_weather, forecast_multiple_metrics, generate_3d_surface, generate_insights,
    perform_pca_analysis, perform_clustering, detect_anomalies, analyze_correlation_insights,generate_3d_chart
)

# Page Configuration
st.set_page_config(
    page_title="🌍 ClimateScope — Global Weather Insights",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        max-width: 100%;
    }

    h1 {
        color: #2d3748;
        font-size: 48px !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 2rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    h2 {
        color: #4a5568;
        font-size: 32px !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
    }

    h3 {
        color: #718096;
        font-size: 24px !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
        color: #f7fafc;
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #f7fafc;
    }

    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stDateInput label {
        color: #f7fafc !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #667eea !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #4a5568 !important;
    }

    .dataframe {
        font-size: 14px !important;
        border-radius: 10px;
        overflow: hidden;
    }

    .dataframe thead tr th {
        background-color: #667eea !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .stButton > button:hover {
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        transform: translateY(-2px);
    }

    hr {
        border: none;
        height: 3px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        margin: 2rem 0;
    }

    .streamlit-expanderHeader {
        background-color: #f7fafc;
        border-radius: 10px;
        font-weight: 600;
        color: #2d3748;
    }
</style>
""", unsafe_allow_html=True)

# Data Path Configuration
DATA_PATH = "../data/GlobalWeatherRepository_cleaned.csv"

# Cache data loading
@st.cache_data
def get_data():
    try:
        return load_data(DATA_PATH)
    except FileNotFoundError:
        st.error(f"Data file not found at: {DATA_PATH}")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

# Load data
df = get_data()

# Sidebar Filters
with st.sidebar:
    st.markdown("# FILTERS")
   

    st.markdown("### 🌍 Country Selection")
    countries = sorted(df["country"].dropna().unique().tolist())
    selected_countries = st.multiselect(
        "Select Countries",
        countries,
        default=countries[:5] if len(countries) > 5 else countries[:3],
        help="Select one or more countries to analyze"
    )

    # Date Range Filter
    st.markdown("### 📅 Date Range")
    date_min, date_max = df["date"].min(), df["date"].max()
    selected_dates = st.date_input(
        "Select Date Range",
        (date_min, date_max),
        min_value=date_min,
        max_value=date_max
    )

    # Metric Group Filter
    st.markdown("### 📈 Analysis Category")
    metric_group = st.selectbox(
        "Choose Analysis Type",
        [
            "Executive Summary",
            "Temperature Analysis",
            "Humidity & Visibility",
            "Wind Patterns",
            "Precipitation & Pressure",
            "Air Quality",
            "Geographic Analysis",
            "Extreme Events",
            "Forecasting"
        ],
        help="Select which aspect of weather to analyze"
    )

   

    st.markdown("---")

    # Data Overview
    st.markdown("### 📊 Data Overview")
    dff = df.copy()
    if selected_countries:
        dff = dff[dff["country"].isin(selected_countries)]
    if selected_dates and len(selected_dates) == 2:
        start, end = selected_dates
        dff = dff[(dff["date"] >= pd.to_datetime(start)) & (dff["date"] <= pd.to_datetime(end))]

    st.metric("Total Records", f"{len(dff):,}")
    st.metric("Countries Selected", f"{len(selected_countries)}")
    st.metric("Date Range (Days)", f"{(dff['date'].max() - dff['date'].min()).days}")

    st.markdown("---")
    st.markdown("### ℹ️ How to Use Filters")
    st.info("""
1. **🌍 Country Selection:** Choose one or more countries to focus your analysis on.  
2. **📅 Date Range:** Pick a custom time period to filter the dataset by date.  
3. **📈 Analysis Category:** Select the type of weather insight you’d like to explore — from temperature and humidity to forecasting and advanced analytics.  
4. **📊 Data Overview:** Review the number of records, selected countries, and date range before running deeper analyses.  

💡 *Tip:* Use fewer countries and a shorter date range for faster dashboard performance.
""")


# Main Dashboard Header
st.markdown("# 🌍 ClimateScope — Global Weather Dashboard")


# Apply filters to dataframe
dff = df.copy()
if selected_countries:
    dff = dff[dff["country"].isin(selected_countries)]
if selected_dates and len(selected_dates) == 2:
    start, end = selected_dates
    dff = dff[(dff["date"] >= pd.to_datetime(start)) & (dff["date"] <= pd.to_datetime(end))]

# Check if filtered data is empty
if dff.empty:
    st.warning("No data available for the selected filters. Please adjust your selection.")
    st.stop()


def make_interactive_config():
    return {
        'scrollZoom': True,
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToAdd': ['pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']
    }
# ==================== EXECUTIVE SUMMARY ====================
if metric_group == "Executive Summary":
    st.markdown("## 📊 Executive Summary")

    # KPI Metrics Row 1
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if "temperature_celsius" in dff.columns:
            avg_temp = dff["temperature_celsius"].mean()
            st.metric("Avg Temperature", f"{avg_temp:.1f}°C")

    with col2:
        if "feels_like_celsius" in dff.columns:
            avg_feels = dff["feels_like_celsius"].mean()
            st.metric("Avg Feels Like", f"{avg_feels:.1f}°C")

    with col3:
        if "humidity" in dff.columns:
            avg_humid = dff["humidity"].mean()
            st.metric("Avg Humidity", f"{avg_humid:.1f}%")

    with col4:
        if "wind_kph" in dff.columns:
            avg_wind = dff["wind_kph"].mean()
            st.metric("Avg Wind Speed", f"{avg_wind:.1f} km/h")

    with col5:
        if "pressure_mb" in dff.columns:
            avg_pressure = dff["pressure_mb"].mean()
            st.metric("Avg Pressure", f"{avg_pressure:.1f} mb")

    # KPI Metrics Row 2
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if "precip_mm" in dff.columns:
            avg_precip = dff["precip_mm"].mean()
            st.metric("Avg Precipitation", f"{avg_precip:.2f} mm")

    with col2:
        if "visibility_km" in dff.columns:
            avg_vis = dff["visibility_km"].mean()
            st.metric("Avg Visibility", f"{avg_vis:.1f} km")

    with col3:
        if "uv_index" in dff.columns:
            avg_uv = dff["uv_index"].mean()
            st.metric("Avg UV Index", f"{avg_uv:.1f}")

    with col4:
        if "cloud" in dff.columns:
            avg_cloud = dff["cloud"].mean()
            st.metric("Avg Cloud Cover", f"{avg_cloud:.1f}%")

    with col5:
        if "air_quality_us-epa-index" in dff.columns:
            avg_aqi = dff["air_quality_us-epa-index"].mean()
            st.metric("Avg AQI", f"{avg_aqi:.1f}")

    st.markdown("---")

    # Top Performers Section
    st.markdown("## 🏆 Key Highlights")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔥 Hottest Countries")
        if "country" in dff.columns and "temperature_celsius" in dff.columns:
            top_hot = dff.groupby("country")["temperature_celsius"].mean().sort_values(ascending=False).head(5)
            for idx, (country, temp) in enumerate(top_hot.items(), 1):
                st.markdown(f"**{idx}. {country}** — {temp:.2f}°C")

    with col2:
        st.markdown("### ❄️ Coldest Countries")
        if "country" in dff.columns and "temperature_celsius" in dff.columns:
            top_cold = dff.groupby("country")["temperature_celsius"].mean().sort_values().head(5)
            for idx, (country, temp) in enumerate(top_cold.items(), 1):
                st.markdown(f"**{idx}. {country}** — {temp:.2f}°C")

    st.markdown("---")

    # 3D Visualization (moved from Geographic Analysis)
    st.markdown("## 🎲 3D Weather Visualization")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        x_metric = st.selectbox("X-Axis", ["humidity", "temperature_celsius", "wind_kph", "pressure_mb"], key="x_exec")
    with col2:
        y_metric = st.selectbox("Y-Axis", ["temperature_celsius", "humidity", "precip_mm", "visibility_km"], key="y_exec")
    with col3:
        z_metric = st.selectbox("Z-Axis", ["pressure_mb", "wind_kph", "humidity", "temperature_celsius"], key="z_exec")
    with col4:
        chart_type = st.selectbox("Chart Type", ["Scatter 3D", "Surface", "Line 3D", "Mesh 3D", "Bubble 3D"], key="chart_type_exec")

    fig_3d = generate_3d_chart(dff, x_metric=x_metric, y_metric=y_metric, z_metric=z_metric, chart_type=chart_type)
    if fig_3d:
        st.plotly_chart(fig_3d, use_container_width=True, config=make_interactive_config())
    else:
        st.warning("3D visualization unavailable for selected metrics.")

    st.markdown("---")

    # AI-Generated Insights
    st.markdown("## 🧠 Insights")
    insights = generate_insights(dff)

    cols = st.columns(2)
    for idx, (category, insight) in enumerate(insights.items()):
        with cols[idx % 2]:
            with st.expander(f"💡 {category} Insights", expanded=True):
                st.write(insight)

    st.markdown("---")

    # Quick Overview Charts
    st.markdown("## 📈 Quick Overview Charts")

    col1, col2 = st.columns(2)

    with col1:
        if "temperature_celsius" in dff.columns and "date" in dff.columns:
            daily_temp = dff.groupby("date")["temperature_celsius"].mean().reset_index()
            fig = px.line(daily_temp, x="date", y="temperature_celsius",
                         title="Temperature Trend", labels={"temperature_celsius": "Temperature (°C)", "date": "Date"})
            fig.update_traces(line_color='#FF6B6B', line_width=2)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "humidity" in dff.columns and "date" in dff.columns:
            daily_humid = dff.groupby("date")["humidity"].mean().reset_index()
            fig = px.line(daily_humid, x="date", y="humidity",
                         title="Humidity Trend", labels={"humidity": "Humidity (%)", "date": "Date"})
            fig.update_traces(line_color='#4ECDC4', line_width=2)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if "wind_kph" in dff.columns and "date" in dff.columns:
            daily_wind = dff.groupby("date")["wind_kph"].mean().reset_index()
            fig = px.area(daily_wind, x="date", y="wind_kph",
                         title="Wind Speed Trend", labels={"wind_kph": "Wind Speed (km/h)", "date": "Date"})
            fig.update_traces(line_color='#3498db', fillcolor='rgba(52, 152, 219, 0.3)')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "precip_mm" in dff.columns and "date" in dff.columns:
            daily_precip = dff.groupby("date")["precip_mm"].mean().reset_index()
            fig = px.bar(daily_precip, x="date", y="precip_mm",
                        title="Precipitation Pattern", labels={"precip_mm": "Precipitation (mm)", "date": "Date"})
            fig.update_traces(marker_color='#27ae60')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

# ==================== TEMPERATURE ANALYSIS ====================
elif metric_group == "Temperature Analysis":
    st.markdown("## 🌡️ Temperature Analysis")

    if "temperature_celsius" in dff.columns:
        # Temperature Statistics
        col1, col2, col3, col4, col5 = st.columns(5)
        temp_mean = dff["temperature_celsius"].mean()
        temp_median = dff["temperature_celsius"].median()
        temp_std = dff["temperature_celsius"].std()
        temp_max = dff["temperature_celsius"].max()
        temp_min = dff["temperature_celsius"].min()

        with col1:
            st.metric("Mean Temperature", f"{temp_mean:.2f}°C")
        with col2:
            st.metric("Median Temperature", f"{temp_median:.2f}°C")
        with col3:
            st.metric("Std Deviation", f"{temp_std:.2f}°C")
        with col4:
            st.metric("Max Temperature", f"{temp_max:.2f}°C")
        with col5:
            st.metric("Min Temperature", f"{temp_min:.2f}°C")

        st.markdown("---")

        # Temperature Distribution
        st.markdown("### 📊 Temperature Distribution (KDE)")
        fig = px.histogram(dff, x="temperature_celsius", nbins=50, marginal="box",
                         title="Temperature Distribution with Box Plot",
                         labels={"temperature_celsius": "Temperature (°C)"})
        fig.update_traces(marker_color='#FF6B6B')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Insights Section
        st.markdown("### 💡 Temperature Insights")
        variability = "high" if temp_std > 15 else "moderate" if temp_std > 8 else "low"
        st.info(f"""
        - **Average Temperature:** {temp_mean:.2f}°C
        - **Temperature Range:** {temp_min:.2f}°C to {temp_max:.2f}°C ({temp_max - temp_min:.2f}°C spread)
        - **Variability:** {variability.title()} (σ = {temp_std:.2f}°C)
        - **Distribution:** {'Positively skewed' if dff['temperature_celsius'].skew() > 0 else 'Negatively skewed' if dff['temperature_celsius'].skew() < 0 else 'Normally distributed'}
        """)

        st.markdown("---")

        # Temperature Trend
        st.markdown("### 📈 Temperature Trend Over Time")
        daily_temp = dff.groupby("date")[["temperature_celsius", "feels_like_celsius"]].mean().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_temp["date"], y=daily_temp["temperature_celsius"],
                                mode='lines', name='Actual Temperature', line=dict(color='red', width=2)))
        if "feels_like_celsius" in daily_temp.columns:
            fig.add_trace(go.Scatter(x=daily_temp["date"], y=daily_temp["feels_like_celsius"],
                                    mode='lines', name='Feels Like', line=dict(color='orange', width=2)))
        fig.update_layout(height=500, hovermode='x unified', xaxis_title="Date", yaxis_title="Temperature (°C)")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Country Comparison - Top 5 and Bottom 5
        if "country" in dff.columns:
            st.markdown("### 🌍 Country Temperature Comparison")

            country_temps = dff.groupby("country")["temperature_celsius"].mean().sort_values(ascending=False)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 🔥 Top 5 Hottest Countries")
                top5 = country_temps.head(5).reset_index()
                fig = px.bar(top5, x="country", y="temperature_celsius",
                           title="Top 5 Hottest Countries",
                           labels={"temperature_celsius": "Avg Temp (°C)", "country": "Country"},
                           color="temperature_celsius", color_continuous_scale='Reds')
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("#### ❄️ Bottom 5 Coldest Countries")
                bottom5 = country_temps.tail(5).reset_index()
                fig = px.bar(bottom5, x="country", y="temperature_celsius",
                           title="Bottom 5 Coldest Countries",
                           labels={"temperature_celsius": "Avg Temp (°C)", "country": "Country"},
                           color="temperature_celsius", color_continuous_scale='Blues')
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            # Full Comparison
            st.markdown("#### 📊 All Countries Comparison")
            comp, fig = region_comparisons(dff, metric="temperature_celsius")
            if fig:
                 if hasattr(fig, "update_layout"):
                     fig.update_layout(height=600)
                     st.plotly_chart(fig, use_container_width=True)
            else:
                  fig.set_size_inches(10, 6)
                  st.pyplot(fig, use_container_width=True)



    else:
        st.warning("Temperature data not available in the selected dataset.")

# ==================== HUMIDITY & VISIBILITY ====================
elif metric_group == "Humidity & Visibility":
    st.markdown("## 💧 Humidity & Visibility Analysis")

    col1, col2 = st.columns(2)

    with col1:
        if "humidity" in dff.columns:
            st.metric("Avg Humidity", f"{dff['humidity'].mean():.1f}%")
            st.metric("Max Humidity", f"{dff['humidity'].max():.1f}%")
            st.metric("Min Humidity", f"{dff['humidity'].min():.1f}%")

    with col2:
        if "visibility_km" in dff.columns:
            st.metric("Avg Visibility", f"{dff['visibility_km'].mean():.2f} km")
            st.metric("Max Visibility", f"{dff['visibility_km'].max():.2f} km")
            st.metric("Min Visibility", f"{dff['visibility_km'].min():.2f} km")

    st.markdown("---")

    # Humidity vs Temperature Scatter
    if "humidity" in dff.columns and "temperature_celsius" in dff.columns:
        st.markdown("### 🔥 Humidity vs Temperature Relationship")
        fig = px.scatter(dff, x="humidity", y="temperature_celsius", color="country" if "country" in dff.columns else None,
                        title="Humidity vs Temperature",
                        labels={"humidity": "Humidity (%)", "temperature_celsius": "Temperature (°C)"},
                        opacity=0.6, trendline="ols")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Correlation insight
        corr = dff[["humidity", "temperature_celsius"]].corr().iloc[0, 1]
        st.info(f"**Correlation:** {corr:.3f} — {'Strong' if abs(corr) > 0.7 else 'Moderate' if abs(corr) > 0.4 else 'Weak'} {'positive' if corr > 0 else 'negative'} relationship")

    st.markdown("---")

    # Country-wise Comparison
    if "country" in dff.columns and "humidity" in dff.columns:
        st.markdown("### 🌍 Country-wise Humidity & Visibility Comparison")

        country_humid = dff.groupby("country")[["humidity", "visibility_km"]].mean().sort_values("humidity", ascending=False).head(15).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(x=country_humid["country"], y=country_humid["humidity"],
                            name="Humidity (%)", marker_color='#4ECDC4'))
        if "visibility_km" in country_humid.columns:
            fig.add_trace(go.Bar(x=country_humid["country"], y=country_humid["visibility_km"],
                                name="Visibility (km)", marker_color='#95E1D3', yaxis="y2"))

        fig.update_layout(
            title="Top 15 Countries: Humidity & Visibility",
            xaxis_title="Country",
            yaxis_title="Humidity (%)",
            yaxis2=dict(title="Visibility (km)", overlaying='y', side='right'),
            height=500,
            xaxis_tickangle=-45,
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Visibility Trend
    if "visibility_km" in dff.columns and "date" in dff.columns:
        st.markdown("### 🌫️ Visibility Trend Over Time")
        daily_vis = dff.groupby("date")["visibility_km"].mean().reset_index()
        fig = px.line(daily_vis, x="date", y="visibility_km",
                     title="Average Daily Visibility", labels={"visibility_km": "Visibility (km)", "date": "Date"})
        fig.update_traces(line_color='#95E1D3', line_width=2)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Insights Section
    st.markdown("### 💡 Humidity & Visibility Insights")
    if "humidity" in dff.columns and "visibility_km" in dff.columns:
        humid_vis_corr = dff[["humidity", "visibility_km"]].corr().iloc[0, 1]
        st.info(f"""
        **Correlation between Humidity and Visibility:** {humid_vis_corr:.3f}

        {f'High humidity tends to reduce visibility (correlation: {humid_vis_corr:.3f}). Moisture in the air can trap particulates and reduce visibility.' if humid_vis_corr < -0.3 else 'Humidity and visibility show minimal correlation.' if abs(humid_vis_corr) < 0.3 else 'Interestingly, higher humidity correlates with better visibility in this dataset.'}
        """)

# ==================== WIND PATTERNS ====================
elif metric_group == "Wind Patterns":
    st.markdown("## 🌬️ Wind Pattern Analysis")

    if "wind_kph" in dff.columns:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Avg Wind Speed", f"{dff['wind_kph'].mean():.2f} km/h")
        with col2:
            st.metric("Max Wind Speed", f"{dff['wind_kph'].max():.2f} km/h")
        with col3:
            if "gust_kph" in dff.columns:
                st.metric("Avg Gust Speed", f"{dff['gust_kph'].mean():.2f} km/h")
        with col4:
            if "gust_kph" in dff.columns:
                st.metric("Max Gust Speed", f"{dff['gust_kph'].max():.2f} km/h")

        st.markdown("---")

        # Wind Speed Trend
        st.markdown("### 🌪️ Wind Speed Trend Over Time")
        daily_wind = dff.groupby("date")[["wind_kph", "gust_kph"]].mean().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_wind["date"], y=daily_wind["wind_kph"],
                                mode='lines', name='Wind Speed', line=dict(color='blue', width=2)))
        if "gust_kph" in daily_wind.columns:
            fig.add_trace(go.Scatter(x=daily_wind["date"], y=daily_wind["gust_kph"],
                                    mode='lines', name='Gust Speed', line=dict(color='red', width=2)))
        fig.update_layout(height=500, hovermode='x unified', xaxis_title="Date", yaxis_title="Speed (km/h)")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Country-wise Comparison
        if "country" in dff.columns:
            st.markdown("### 🌍 Country-wise Wind Speed Comparison")

            country_wind = dff.groupby("country")["wind_kph"].mean().sort_values(ascending=False).head(15).reset_index()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 🌪️ Windiest Countries")
                windiest = country_wind.head(5)
                for idx, row in windiest.iterrows():
                    st.markdown(f"**{idx+1}. {row['country']}** — {row['wind_kph']:.2f} km/h")

            with col2:
                st.markdown("#### 🍃 Calmest Countries")
                calmest = dff.groupby("country")["wind_kph"].mean().sort_values().head(5)
                for idx, (country, speed) in enumerate(calmest.items(), 1):
                    st.markdown(f"**{idx}. {country}** — {speed:.2f} km/h")

            fig = px.bar(country_wind, x="country", y="wind_kph",
                        title="Top 15 Windiest Countries",
                        labels={"wind_kph": "Avg Wind Speed (km/h)", "country": "Country"},
                        color="wind_kph", color_continuous_scale='Blues')
            fig.update_layout(height=500, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Wind Distribution
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Wind Speed Distribution")
            fig = px.histogram(dff, x="wind_kph", nbins=40,
                             title="Wind Speed Distribution", labels={"wind_kph": "Wind Speed (km/h)"})
            fig.update_traces(marker_color='#3498db')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            if "precip_mm" in dff.columns and "gust_kph" in dff.columns:
                st.markdown("### 🌧️ Wind Gusts vs Precipitation")
                fig = px.scatter(dff, x="gust_kph", y="precip_mm",
                               title="Wind Gusts vs Precipitation",
                               labels={"gust_kph": "Gust Speed (km/h)", "precip_mm": "Precipitation (mm)"},
                               opacity=0.5)
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Insights
        st.markdown("### 💡 Wind Insights")
        wind_mean = dff['wind_kph'].mean()
        wind_category = "Strong" if wind_mean > 20 else "Moderate" if wind_mean > 10 else "Calm"
        st.info(f"""
        **Wind Conditions:** {wind_category} (Average: {wind_mean:.2f} km/h)

        {f'Strong wind conditions are prevalent, which may indicate frequent storm systems or geographical factors.' if wind_mean > 20 else 'Moderate wind patterns suggest balanced atmospheric conditions.' if wind_mean > 10 else 'Generally calm wind conditions indicate stable weather patterns.'}
        """)

    else:
        st.warning("Wind data not available in the selected dataset.")

# ==================== PRECIPITATION & PRESSURE ====================
elif metric_group == "Precipitation & Pressure":
    st.markdown("## 🌧️ Precipitation & Pressure Analysis")

    col1, col2 = st.columns(2)

    with col1:
        if "precip_mm" in dff.columns:
            st.metric("Avg Precipitation", f"{dff['precip_mm'].mean():.2f} mm")
            st.metric("Max Precipitation", f"{dff['precip_mm'].max():.2f} mm")
            rainy_days = (dff["precip_mm"] > 0).sum()
            st.metric("Rainy Observations", f"{rainy_days:,} ({rainy_days/len(dff)*100:.1f}%)")

    with col2:
        if "pressure_mb" in dff.columns:
            st.metric("Avg Pressure", f"{dff['pressure_mb'].mean():.2f} mb")
            st.metric("Max Pressure", f"{dff['pressure_mb'].max():.2f} mb")
            st.metric("Min Pressure", f"{dff['pressure_mb'].min():.2f} mb")

    st.markdown("---")

    # Regional Comparison
    if "country" in dff.columns and "precip_mm" in dff.columns:
        st.markdown("### 🌍 Regional Precipitation Comparison")

        country_precip = dff.groupby("country")["precip_mm"].mean().sort_values(ascending=False).head(15).reset_index()

        fig = px.bar(country_precip, x="precip_mm", y="country", orientation='h',
                    title="Top 15 Countries by Precipitation",
                    labels={"precip_mm": "Avg Precipitation (mm)", "country": "Country"},
                    color="precip_mm", color_continuous_scale='Blues')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Monthly Precipitation
    if "precip_mm" in dff.columns and "date" in dff.columns:
        st.markdown("### 📊 Monthly Precipitation Pattern")
        monthly_precip = dff.groupby(dff["date"].dt.to_period("M"))["precip_mm"].mean().reset_index()
        monthly_precip["date"] = monthly_precip["date"].astype(str)
        fig = px.bar(monthly_precip, x="date", y="precip_mm",
                    title="Monthly Average Precipitation", labels={"precip_mm": "Precipitation (mm)", "date": "Month"})
        fig.update_traces(marker_color='#3498db')
        fig.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Pressure Trend
    if "pressure_mb" in dff.columns and "date" in dff.columns:
        st.markdown("### 📉 Pressure Trend Over Time")
        daily_pressure = dff.groupby("date")["pressure_mb"].mean().reset_index()
        fig = px.line(daily_pressure, x="date", y="pressure_mb",
                     title="Daily Average Pressure", labels={"pressure_mb": "Pressure (mb)", "date": "Date"})
        fig.update_traces(line_color='#8e44ad', line_width=2)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Pressure vs Precipitation
    if "pressure_mb" in dff.columns and "precip_mm" in dff.columns:
        st.markdown("### 💨 Pressure vs Precipitation Relationship")
        fig = px.scatter(dff, x="pressure_mb", y="precip_mm", color="country" if "country" in dff.columns else None,
                        title="Pressure vs Precipitation",
                        labels={"pressure_mb": "Pressure (mb)", "precip_mm": "Precipitation (mm)"},
                        opacity=0.5, trendline="ols")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        corr = dff[["pressure_mb", "precip_mm"]].corr().iloc[0, 1]
        st.info(f"**Correlation:** {corr:.3f} — {f'Low pressure systems tend to bring rainfall (negative correlation: {corr:.3f}).' if corr < -0.2 else 'Pressure and precipitation show minimal direct correlation.' if abs(corr) < 0.2 else 'Interestingly, higher pressure correlates with more precipitation in this dataset.'}")

    st.markdown("---")

    # Insights
    st.markdown("### 💡 Precipitation & Pressure Insights")
    if "precip_mm" in dff.columns:
        precip_mean = dff["precip_mm"].mean()
        rainy_pct = (dff["precip_mm"] > 0).sum() / len(dff) * 100
        st.info(f"""
        **Precipitation Patterns:**
        - Average precipitation: {precip_mean:.2f} mm
        - Rainy observations: {rainy_pct:.1f}% of total records
        - {'Frequent rainfall indicates wet climate conditions' if rainy_pct > 50 else 'Moderate rainfall patterns' if rainy_pct > 25 else 'Generally dry conditions with occasional rainfall'}
        """)

# ==================== AIR QUALITY ====================
elif metric_group == "Air Quality":
    st.markdown("## 🌫️ Air Quality Analysis")

    aq_cols = [c for c in ["air_quality_PM2.5", "air_quality_PM10", "air_quality_us-epa-index",
                           "air_quality_Carbon_Monoxide", "air_quality_Ozone"] if c in dff.columns]

    if aq_cols:
        # AQI Metrics
        if "air_quality_us-epa-index" in dff.columns:
            col1, col2, col3 = st.columns(3)
            avg_aqi = dff["air_quality_us-epa-index"].mean()
            with col1:
                st.metric("Avg AQI", f"{avg_aqi:.2f}")
            with col2:
                aqi_category = {1: "Good", 2: "Moderate", 3: "Unhealthy for Sensitive",
                               4: "Unhealthy", 5: "Very Unhealthy", 6: "Hazardous"}
                st.metric("AQI Category", aqi_category.get(round(avg_aqi), "Unknown"))
            with col3:
                st.metric("Max AQI", f"{dff['air_quality_us-epa-index'].max():.2f}")

        st.markdown("---")

        # AQ Trend
        st.markdown("### 📈 Air Quality Trend Over Time")
        daily_aq = dff.groupby("date")[aq_cols].mean().reset_index()
        fig = go.Figure()
        colors = ['#e74c3c', '#f39c12', '#27ae60', '#3498db', '#9b59b6']
        for idx, col in enumerate(aq_cols):
            fig.add_trace(go.Scatter(x=daily_aq["date"], y=daily_aq[col],
                                    mode='lines', name=col.replace('air_quality_', ''),
                                    line=dict(color=colors[idx % len(colors)], width=2)))
        fig.update_layout(height=500, hovermode='x unified', xaxis_title="Date", yaxis_title="Value")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # AQI vs Temperature
        if "temperature_celsius" in dff.columns and "air_quality_us-epa-index" in dff.columns:
            st.markdown("### 🌡️ Air Quality vs Temperature")
            fig = px.scatter(dff, x="temperature_celsius", y="air_quality_us-epa-index",
                           title="AQI vs Temperature Relationship",
                           labels={"temperature_celsius": "Temperature (°C)", "air_quality_us-epa-index": "AQI"},
                           opacity=0.5, trendline="ols", color="country" if "country" in dff.columns else None)
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

            corr = dff[["temperature_celsius", "air_quality_us-epa-index"]].corr().iloc[0, 1]
            st.info(f"**Temperature-AQI Correlation:** {corr:.3f} — {f'Higher temperatures tend to worsen air quality.' if corr > 0.3 else 'Temperature shows minimal impact on air quality.' if abs(corr) < 0.3 else 'Higher temperatures correlate with better air quality.'}")

        st.markdown("---")

        # AQI vs Humidity
        if "humidity" in dff.columns and "air_quality_us-epa-index" in dff.columns:
            st.markdown("### 💧 Air Quality vs Humidity")
            fig = px.scatter(dff, x="humidity", y="air_quality_us-epa-index",
                           title="AQI vs Humidity Relationship",
                           labels={"humidity": "Humidity (%)", "air_quality_us-epa-index": "AQI"},
                           opacity=0.5, trendline="ols")
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

            corr = dff[["humidity", "air_quality_us-epa-index"]].corr().iloc[0, 1]
            st.info(f"**Humidity-AQI Correlation:** {corr:.3f} — {f'High humidity may trap pollutants, worsening air quality.' if corr > 0.3 else 'Humidity shows minimal correlation with air quality.' if abs(corr) < 0.3 else 'Higher humidity correlates with better air quality.'}")

        st.markdown("---")

        # Pollutant Correlation
        if len(aq_cols) > 1:
            st.markdown("### 🔗 Pollutant Correlation Heatmap")
            corr_aq = dff[aq_cols].corr()
            fig = px.imshow(corr_aq, text_auto=True, color_continuous_scale='YlOrRd',
                           title="Air Quality Pollutant Correlations")
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Regional AQI
        if "country" in dff.columns and "air_quality_us-epa-index" in dff.columns:
            st.markdown("### 🗺️ Regional AQI Comparison")
            country_aq = dff.groupby("country")["air_quality_us-epa-index"].mean().sort_values(ascending=False).head(15).reset_index()
            fig = px.bar(country_aq, x="air_quality_us-epa-index", y="country", orientation='h',
                        title="Top 15 Countries by AQI (Higher = Worse)",
                        labels={"air_quality_us-epa-index": "Avg AQI", "country": "Country"})
            fig.update_traces(marker_color='#e74c3c')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Conclusions
        st.markdown("### 💡 Air Quality Conclusions")
        if "air_quality_us-epa-index" in dff.columns:
            avg_aqi = dff["air_quality_us-epa-index"].mean()
            aqi_cat = {1: "Good", 2: "Moderate", 3: "Unhealthy for Sensitive Groups",
                      4: "Unhealthy", 5: "Very Unhealthy", 6: "Hazardous"}
            category = aqi_cat.get(round(avg_aqi), "Unknown")

            st.info(f"""
            **Overall Air Quality: {category}** (Average AQI: {avg_aqi:.2f})

            **Key Findings:**
            - Air quality is generally {category.lower()}
            - {'Immediate action needed to reduce pollution levels' if avg_aqi > 4 else 'Monitor sensitive groups during peak pollution' if avg_aqi > 3 else 'Acceptable air quality for general population'}
            - Pollutant levels {'exceed' if avg_aqi > 3 else 'meet'} standard health guidelines
            """)

    else:
        st.warning("Air quality data not available in the selected dataset.")

# ==================== GEOGRAPHIC ANALYSIS ====================
elif metric_group == "Geographic Analysis":
    st.markdown("## 🗺️ Geographic & Regional Analysis")

    # Map Visualization
    st.markdown("### 🗺️ Global Weather Map")
    metric_choice = st.selectbox(
        "Select Metric for Map Visualization",
        ["temperature_celsius", "humidity", "pressure_mb", "precip_mm", "air_quality_us-epa-index", "wind_kph"]
    )

    if metric_choice in dff.columns:
        # Choropleth Map
        if "country" in dff.columns:
            country_means = dff.groupby("country")[metric_choice].mean().reset_index().sort_values(metric_choice, ascending=False)
            fig = px.choropleth(
                country_means,
                locations="country",
                locationmode="country names",
                color=metric_choice,
                color_continuous_scale="RdYlBu_r",
                title=f"Global {metric_choice.replace('_', ' ').title()} Distribution",
                projection="natural earth",
                height=600
            )
            fig.update_geos(showcountries=True, showframe=True, showcoastlines=True)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Top 5 and Bottom 5
            st.markdown(f"### 🏆 Rankings for {metric_choice.replace('_', ' ').title()}")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 🔝 Top 5 Highest")
                top5 = country_means.head(5)
                for idx, row in top5.iterrows():
                    st.success(f"**{idx+1}. {row['country']}** — {row[metric_choice]:.2f}")

            with col2:
                st.markdown("#### 🔻 Top 5 Lowest")
                bottom5 = country_means.tail(5).iloc[::-1]
                for idx, row in enumerate(bottom5.itertuples(), 1):
                    st.info(f"**{idx}. {row.country}** — {getattr(row, metric_choice):.2f}")

    st.markdown("---")

    # Country-Level Summary (removed heatmap as requested)
    if "country" in dff.columns:
        st.markdown("### 📋 Country-Level Climate Summary")
        agg = country_aggregates(dff)
        if not agg.empty:
            with st.expander("View Detailed Country Statistics", expanded=False):
                st.dataframe(agg.head(20), use_container_width=True, height=400)

# ==================== EXTREME EVENTS ====================
elif metric_group == "Extreme Events":
    st.markdown("## ⚠️ Extreme Weather Events Detection")

    thresholds, ext_events, summary = detect_extreme_events(dff)

    # Display Thresholds
    st.markdown("### ⚙️ Detection Thresholds")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if "high_temp" in thresholds:
            st.metric("High Temp Threshold", f"{thresholds['high_temp']:.2f}°C")
    with col2:
        if "high_wind" in thresholds:
            st.metric("High Wind Threshold", f"{thresholds['high_wind']:.2f} km/h")
    with col3:
        if "heavy_precip" in thresholds:
            st.metric("Heavy Precip Threshold", f"{thresholds['heavy_precip']:.2f} mm")
    with col4:
        if "low_visibility" in thresholds:
            st.metric("Low Visibility Threshold", f"{thresholds['low_visibility']:.2f} km")

    st.markdown("---")

    if not ext_events.empty:
        st.markdown(f"### 📊 Detected Events: {len(ext_events):,} extreme conditions")

        # Event Type Breakdown
        if "extreme_types" in ext_events.columns:
            event_counts = ext_events["extreme_types"].value_counts().head(10)
            fig = px.bar(
                x=event_counts.values,
                y=event_counts.index,
                orientation='h',
                title="Top 10 Extreme Event Types",
                labels={"x": "Count", "y": "Event Type"}
            )
            fig.update_traces(marker_color='#e74c3c')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        st.markdown("""
            **Legend:**
            - 🔴 **Red**: Heatwave  
            - 🔵 **Blue**: Flood  
            - 🟣 **Purple**: Storm  
            - 🟡 **Yellow**: Drought  
            - ⚫ **Gray**: Mixed Events
        """)

        # Color-coded Choropleth Map
        st.markdown("### 🗺️ Extreme Events Map (Color-coded by Event Type)")

        if "country" in ext_events.columns and "extreme_types" in ext_events.columns:
            # Create country-level event summary
            country_events = ext_events.groupby("country")["extreme_types"].apply(
                lambda x: x.mode()[0] if len(x.mode()) > 0 else "Mixed"
            ).reset_index()
            country_events.columns = ["country", "primary_event"]

            country_events["color_code"] = country_events["primary_event"].map(
                lambda x: 1 if "Heatwave" in str(x)
                else 2 if "Flood" in str(x)
                else 3 if "Storm" in str(x)
                else 4 if "Drought" in str(x)
                else 5
            )

            fig = px.choropleth(
                country_events,
                locations="country",
                locationmode="country names",
                color="color_code",
                hover_name="country",
                hover_data={"primary_event": True, "color_code": False},
                color_continuous_scale=[
                    [0.0, "#FF0000"],   # Heatwave - Red
                    [0.25, "#0000FF"],  # Flood - Blue
                    [0.5, "#9B59B6"],   # Storm - Purple
                    [0.75, "#FFD700"],  # Drought - Yellow
                    [1.0, "#808080"]    # Mixed - Gray
                ],
                title="Extreme Events by Country (Color-coded)",
                projection="natural earth",
                height=600
            )
            fig.update_geos(showcountries=True, showframe=True, showcoastlines=True)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Extreme Events Table with color coding
        st.markdown("### 📋 Extreme Events Log")

        display_cols = [
            c for c in [
                "date", "country", "location_name", "temperature_celsius",
                "wind_kph", "precip_mm", "visibility_km", "extreme_types"
            ] if c in ext_events.columns
        ]

        if display_cols:
            df_display = ext_events[display_cols].copy()

            # Style function: slightly darker, readable pastel tones
            def style_extreme_rows(row):
                style = ['color: black'] * len(row)  # Keep text readable
                if "extreme_types" in row and pd.notna(row["extreme_types"]):
                    event_type = str(row["extreme_types"])
                    if "Heatwave" in event_type:
                        bg_color = '#8B0000'  # darker light red
                    elif "Flood" in event_type:
                        bg_color = '#3366CC'  # darker light blue
                    elif "Storm" in event_type:
                        bg_color = '#e0ccff'  # darker light purple
                    elif "Drought" in event_type:
                        bg_color = '#fff5b3'  # darker light yellow
                    else:
                        bg_color = '2B2B2B'  # soft gray for mixed
                    return [f'background-color: {bg_color}; color: black'] * len(row)
                return style

            # Apply styling
            styled_df = df_display.head(100).style.apply(style_extreme_rows, axis=1)

            # Display styled DataFrame
            st.dataframe(styled_df, use_container_width=True, height=500)

            # Download button
            csv = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Extreme Events CSV",
                data=csv,
                file_name=f"extreme_events_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No extreme events detected in the selected data range.")

# ==================== FORECASTING ====================
elif metric_group == "Forecasting":
    st.markdown("## 📈 Weather Forecasting (Table Format)")

   

    # Forecast Settings
    col1, col2 = st.columns(2)
    with col1:
        forecast_days = st.slider("Forecast Period (Days)", 7, 90, 30)

    st.markdown("---")

    # Multi-metric forecast
    st.markdown("### 📊 Multi-Metric Forecast Table")

    forecast_df = forecast_multiple_metrics(dff, periods=forecast_days)

    if not forecast_df.empty:
        # Display as table
        st.dataframe(forecast_df, use_container_width=True, height=500)

        # Summary Statistics
        st.markdown("### 📈 Forecast Summary")

        cols_to_analyze = [c for c in forecast_df.columns if c != 'Date']

        for col in cols_to_analyze:
            with st.expander(f"📊 {col} Forecast Insights", expanded=False):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Forecast Mean", f"{forecast_df[col].mean():.2f}")
                with col2:
                    st.metric("Forecast Max", f"{forecast_df[col].max():.2f}")
                with col3:
                    st.metric("Forecast Min", f"{forecast_df[col].min():.2f}")
                with col4:
                    trend = "Increasing" if forecast_df[col].iloc[-1] > forecast_df[col].iloc[0] else "Decreasing"
                    st.metric("Trend", trend)

        # Download forecast
        csv = forecast_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Forecast CSV",
            data=csv,
            file_name=f"weather_forecast_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

        # Insights
        st.markdown("### 💡 Forecast Insights")
        insights_text = "**Key Forecast Observations:**\n\n"
        for col in cols_to_analyze:
            mean_val = forecast_df[col].mean()
            trend_val = forecast_df[col].iloc[-1] - forecast_df[col].iloc[0]
            trend_dir = "increasing" if trend_val > 0 else "decreasing"
            insights_text += f"- **{col}:** Average forecast value is {mean_val:.2f}, showing a {trend_dir} trend ({abs(trend_val):.2f} change over {forecast_days} days).\n"

        st.info(insights_text)

    else:
        st.warning("Unable to generate forecast with available data.")

# ==================== FOOTER ====================
st.markdown("---")

