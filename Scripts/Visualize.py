# app_streamlit.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from Analysis import (
    load_data, descriptive_stats, country_aggregates, correlation_matrix,
    monthly_trends, detect_extreme_events, region_comparisons
)

st.set_page_config(page_title="🌦️ ClimateScope — Advanced Weather Dashboard", layout="wide")

DATA_PATH = "../data/GlobalWeatherRepository_cleaned.csv"

@st.cache_data
def get_data():
    return load_data(DATA_PATH)

df = get_data()

# --- Sidebar ---
with st.sidebar:
    st.header("Filters")
    countries = sorted(df["country"].dropna().unique().tolist())
    selected_country = st.multiselect("Country", countries, default=countries[:3])

    date_min, date_max = df["date"].min(), df["date"].max()
    selected_dates = st.date_input("Date range", (date_min, date_max))

    metric_group = st.selectbox("Metric Group", [
        "Temperature",
        "Humidity & Visibility",
        "Wind",
        "Precipitation & Pressure",
        "Air Quality",
        "Regional / Geographical",
        "Temporal / Seasonal",
        "Extreme Events"
    ])

# --- Apply Filters ---
dff = df.copy()
if selected_country:
    dff = dff[dff["country"].isin(selected_country)]
if selected_dates and isinstance(selected_dates, tuple):
    start, end = selected_dates
    dff = dff[(dff["date"] >= pd.to_datetime(start)) & (dff["date"] <= pd.to_datetime(end))]

# --- Dashboard Header ---
st.title("🌤️ ClimateScope — Interactive Global Weather & Air Quality Dashboard")
st.caption("Explore live climate analytics: trends, correlations, and regional comparisons.")

# --- Top-level metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", f"{dff.shape[0]:,}")
col2.metric("Countries", f"{dff['country'].nunique()}")
col3.metric("Locations", f"{dff['location_name'].nunique()}")

st.markdown("---")

# --- Metric Group Views ---
if metric_group == "Temperature":
    st.subheader("🌡️ Temperature Metrics")
    cols = ["temperature_celsius", "feels_like_celsius"]
    available = [c for c in cols if c in dff.columns]
    if not available:
        st.warning("Temperature columns not found.")
    else:
        # Line Chart
        st.write("**Temperature Trend Over Time**")
        fig, ax = plt.subplots(figsize=(10,4))
        for c in available:
            ax.plot(dff["date"], dff[c], label=c)
        ax.legend(); ax.set_xlabel("Date"); ax.set_ylabel("°C")
        st.pyplot(fig)

        # Histogram + KDE
        st.write("**Temperature Distribution**")
        fig2, ax2 = plt.subplots(figsize=(8,4))
        sns.histplot(dff["temperature_celsius"], kde=True, ax=ax2, color="coral")
        st.pyplot(fig2)

        # Boxplot by month
        dff["month"] = dff["date"].dt.month
        fig3, ax3 = plt.subplots(figsize=(8,4))
        sns.boxplot(
    x="month",
    y="temperature_celsius",
    hue="month",
    data=dff,
    palette="coolwarm",
    legend=False,
    ax=ax3
)

        ax3.set_title("Monthly Temperature Distribution")
        st.pyplot(fig3)

elif metric_group == "Humidity & Visibility":
    st.subheader("💧 Humidity & Visibility")
    if {"humidity","visibility_km","temperature_celsius"}.issubset(dff.columns):
        st.write("**Humidity vs Temperature**")
        fig, ax = plt.subplots(figsize=(6,4))
        sns.scatterplot(data=dff, x="humidity", y="temperature_celsius", alpha=0.5, color="teal")
        st.pyplot(fig)

        st.write("**Visibility Trend Over Time**")
        fig2, ax2 = plt.subplots(figsize=(10,4))
        ax2.plot(dff["date"], dff["visibility_km"], color="orange")
        ax2.set_ylabel("Visibility (km)")
        st.pyplot(fig2)

        st.write("**Humidity–Visibility–Temperature Correlation Heatmap**")
        fig3, ax3 = plt.subplots(figsize=(5,4))
        corr = dff[["humidity","visibility_km","temperature_celsius"]].corr()
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax3)
        st.pyplot(fig3)

