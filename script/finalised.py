


import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------- PAGE CONFIG ---------------------
st.set_page_config(
    page_title="🌍 Global Weather & Air Quality Dashboard",
    layout="wide",
    page_icon="☁"
)
st.title("🌦 Global Weather & Air Quality Interactive Dashboard")


# --------------------- STYLES ---------------------
st.markdown("""
<style>
/* MAIN PAGE BACKGROUND */
.block-container {
    background-color: #000000 !important;
    color: #FFFFFF !important;
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* HEADER / MAIN TITLE */
h1 {
    color: #FFA500 !important;
    text-align: center !important;
    font-weight: 800 !important;
    font-size: 2.9rem !important;
    margin-top: 1.5rem !important;   
    margin-bottom: 1.5rem !important;
    background-color: #111111 !important;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 3px 10px rgba(255,165,0,0.3);
}

/* SUB HEADINGS */
h2, h3, h4 {
    color: #00FFFF !important;
    font-weight: 700 !important;
    margin-bottom: 0.6rem !important;
}

/* SIDEBAR DESIGN */
[data-testid="stSidebar"] {
    background-color: #111111 !important;
    border-right: 2px solid #00FFFF;
    box-shadow: 2px 0px 6px rgba(0,255,255,0.1);
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;  
    font-weight: 600 !important;
}

/* SIDEBAR INPUT BOXES */
div[data-baseweb="select"], .stDateInput, .stMultiSelect, .stTextInput {
    background-color: #222222 !important;
    border-radius: 8px !important;
    border: 1.5px solid #00FFFF !important;
    color: #FFFFFF !important;  
}

/* METRICS SECTION */
[data-testid="stMetric"] {
    background-color: #111111 !important;
    border-radius: 12px;
    padding: 16px;
    margin: 6px;
    box-shadow: 0 2px 6px rgba(0,255,255,0.1);
    text-align: center !important;
}
[data-testid="stMetricLabel"] { color: #00FFFF !important; font-weight: 700 !important; font-size: 1.1rem !important;}
[data-testid="stMetricValue"] { color: #FFA500 !important; font-weight: 800 !important; font-size: 1.3rem !important;}

/* PLOTLY CHARTS */
.js-plotly-plot {
    border-radius: 10px;
    background-color: #111111 !important;
    padding: 10px !important;
    box-shadow: 0 2px 6px rgba(0,255,255,0.05);
}

/* All tab names */
div[role="tablist"] button[role="tab"] { color: #BBBBBB !important; font-weight: 700 !important; font-size: 1rem !important;}
div[role="tablist"] button[role="tab"][aria-selected="true"] { color: #FFA500 !important; }

</style>
""", unsafe_allow_html=True)

# --------------------- DATA LOAD ---------------------
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\Kashi\Desktop\climatescope-project\data\GlobalWeatherRepository_cleaned.csv")
    df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')
    df['Date'] = df['last_updated'].dt.date
    df['Hour'] = df['last_updated'].dt.hour
    df = df.dropna(subset=["latitude", "longitude"])
    df = df[df['last_updated'].dt.year.isin([2024, 2025])]
    return df

df = load_data()

# --------------------- SIDEBAR FILTERS ---------------------
st.sidebar.header("🔍 Filters")

# Country filter
if 'country' in df.columns:
    countries = sorted(df['country'].dropna().unique())
    select_all = st.sidebar.checkbox("Select All Countries", value=True)
    selected_countries = countries if select_all else st.sidebar.multiselect("Select Country", countries, default=countries[:3])
    df = df[df['country'].isin(selected_countries)]

# Year filter
years = sorted(df['last_updated'].dt.year.dropna().unique())
selected_years = st.sidebar.multiselect("Select Year", years, default=years)
df = df[df['last_updated'].dt.year.isin(selected_years)]

# Temperature range filter
temp_min, temp_max = float(df["temperature_celsius"].min()), float(df["temperature_celsius"].max())
temp_range = st.sidebar.slider("Select Temperature Range (°C)", temp_min, temp_max, (temp_min, temp_max))
df = df[(df["temperature_celsius"] >= temp_range[0]) & (df["temperature_celsius"] <= temp_range[1])]

# Variable selector
numeric_cols = df.select_dtypes(include=['float64','int64']).columns.tolist()
default_var = "temperature_celsius" if "temperature_celsius" in numeric_cols else numeric_cols[0]
selected_variable = st.sidebar.selectbox("Select variable to visualize", numeric_cols, index=numeric_cols.index(default_var))

# Raw data preview
if st.sidebar.checkbox("Show Raw Data"):
    st.subheader("Raw Data Preview")
    st.dataframe(df.head(100))

