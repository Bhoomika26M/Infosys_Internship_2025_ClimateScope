# ==========================================================
# ClimateScope Professional Dashboard
# Author: Bhagyalaxmi Kali
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------
st.set_page_config(page_title="ClimateScope Dashboard", layout="wide")

# ----------------------------------------------------------
# CUSTOM STYLING
# ----------------------------------------------------------
st.markdown("""
    <style>
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-right: 1px solid #1E293B;
            padding-top: 0 !important;
        }
        .sidebar-title {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            font-size: 22px;
            font-weight: 700;
            color: #60A5FA;
            margin-top: -20px;
            margin-left: 1px;
        }
        .sidebar-title span {
            margin-right: 8px;
            font-size: 22px;
        }
        .sidebar-divider {
            border: none;
            border-top: 1px solid #1E3A8A;
            margin: 8px 0 12px 0;
        }

        /* Main background */
        .main {
            background-color: #0E1117;
            color: #F1F5F9;
        }

        /* Dashboard Header */
        .dashboard-title {
    text-align: center;
    font-size: 36px;
    font-weight: 700;
    color: #60A5FA;
    letter-spacing: 1px;
    margin-top: -40px;   /* moved up by ~1 inch */
    margin-bottom: -10px;
}

.dashboard-subtitle {
    text-align: center;
    font-size: 18px;
    color: #CBD5E1;
    margin-top: 5px;     /* keeps spacing ratio same */
    margin-bottom: 25px;
}


        /* KPI Cards */
        .metric-container {
            background: rgba(37, 99, 235, 0.12);
            border: 1px solid rgba(37, 99, 235, 0.25);
            border-radius: 15px;
            padding: 18px;
            margin: 5px;
            text-align: center;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.25);
            transition: transform 0.2s ease-in-out;
        }
        .metric-container:hover {
            transform: translateY(-4px);
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
        }
        .metric-container h3 {
            font-size: 16px;
            color: #93C5FD;
            margin-bottom: 5px;
        }
        .metric-container p {
            font-size: 22px;
            color: #E2E8F0;
            margin: 0;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------
@st.cache_data
def load_data():
    daily = pd.read_csv("daily_cleaned.csv")
    monthly = pd.read_csv("weather_data_monthly.csv")
    seasonal = pd.read_csv("weather_seasonal_avg.csv")
    yearly = pd.read_csv("weather_yearly_avg.csv")
    return daily, monthly, seasonal, yearly

daily_df, monthly_df, seasonal_df, yearly_df = load_data()

# ----------------------------------------------------------
# EXTRA COLUMNS
# ----------------------------------------------------------
yearly_df["air_quality_score"] = yearly_df[
    ["air_quality_Carbon_Monoxide", "air_quality_Ozone", "air_quality_PM2.5", "air_quality_PM10"]
].mean(axis=1)

def normalize(series):
    return 100 * (series - series.min()) / (series.max() - series.min())

# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------
with st.sidebar:
    st.markdown("<div class='sidebar-title'><span>🌍</span>ClimateScope</div><hr class='sidebar-divider'>", unsafe_allow_html=True)
    page = st.radio("📊 Dashboard Sections", ["Home Overview", "Monthly Trends", "Yearly Analysis", "Seasonal Patterns", "Global Insights"])
    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    countries = sorted(yearly_df["country"].unique())
    selected_countries = st.multiselect("Select Countries", countries, default=countries[:3])

# Filter by selection
daily_df = daily_df[daily_df["country"].isin(selected_countries)]
monthly_df = monthly_df[monthly_df["country"].isin(selected_countries)]
seasonal_df = seasonal_df[seasonal_df["country"].isin(selected_countries)]
yearly_df = yearly_df[yearly_df["country"].isin(selected_countries)]

# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------
st.markdown("<div class='dashboard-title'>ClimateScope Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='dashboard-subtitle'>Advanced Climate & Air Quality Analytics</div>", unsafe_allow_html=True)

# ==========================================================
# HOME OVERVIEW
# ==========================================================
if page == "Home Overview":
    st.markdown("####  Global Climate Overview")
    # ---------------- KPI METRICS ----------------
    col1, col2, col3, col4 = st.columns(4)

    avg_temp = yearly_df["temperature_celsius"].mean()
    avg_wind = yearly_df["wind_kph"].mean()
    avg_aqi = yearly_df["air_quality_score"].mean()
    avg_climate_index = (
        yearly_df["temperature_celsius"].rank(ascending=True)*0.3 +
        yearly_df["air_quality_score"].rank(ascending=True)*0.4 +
        yearly_df["wind_kph"].rank(ascending=False)*0.3
    ).mean()

    for c, t, v in zip(
        [col1, col2, col3, col4],
        ["Avg Temp (°C)", "Avg Wind (kph)", "Air Quality Index", "Climate Index"],
        [avg_temp, avg_wind, avg_aqi, avg_climate_index]
    ):
        c.markdown(
            f"<div class='metric-container'><h3>{t}</h3><p>{v:.2f}</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ---------------- 4 ADVANCED VISUALS ----------------
    r1c1, r1c2 = st.columns(2)
    r2c1, r2c2 = st.columns(2)

    # 🌍 1. Geo Distribution Map
    with r1c1:
        fig = px.scatter_geo(
            yearly_df,
            lat="latitude",
            lon="longitude",
            color="temperature_celsius",
            hover_name="country",
            size="air_quality_score",
            color_continuous_scale="Blues",
            title="🌍 Global Temperature & Air Quality Map",
        )
        fig.update_layout(
            geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
            margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="#E2E8F0"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # 📈 2. Temperature Trend with Rolling Average
    with r1c2:
        df_temp = yearly_df.groupby("year")["temperature_celsius"].mean().reset_index()
        df_temp["Rolling Avg"] = df_temp["temperature_celsius"].rolling(3, min_periods=1).mean()
        fig = px.line(
            df_temp,
            x="year",
            y=["temperature_celsius", "Rolling Avg"],
            labels={"value": "Temperature (°C)", "year": "Year"},
            title="📈 Global Temperature Trend (with 3-Year Rolling Average)",
            color_discrete_sequence=["#60A5FA", "#1E3A8A"],
        )
        fig.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="#E2E8F0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig, use_container_width=True)

    # 🌫️ 3. Air Quality Score Trend
    with r2c1:
        fig = px.line(
            yearly_df,
            x="year",
            y="air_quality_score",
            color="country",
            title="🌫️ Air Quality Score Over Years",
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        fig.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="#E2E8F0"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # 💨 4. Wind Speed vs Air Quality Correlation
    with r2c2:
        fig = px.scatter(
            yearly_df,
            x="wind_kph",
            y="air_quality_score",
            color="country",
            trendline="ols",
            title="💨 Wind Speed vs Air Quality Relationship",
            color_discrete_sequence=px.colors.sequential.Blues,
        )
        fig.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="#E2E8F0"),
        )
        st.plotly_chart(fig, use_container_width=True)


# ==========================================================
# MONTHLY ANALYSIS
# ==========================================================
elif page == "Monthly Trends":
    st.markdown("#### 📅 Monthly Climate Trends")

    # --- Country filter (from sidebar) ---
    selected_countries = st.session_state.get("selected_countries", [])
    if selected_countries:
        monthly_filtered = monthly_df[monthly_df["country"].isin(selected_countries)]
    else:
        monthly_filtered = monthly_df
    # --- Preprocess 'year_month' column for clean display ---
    monthly_filtered = monthly_filtered.copy()
    monthly_filtered["year_month"] = pd.to_datetime(monthly_filtered["year_month"], errors='coerce')
    monthly_filtered = monthly_filtered.sort_values("year_month")
    monthly_filtered["year_month"] = monthly_filtered["year_month"].dt.strftime("%b%Y")



    # --- Month selector (affects only KPIs) ---
    all_months = sorted(monthly_filtered["year_month"].unique())
    selected_month = st.selectbox(
        "Select Month for KPI Analysis",
        all_months,
        index=len(all_months) - 1,
        key="month_selector"
    )

    # --- KPI Data for Selected Month ---
    kpi_df = monthly_filtered[monthly_filtered["year_month"] == selected_month]

    # --- Monthly KPIs ---
    col1, col2, col3, col4 = st.columns(4)
    avg_temp = kpi_df["temperature_celsius"].mean()
    avg_wind = kpi_df["wind_kph"].mean()
    avg_humidity = kpi_df["humidity"].mean()
    avg_precip = kpi_df["precip_mm"].mean()

    with col1:
        st.markdown(
            f"<div class='metric-container'><h3>Avg Temperature (°C)</h3><p>{avg_temp:.2f}</p></div>",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"<div class='metric-container'><h3>Avg Wind Speed (kph)</h3><p>{avg_wind:.2f}</p></div>",
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"<div class='metric-container'><h3>Avg Humidity (%)</h3><p>{avg_humidity:.2f}</p></div>",
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"<div class='metric-container'><h3>Avg Precipitation (mm)</h3><p>{avg_precip:.2f}</p></div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # --- Chart Layout ---
    r1c1, r1c2 = st.columns(2)
    r2c1, r2c2 = st.columns(2)

    # --- 1️⃣ Monthly Average Temperature Trend ---
    with r1c1:
        fig = px.line(
            monthly_filtered,
            x="year_month",
            y="temperature_celsius",
            color="country",
            markers=True,
            title="🌡️ Monthly Average Temperature Trend",
            color_discrete_sequence=px.colors.sequential.Blues,
        )
        fig.update_layout(
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            font_color="#E2E8F0",
            title_font_color="#60A5FA",
            xaxis_title="Month (YYYY-MM)",
            yaxis_title="Temperature (°C)",
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- 2️⃣ Wind Speed Trend ---
    with r1c2:
        fig2 = px.line(
            monthly_filtered,
            x="year_month",
            y="wind_kph",
            color="country",
            markers=True,
            title="💨 Monthly Wind Speed Trend",
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        fig2.update_layout(
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            font_color="#E2E8F0",
            title_font_color="#60A5FA",
            xaxis_title="Month (YYYY-MM)",
            yaxis_title="Wind Speed (kph)",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --- 3️⃣ Combined Air Quality Index ---
    with r2c1:
        monthly_filtered["combined_AQI"] = (
            monthly_filtered["air_quality_PM2.5"] * 0.6 +
            monthly_filtered["air_quality_Ozone"] * 0.4
        )
        fig3 = px.bar(
            monthly_filtered,
            x="year_month",
            y="combined_AQI",
            color="country",
            title="🧪 Combined Air Quality Index (PM2.5 + Ozone)",
            barmode="group",
            color_discrete_sequence=px.colors.sequential.Blues,
        )
        fig3.update_layout(
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            font_color="#E2E8F0",
            title_font_color="#60A5FA",
            xaxis_title="Month (YYYY-MM)",
            yaxis_title="AQI (Scaled)",
        )
        st.plotly_chart(fig3, use_container_width=True)

    # --- 4️⃣ Temperature vs AQI Correlation ---
    with r2c2:
        fig4 = px.scatter(
            monthly_filtered,
            x="temperature_celsius",
            y="combined_AQI",
            color="country",
            trendline="ols",
            title="📈 Temperature vs Air Quality (Monthly Correlation)",
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        fig4.update_layout(
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            font_color="#E2E8F0",
            title_font_color="#60A5FA",
            xaxis_title="Temperature (°C)",
            yaxis_title="Combined AQI",
        )
        st.plotly_chart(fig4, use_container_width=True)

# ==========================================================
# YEARLY ANALYSIS 
# ==========================================================
elif page == "Yearly Analysis":
    st.markdown("#### 📊 Yearly Climate Deep Analysis")

    # --- Country filter (from sidebar) ---
    selected_countries = st.session_state.get("selected_countries", [])
    if selected_countries:
        yearly_filtered = yearly_df[yearly_df["country"].isin(selected_countries)]
    else:
        yearly_filtered = yearly_df

    # --- Year selector (affects only KPIs) ---
    all_years = sorted(yearly_filtered["year"].unique())
    selected_year = st.selectbox(
        "Select Year for KPI Analysis",
        all_years,
        index=len(all_years) - 1,
        key="year_selector"
    )

    # --- KPI Data for Selected Year ---
    kpi_df = yearly_filtered[yearly_filtered["year"] == selected_year]

    # --- KPI SECTION ---
    avg_temp = kpi_df["temperature_celsius"].mean()
    avg_aqi = kpi_df["air_quality_PM2.5"].mean()
    avg_humidity = kpi_df["humidity"].mean()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-container">
                <h3> Avg Temperature</h3>
                <p>{avg_temp:.2f} °C</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-container">
                <h3> Avg PM2.5 (Air Quality)</h3>
                <p>{avg_aqi:.2f}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-container">
                <h3> Avg Humidity</h3>
                <p>{avg_humidity:.2f}%</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --- Chart layout: 2x2 grid (Unchanged) ---
    r1c1, r1c2 = st.columns(2)
    r2c1, r2c2 = st.columns(2)

    # --- 1️⃣ Average Yearly Temperature Trend ---
    with r1c1:
        fig1 = px.line(
            yearly_filtered,
            x="year",
            y="temperature_celsius",
            color="country",
            markers=True,
            title="🌡️ Yearly Average Temperature Trend",
            color_discrete_sequence=px.colors.sequential.Blues,
        )
        fig1.update_layout(
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            font_color="#E2E8F0",
            title_font_color="#60A5FA",
            xaxis_title="Year",
            yaxis_title="Temperature (°C)",
        )
        st.plotly_chart(fig1, use_container_width=True)

    # --- 2️⃣ Yearly Average Humidity Trend ---
    with r1c2:
        fig2 = px.line(
            yearly_filtered,
            x="year",
            y="humidity",
            color="country",
            markers=True,
            title="💧 Yearly Humidity Trends",
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        fig2.update_layout(
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            font_color="#E2E8F0",
            title_font_color="#60A5FA",
            xaxis_title="Year",
            yaxis_title="Humidity (%)",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --- 3️⃣ Yearly Air Quality Comparison ---
    with r2c1:
        fig3 = px.bar(
            yearly_filtered,
            x="year",
            y=["air_quality_PM2.5", "air_quality_PM10"],
            barmode="group",
            title="🧪 Yearly Air Quality Comparison (PM2.5 vs PM10)",
            color_discrete_sequence=px.colors.sequential.Blues,
        )
        fig3.update_layout(
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            font_color="#E2E8F0",
            title_font_color="#60A5FA",
            xaxis_title="Year",
            yaxis_title="Concentration (µg/m³)",
        )
        st.plotly_chart(fig3, use_container_width=True)

    # --- 4️⃣ Temperature vs Humidity Correlation ---
    with r2c2:
        fig4 = px.scatter(
            yearly_filtered,
            x="temperature_celsius",
            y="humidity",
            color="country",
            trendline="ols",
            title="📈 Temperature vs Humidity (Yearly Correlation)",
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        fig4.update_layout(
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            font_color="#E2E8F0",
            title_font_color="#60A5FA",
            xaxis_title="Temperature (°C)",
            yaxis_title="Humidity (%)",
        )
        st.plotly_chart(fig4, use_container_width=True)




# ==========================================================
# SEASONAL PATTERNS (4 VISUALS)
# ==========================================================
elif page == "Seasonal Patterns":
    st.markdown("---")
    st.markdown("#### 🌦️ Seasonal Climate Deep Analysis")

    # --- Data Prep ---
    seasonal_df["avg_aqi"] = seasonal_df[
        ["air_quality_Carbon_Monoxide", "air_quality_Ozone",
         "air_quality_PM2.5", "air_quality_PM10"]
    ].mean(axis=1)

    # Create a simple normalized "Seasonal Climate Index"
    seasonal_df["climate_index"] = (
        normalize(seasonal_df["temperature_celsius"]) * 0.4 +
        normalize(seasonal_df["avg_aqi"]) * 0.4 +
        normalize(seasonal_df["wind_kph"]) * 0.2
    )

    # --- Row 1: Two Visuals Side by Side ---
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        fig = px.box(
            seasonal_df,
            x="season",
            y="temperature_celsius",
            color="country",
            title="Seasonal Temperature Variation",
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#E2E8F0")
        )
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        fig = px.bar(
            seasonal_df,
            x="season",
            y="wind_kph",
            color="country",
            barmode="group",
            title="Seasonal Wind Speed Comparison",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#E2E8F0")
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Row 2: Two Visuals Side by Side ---
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        # Stacked Air Quality Components
        air_components = seasonal_df.groupby(["season", "country"])[
            ["air_quality_PM2.5", "air_quality_PM10", "air_quality_Ozone"]
        ].mean().reset_index()

        fig = px.bar(
            air_components,
            x="season",
            y=["air_quality_PM2.5", "air_quality_PM10", "air_quality_Ozone"],
            color_discrete_sequence=px.colors.sequential.Blues,
            title="Seasonal Air Quality Composition (PM2.5, PM10, Ozone)",
        )
        fig.update_layout(
            barmode="stack",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#E2E8F0")
        )
        st.plotly_chart(fig, use_container_width=True)

    with r2c2:
        # Heatmap for Climate Index
        heatmap_df = seasonal_df.groupby(["country", "season"])["climate_index"].mean().reset_index()
        fig = px.density_heatmap(
            heatmap_df,
            x="season",
            y="country",
            z="climate_index",
            color_continuous_scale="Blues",
            title="Seasonal Climate Index Heatmap",
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#E2E8F0")
        )
        st.plotly_chart(fig, use_container_width=True)


# ==========================================================
# 🌐 GLOBAL INSIGHTS
# ==========================================================
elif page == "Global Insights":
    st.markdown("---")
    st.markdown("#### 🌐 Global Climate Insights & Correlations")

    # --- Data Prep ---
    df = daily_df.copy()

    df["avg_aqi"] = df[
        ["air_quality_Carbon_Monoxide", "air_quality_Ozone",
         "air_quality_PM2.5", "air_quality_PM10"]
    ].mean(axis=1)

    def normalize(series):
        return (series - series.min()) / (series.max() - series.min())

    df["climate_index"] = (
        normalize(df["temperature_celsius"]) * 0.4 +
        normalize(df["avg_aqi"]) * 0.4 +
        normalize(df["wind_kph"]) * 0.2
    )

    # --- Row 1: Country-level Insights ---
    col1, col2 = st.columns(2)

    with col1:
        country_index = df.groupby("country")["climate_index"].mean().reset_index()
        fig = px.bar(
            country_index.sort_values("climate_index", ascending=False),
            x="country", y="climate_index",
            color="climate_index",
            color_continuous_scale="Blues",
            title="🌍 Global Climate Index Ranking"
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E2E8F0"),
            title_x=0.3
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            df,
            x="temperature_celsius",
            y="avg_aqi",
            color="country",
            size="wind_kph",
            title="🌡️ Temperature vs Air Quality (Correlation)",
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E2E8F0"),
            title_x=0.3
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Row 2: Trend Analysis + Correlations ---
    col3, col4 = st.columns(2)

    with col3:
        avg_trends = df.groupby("country")[["wind_kph", "avg_aqi"]].mean().reset_index()
        fig = px.line(
            avg_trends.melt(id_vars="country", var_name="Metric", value_name="Value"),
            x="country",
            y="Value",
            color="Metric",
            title="💨 Average Wind Speed vs Air Quality (Global View)",
            markers=True,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E2E8F0"),
            title_x=0.3
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        corr_df = df[
            ["temperature_celsius", "wind_kph", "avg_aqi", "climate_index"]
        ].corr().round(2)
        fig = px.imshow(
            corr_df,
            text_auto=True,
            color_continuous_scale="Blues",
            title="🧩 Global Parameter Correlation Heatmap"
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E2E8F0"),
            title_x=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