elif metric_group == "Wind":
    st.subheader("🌬️ Wind Metrics")
    if "wind_kph" in dff.columns:
        st.write("**Wind Speed Trend**")
        fig, ax = plt.subplots(figsize=(10,4))
        ax.plot(dff["date"], dff["wind_kph"], label="wind_kph", color="blue")
        if "gust_kph" in dff.columns:
            ax.plot(dff["date"], dff["gust_kph"], label="gust_kph", color="red", alpha=0.6)
        ax.legend(); st.pyplot(fig)

        if "gust_kph" in dff.columns and "precip_mm" in dff.columns:
            st.write("**Gusts vs Precipitation**")
            fig2, ax2 = plt.subplots(figsize=(6,4))
            sns.scatterplot(data=dff, x="gust_kph", y="precip_mm", color="purple")
            st.pyplot(fig2)
    else:
        st.warning("Wind data unavailable.")

elif metric_group == "Precipitation & Pressure":
    st.subheader("🌧️ Precipitation & Pressure")
    if "date" in dff.columns:
        dff["month"] = dff["date"].dt.to_period("M")
        monthly = dff.groupby("month")[["precip_mm","pressure_mb"]].mean().reset_index()

        if "precip_mm" in monthly.columns:
            st.write("**Average Monthly Precipitation**")
            fig, ax = plt.subplots(figsize=(8,4))
            sns.barplot(x=monthly["month"].astype(str), y="precip_mm", data=monthly, color="skyblue")
            ax.set_xticks(ax.get_xticks())
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

            st.pyplot(fig)

        if "pressure_mb" in dff.columns:
            st.write("**Pressure Trend Over Time**")
            fig2, ax2 = plt.subplots(figsize=(10,4))
            ax2.plot(dff["date"], dff["pressure_mb"], color="brown")
            ax2.set_ylabel("Pressure (mb)")
            st.pyplot(fig2)

            st.write("**Pressure vs Precipitation**")
            if "precip_mm" in dff.columns:
                fig3, ax3 = plt.subplots(figsize=(6,4))
                sns.scatterplot(data=dff, x="pressure_mb", y="precip_mm", color="gray")
                st.pyplot(fig3)
    else:
        st.warning("Date column missing for monthly aggregation.")

elif metric_group == "Air Quality":
    st.subheader("🌫️ Air Quality Metrics")
    aq_cols = [c for c in ["air_quality_PM2.5","air_quality_PM10","air_quality_us-epa-index"] if c in dff.columns]
    if aq_cols:
        st.write("**Air Quality Trend Over Time**")
        fig, ax = plt.subplots(figsize=(10,4))
        for c in aq_cols:
            ax.plot(dff["date"], dff[c], label=c)
        ax.legend(); st.pyplot(fig)

        st.write("**Pollutant Correlation Heatmap**")
        fig2, ax2 = plt.subplots(figsize=(5,4))
        sns.heatmap(dff[aq_cols].corr(), annot=True, cmap="YlOrRd", ax=ax2)
        st.pyplot(fig2)

        st.write("**Regional AQI Comparison**")
        if "country" in dff.columns:
            agg = dff.groupby("country")["air_quality_us-epa-index"].mean().sort_values(ascending=False).head(20)
            st.bar_chart(agg)
    else:
        st.warning("Air quality columns unavailable.")