# Download filtered data
csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("Download Filtered Data (CSV)", csv, "filtered_weather_data.csv", "text/csv")

# --------------------- SUMMARY METRICS ---------------------
st.subheader("📊 Key Weather Statistics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("🌡 Avg Temperature (°C)", f"{df['temperature_celsius'].mean():.2f}")
col2.metric("💧 Avg Humidity (%)", f"{df['humidity'].mean():.2f}")
col3.metric("🌬 Avg Wind Speed (kph)", f"{df['wind_kph'].mean():.2f}")
col4.metric("📈 Avg Pressure (mb)", f"{df['pressure_mb'].mean():.2f}")

# --------------------- TABS ---------------------
tab_overview, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📌 Overview",
    "🌡 Temperature Trends",
    "🌫 Air Quality Analysis",
    "🌍 Geospatial Visualization",
    "📊 Correlation Heatmap",
    "⚠ Extreme Events",
    "🧭 Insights Summary"
])

# --------------------- TAB: PROJECT OVERVIEW ---------------------
with tab_overview:
    st.subheader("Project Overview")
    st.markdown("""
    *Purpose:* Visualize global weather & air quality trends interactively.  
    *Features:* Temperature, Humidity, Wind, Air Quality, Extreme Events, Correlation Analysis.  
    *Time Coverage:* 2024–2025, multiple countries & cities.
    """)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🌡 Temp Trends", "✅")
    col2.metric("💧 Humidity", "✅")
    col3.metric("💨 Wind", "✅")
    col4.metric("🌍 Geospatial", "✅")
    col5.metric("⚠ Extreme Events", "✅")

# --------------------- TAB 1: TEMPERATURE ---------------------
with tab1:
    st.subheader("📈 Temperature and Weather Trends")
    single_chart_type = st.selectbox("Select chart type for single variable", ["Line Chart", "Scatter Plot", "Bar Chart"])
    template_dark = "plotly_dark"
    if single_chart_type == "Line Chart":
        fig_temp = px.line(df, x="last_updated", y=selected_variable, template=template_dark,
                           title=f"{selected_variable.replace('_',' ').title()} Over Time", markers=True, color_discrete_sequence=["#FFA500"])
        st.plotly_chart(fig_temp, use_container_width=True)
    elif single_chart_type == "Scatter Plot":
        fig_temp = px.scatter(df, x="last_updated", y=selected_variable, template=template_dark,
                              title=f"{selected_variable.replace('_',' ').title()} Over Time (Scatter)", color_discrete_sequence=["#FFA500"])
        st.plotly_chart(fig_temp, use_container_width=True)
    elif single_chart_type == "Bar Chart":
        fig_temp = px.bar(df, x="last_updated", y=selected_variable, template=template_dark,
                          title=f"{selected_variable.replace('_',' ').title()} Over Time (Bar)", color_discrete_sequence=["#FFA500"])
        st.plotly_chart(fig_temp, use_container_width=True)

    st.markdown("#### Comparison of Multiple Variables")
    compare_chart_type = st.selectbox("Select chart type for comparison", ["Line Chart", "Scatter Plot"], key="compare_type")
    compare_vars = st.multiselect("Select variables to compare", numeric_cols, default=["temperature_celsius","humidity"], key="compare_vars")
    if compare_vars:
        if compare_chart_type == "Line Chart":
            fig_comp = px.line(df, x="last_updated", y=compare_vars, template=template_dark)
        else:
            fig_comp = px.scatter(df, x="last_updated", y=compare_vars, template=template_dark)
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.warning("Please select at least one variable for comparison.")

# --------------------- TAB 2: AIR QUALITY ---------------------
with tab2:
    st.subheader("💨 Air Quality Metrics")
    air_cols = [c for c in df.columns if "air_quality" in c.lower()]
    if air_cols:
        selected_aq = st.selectbox("Select Air Quality Parameter", air_cols)
        fig_aq = px.line(df, x="last_updated", y=selected_aq, template=template_dark,
                         color_discrete_sequence=["#00FFFF"])
        st.plotly_chart(fig_aq, use_container_width=True)
        st.markdown("#### Compare Multiple Air Quality Components")
        aq_compare = st.multiselect("Select components", air_cols,
                                    default=["air_quality_PM2.5","air_quality_PM10"] if "air_quality_PM2.5" in air_cols else air_cols[:2])
        if aq_compare:
            fig_compare = px.line(df, x="last_updated", y=aq_compare, template=template_dark)
            st.plotly_chart(fig_compare, use_container_width=True)
    else:
        st.warning("No air quality columns found in dataset.")