elif metric_group == "Regional / Geographical":
    import plotly.express as px

    st.subheader("🗺️ Regional & Geographical Analysis")

    # Compute country-level aggregates
    agg = country_aggregates(dff)
    if not agg.empty:
        st.write("**Country-Level Climate Summary**")
        st.dataframe(agg)

        # Pick a representative metric for map coloring
        metric_choice = st.selectbox(
            "Select metric for map color",
            ["temperature_celsius", "humidity", "air_quality_us-epa-index", "pressure_mb", "precip_mm"]
        )

        if metric_choice in dff.columns:
            # Country-level mean metric
            country_means = (
                dff.groupby("country")[metric_choice]
                .mean()
                .reset_index()
                .sort_values(metric_choice, ascending=False)
            )

            st.write(f"**Mean {metric_choice} by Country**")
            fig_choro = px.choropleth(
                country_means,
                locations="country",
                locationmode="country names",
                color=metric_choice,
                color_continuous_scale="RdYlBu_r",
                title=f"Average {metric_choice} by Country",
                projection="natural earth",
                height=650,
            )
            fig_choro.update_geos(showcountries=True, showframe=True)

            st.plotly_chart(fig_choro, use_container_width=True)
        else:
            st.warning(f"Column '{metric_choice}' not found in dataset.")
    else:
        st.warning("No country data available for aggregation.")

    # --- Location-level map with color-coded points ---
    # if {"latitude", "longitude"}.issubset(dff.columns):
    #     st.write("**Location-Level Map (Colored by Temperature or AQI)**")
    #     color_col = st.selectbox(
    #         "Select parameter for point color",
    #         [c for c in ["temperature_celsius", "air_quality_PM2.5", "humidity"] if c in dff.columns],
    #         index=0
    #     )

    #     fig_map = px.scatter_mapbox(
    #         dff,
    #         lat="latitude",
    #         lon="longitude",
    #         color=color_col,
    #         hover_name="location_name" if "location_name" in dff.columns else None,
    #         hover_data=["country", color_col],
    #         color_continuous_scale="Turbo",
    #         zoom=1.2,
    #         height=500
    #     )
    #     fig_map.update_layout(mapbox_style="open-street-map", title=f"{color_col} by Location")
    #     st.plotly_chart(fig_map, use_container_width=True)
    # else:
    #     st.warning("No geographic coordinates found in dataset.")


elif metric_group == "Temporal / Seasonal":
    st.subheader("📅 Temporal / Seasonal Patterns")
    monthly, figm = monthly_trends(dff)
    if not monthly.empty:
        st.pyplot(figm)
        st.line_chart(monthly[["temperature_celsius","humidity","air_quality_PM2.5"]].dropna(how='all', axis=1))
    else:
        st.warning("Insufficient date data for temporal analysis.")

elif metric_group == "Extreme Events":
    st.subheader("⚠️ Extreme Weather Events")

    thresholds, ext_events, summary = detect_extreme_events(dff)

    st.write("### Thresholds used to flag extremes:")
    st.json(thresholds)

    if not ext_events.empty:
        # Columns to display
        display_cols = ["date", "country", "location_name", "temperature_celsius",
                        "wind_kph", "precip_mm", "visibility_km", "extreme_types"]
        df_display = ext_events[display_cols].copy()

        # Color palette (Low Visibility is transparent)
        color_map = {
            "High Temp": "#FF6B6B",       # Soft Red
            "High Wind": "#4D96FF",       # Gentle Blue
            "Heavy Precip": "#4CAF50",    # Soft Green
            "Low Visibility": ""           # Transparent / no highlight
        }

        # --- Display legend above table ---
        legend_html = """
        <b>Legend (Row Color):</b> 
        <span style='background-color:#FF6B6B;padding:2px 8px;margin-right:5px;'>High Temp</span>
        <span style='background-color:#4D96FF;padding:2px 8px;margin-right:5px;'>High Wind</span>
        <span style='background-color:#4CAF50;padding:2px 8px;margin-right:5px;'>Heavy Precip</span>
        <span style='background-color:transparent;padding:2px 8px;margin-right:5px;'>Low Visibility</span>
        """
        st.markdown(legend_html, unsafe_allow_html=True)

        # Highlight rows based on extreme type
        def highlight_extremes(row):
            if row["extreme_types"]:
                for key in color_map:
                    if key.lower() in row["extreme_types"].lower() and color_map[key]:
                        return ['background-color: ' + color_map[key]] * len(row)
            return [''] * len(row)

        st.write("### Extreme Events Table (highlighted by type)")
        st.dataframe(df_display.style.apply(highlight_extremes, axis=1))
    else:
        st.info("No extreme events detected in this selection.")



# --- Footer ---
st.markdown("---")