# --------------------- TAB 3: GEOSPATIAL ---------------------
with tab3:
    st.subheader("🗺 Global Temperature Distribution")
    if "latitude" in df.columns and "longitude" in df.columns:
        fig_map = px.scatter_geo(df, lat="latitude", lon="longitude", color="temperature_celsius",
                                 size="humidity", template=template_dark, projection="natural earth",
                                 color_continuous_scale="RdYlBu_r", hover_data=["pressure_mb","visibility_km"])
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Latitude/Longitude columns not found in dataset.")

# --------------------- TAB 4: CORRELATION ---------------------
with tab4:
    st.subheader("📊 Correlation Between Weather & Air Quality Variables")
    if numeric_cols:
        selected_corr_vars = st.multiselect("Select variables for correlation heatmap", numeric_cols, default=numeric_cols[:8])
        if selected_corr_vars:
            corr = df[selected_corr_vars].corr()
            fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", template=template_dark, title="Correlation Heatmap", aspect="auto")
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.warning("Please select at least one variable.")
    else:
        st.warning("No numeric columns available for correlation.")
# ------------------ TAB 5: EXTREME EVENTS ------------------
with tab5:
    st.subheader("⚠ Extreme Weather & Air Quality Events Detector")

    template_dark = "plotly_dark"  # Dark theme for charts

    # 1️⃣ Let user select variable to detect extremes
    event_var_options = []
    if "temperature_celsius" in df.columns:
        event_var_options.append("temperature_celsius")
    if "wind_kph" in df.columns:
        event_var_options.append("wind_kph")
    # Include air quality columns
    air_cols = [c for c in df.columns if "air_quality" in c.lower()]
    event_var_options.extend(air_cols)

    selected_event_var = st.selectbox("Select variable to detect extreme events", event_var_options)

    # 2️⃣ Let user choose extreme threshold (percentile)
    default_threshold = df[selected_event_var].quantile(0.95)
    threshold = st.slider(
        f"Set threshold for extreme {selected_event_var}", 
        min_value=float(df[selected_event_var].min()),
        max_value=float(df[selected_event_var].max()),
        value=float(default_threshold)
    )

    # 3️⃣ Filter extreme events
    extreme_df = df[df[selected_event_var] > threshold]
    st.markdown(
        f"🔥 Found {len(extreme_df)} extreme records above {threshold:.2f} for {selected_event_var}"
    )

    # 4️⃣ Select columns to display dynamically
    cols_to_show = [col for col in ["country", "city", "Date", selected_event_var, "humidity", "wind_kph", "pressure_mb", "last_updated"] 
                    if col in extreme_df.columns]
    st.dataframe(extreme_df[cols_to_show])

    # 5️⃣ Plot extreme events over time
    if not extreme_df.empty:
        color_col = "country" if "country" in extreme_df.columns else None
        hover_cols = [col for col in ["humidity", "wind_kph", "pressure_mb"] if col in extreme_df.columns]
        fig_extreme = px.scatter(
            extreme_df,
            x="last_updated",
            y=selected_event_var,
            color=color_col,
            title=f"Extreme {selected_event_var} Events Over Time",
            template=template_dark,
            hover_data=hover_cols,
            size=selected_event_var,
            color_continuous_scale="Turbo"
        )
        st.plotly_chart(fig_extreme, use_container_width=True)
    else:
        st.warning(f"No extreme events detected for {selected_event_var} above the selected threshold.")

# ------------------ TAB 6: INSIGHTS & CONCLUSION ------------------
with tab6:
    st.subheader("🧭 Key Insights and Findings")
    st.markdown("""
    <div style='color:white; font-size:1rem; line-height:1.5'>
    <strong>🌡 Temperature:</strong><br>
    - Daily fluctuations visible; lower humidity corresponds with temperature peaks.<br><br>

    <strong>💨 Air Quality:</strong><br>
    - PM2.5 and PM10 levels strongly correlated, reflecting particulate density.<br>
    - CO and NO₂ rise when visibility drops.<br><br>

    <strong>🌍 Geospatial Patterns:</strong><br>
    - Coastal areas show moderate temperatures and high humidity.<br>
    - Air quality varies widely across locations.<br><br>

    <strong>📈 Correlation:</strong><br>
    - Temperature inversely correlated with humidity.<br>
    - PM2.5 ↔ PM10 correlation > 0.9.<br>
    - Wind speed helps disperse pollutants.<br><br>

    <strong>✅ Conclusion:</strong><br>
    - Weather and air quality are interlinked; this dashboard shows their dynamic interaction in real time.
    </div>
    """, unsafe_allow_html=True)