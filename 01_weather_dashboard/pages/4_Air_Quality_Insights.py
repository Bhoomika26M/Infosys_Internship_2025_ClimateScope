# 3_AirQuality_Insights.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import pycountry_convert as pc



# ===============================
# 🎨 Styled Sidebar Navigation
# ===============================
st.markdown(
    """
    <style>
    /* Sidebar background with subtle gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #000000, #1A1A1A);
        color: #F2F2F2;
        box-shadow: 0 0 15px rgba(255,0,0,0.2);
    }

    /* NAV header - bold red */
    [data-testid="stSidebarNav"]::before {
        content: "🧭 NAVIGATION";
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #FF3B3B !important;
        margin-bottom: 2px;
        display: block;
        margin: 6px 8px 4px 8px !important;
        letter-spacing: 0.6px;
    }

    /* Remove default top spacing from nav list */
    [data-testid="stSidebarNav"] ul:first-of-type {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Hide original app label */
    [data-testid="stSidebarNav"] ul li:first-child div {
        visibility: hidden !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
    }


    /* Nav items */
    [data-testid="stSidebarNav"] ul li div {
        margin: 3px 6px !important;
        padding: 6px 10px !important;
        border-radius: 8px;
        font-size: 15.5px !important;
        background: rgba(255,255,255,0.02) !important;
        color: #F2F2F2 !important;
    }

    /* Reduce list container padding */
    [data-testid="stSidebarNav"] ul {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Hover + active states */
    [data-testid="stSidebarNav"] ul li div:hover {
        background: rgba(255,59,59,0.15) !important;
        color: #FF6666 !important;
        transform: translateX(4px);
    }
    [data-testid="stSidebarNav"] ul li div[data-selected="true"] {
        background: rgba(255,59,59,0.2) !important;
        border-left: 3px solid #FF3B3B !important;
        color: #FF3B3B !important;
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="Global Weather Tracker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔧 Hide Streamlit top-right menu & deploy button
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def styled_header(text, level=2, color="rgb(255, 75, 75)", size=32):
    html = f"""
        <h{level} style='
            color: {color};
            font-size: {size}px;
            font-weight: 600;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
            font-family: "Segoe UI", sans-serif;
            margin-top: 10px;
            margin-bottom: 10px;
        '>
            {text}
        </h{level}>
    """
    st.markdown(html, unsafe_allow_html=True)



st.set_page_config(page_title="Air Quality Insights", layout="wide")


hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def styled_header(text, level=2, color="rgb(255, 75, 75)", size=30):
    html = f"""
        <h{level} style='
            color: {color};
            font-size: {size}px;
            font-weight: 600;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
            font-family: "Segoe UI", sans-serif;
            margin-top: 10px;
            margin-bottom: 10px;
        '>
            {text}
        </h{level}>
    """
    st.markdown(html, unsafe_allow_html=True)


# ============================
# Load Data
# ============================
@st.cache_data
def load_data():
    df = pd.read_csv("../data/processed/processed_weather_data.csv", parse_dates=["last_updated"])
    df.columns = [col.strip() for col in df.columns]

    # --- Add continent column dynamically ---
    if 'country' in df.columns:
        def get_continent(country_name):
            try:
                country_alpha2 = pc.country_name_to_country_alpha2(country_name)
                continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
                continent_map = {
                    'AF': 'Africa',
                    'AS': 'Asia',
                    'EU': 'Europe',
                    'NA': 'North America',
                    'OC': 'Oceania',
                    'SA': 'South America',
                    'AN': 'Antarctica'
                }
                return continent_map.get(continent_code, 'Unknown')
            except:
                return 'Unknown'
        df['continent'] = df['country'].apply(get_continent)
    else:
        df['continent'] = 'Unknown'

    return df


df = load_data()

# ============================
# Detect User Country and Set Defaults
# ============================
def get_user_country_and_continent():
    try:
        ip_info = requests.get('https://ipinfo.io').json()
        country_code = ip_info.get('country', None)
        if country_code:
            country_name = pc.country_alpha2_to_country_name(country_code)
            continent_code = pc.country_alpha2_to_continent_code(country_code)
            continent_map = {
                'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe', 'NA': 'North America',
                'OC': 'Oceania', 'SA': 'South America', 'AN': 'Antarctica'
            }
            continent_name = continent_map.get(continent_code, 'Unknown')
            return country_name, continent_name
    except:
        pass
    return "India", "Asia"  # fallback

default_country, default_continent = get_user_country_and_continent()

# ============================
# Sidebar Filters (Smart Defaults + Dynamic Select All)
# ============================
st.sidebar.header("📍 Global Geographic Filters")

# --- Continent ---
continents = sorted(df['continent'].unique())
select_all_cont = st.sidebar.checkbox("Select All Continents", value=False)
if select_all_cont:
    selected_continents = continents
else:
    selected_continents = st.sidebar.multiselect(
        "Select Continent(s)",
        options=continents,
        default=[default_continent] if default_continent in continents else [continents[0]]
    )

# --- Countries ---
countries_in_selected_cont = sorted(df[df['continent'].isin(selected_continents)]['country'].unique())
select_all_countries = st.sidebar.checkbox("Select All Countries", value=False)
if select_all_countries:
    selected_countries = countries_in_selected_cont
else:
    selected_countries = st.sidebar.multiselect(
        "Select Country(s)",
        options=countries_in_selected_cont,
        default=[default_country] if default_country in countries_in_selected_cont else [countries_in_selected_cont[0]]
    )

# --- Locations ---
locations_in_selected_countries = sorted(df[df['country'].isin(selected_countries)]['location_name'].unique())
select_all_locations = st.sidebar.checkbox("Select All Locations", value=True)
if select_all_locations:
    selected_locations = locations_in_selected_countries
else:
    selected_locations = st.sidebar.multiselect(
        "Select Location(s)",
        options=locations_in_selected_countries,
        default=locations_in_selected_countries  # all initially selected for convenience
    )

# AQI filter
aqi_options = {
    1: 'Good (1)', 2: 'Moderate (2)', 3: 'Unhealthy for Sensitive Groups (3)',
    4: 'Unhealthy (4)', 5: 'Very Unhealthy (5)', 6: 'Hazardous (6)'
}
selected_aqi_level = st.sidebar.select_slider(
    "Max Air Quality Index (US EPA)",
    options=list(aqi_options.keys()),
    value=6,
    format_func=lambda x: aqi_options[x]
)

# PM2.5 & PM10 range sliders
pm2_5_range = st.sidebar.slider("PM2.5 Range (µg/m³)", int(df['air_quality_PM2.5'].min()), int(df['air_quality_PM2.5'].max()), (int(df['air_quality_PM2.5'].min()), int(df['air_quality_PM2.5'].max())))
pm10_range = st.sidebar.slider("PM10 Range (µg/m³)", int(df['air_quality_PM10'].min()), int(df['air_quality_PM10'].max()), (int(df['air_quality_PM10'].min()), int(df['air_quality_PM10'].max())))

# ============================
# Filter Data
# ============================
df_filtered = df[
    (df['continent'].isin(selected_continents)) &
    (df['country'].isin(selected_countries)) &
    (df['location_name'].isin(selected_locations)) &
    (df['air_quality_us-epa-index'] <= selected_aqi_level) &
    (df['air_quality_PM2.5'] >= pm2_5_range[0]) & (df['air_quality_PM2.5'] <= pm2_5_range[1]) &
    (df['air_quality_PM10'] >= pm10_range[0]) & (df['air_quality_PM10'] <= pm10_range[1])
]

if df_filtered.empty:
    st.warning("No data found for selected filters.")
    st.stop()




# ============================
# PM2.5 and PM10 Value Ranges by Air Quality Category
# ============================
#st.title("🌬️ Air Quality Insights")
st.markdown("""
    <h1 style='text-align: center; color: #FF4B4B; font-size: 48px; font-family: "Segoe UI", sans-serif;margin-top: -50px;'>
        🌬️ Air Quality Insights
    </h1>
""", unsafe_allow_html=True)

st.markdown("""<h6 style='
      font-size: 16px;
      font-weight: 400;
      color: #A0A0A0;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
      font-family: "Segoe UI", sans-serif;
      line-height: 1.6;
      margin: 0 auto;
      max-width: 100%;
        '>
AQI (Air Quality Index) is a standardized measure used to indicate how clean or polluted the air is, and what associated health effects might be of concern.
AQI is calculated based on the levels of six major pollutants: PM2.5 (fine particulate matter), PM10 (coarse particulate matter), Carbon monoxide (CO), Sulfur dioxide (SO₂), Nitrogen dioxide (NO₂), Ground-level ozone (O₃)
</h6>""", unsafe_allow_html=True)

styled_header("PM2.5 and PM10 Value Ranges by Air Quality Category")
st.markdown("""<h6 style=
            'font-size: 16px;
            font-weight: 200;
            color: #A0A0A0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            font-family: "Segoe UI", sans-serif;
            margin-bottom: 20px;
        '>
These ranges are based on India's National Air Quality Index (NAQI), which is also aligned with global standards.
</h6>""", unsafe_allow_html=True)


naqi_ranges = [
    {"AQI Category": "Good", "PM2.5 (µg/m³)": "0 – 30", "PM10 (µg/m³)": "0 – 50", 
     "Health Impact": "Minimal impact"},
    {"AQI Category": "Satisfactory", "PM2.5 (µg/m³)": "31 – 60", "PM10 (µg/m³)": "51 – 100", 
     "Health Impact": "Minor breathing discomfort to sensitive people"},
    {"AQI Category": "Moderately Polluted", "PM2.5 (µg/m³)": "61 – 90", "PM10 (µg/m³)": "101 – 250", 
     "Health Impact": "Breathing discomfort to people with lung disease"},
    {"AQI Category": "Poor", "PM2.5 (µg/m³)": "91 – 120", "PM10 (µg/m³)": "251 – 350", 
     "Health Impact": "Breathing discomfort on prolonged exposure"},
    {"AQI Category": "Very Poor", "PM2.5 (µg/m³)": "121 – 250", "PM10 (µg/m³)": "351 – 430", 
     "Health Impact": "Respiratory illness on prolonged exposure"},
    {"AQI Category": "Severe", "PM2.5 (µg/m³)": ">250", "PM10 (µg/m³)": ">430", 
     "Health Impact": "Serious health impacts, even on healthy individuals"}
]

naqi_df = pd.DataFrame(naqi_ranges)

# Define header style
header_style = {
    'selector': 'th',
    'props': [('background-color', '#2E8B57'),  # Sea green
              ('color', 'white'),
              ('font-size', '16px'),
              ('font-weight', 'bold'),
              ('text-align', 'center')]
}

# Apply styles
styled_df = naqi_df.style.set_table_styles([header_style])

# Display with styling
st.write(styled_df)

#st.table(naqi_df)

st.markdown("""
<style>
    .hover-link {
        color: #00bfff;
        text-decoration: none;
        margin-right: 20px;
        font-size: 16px;
    }
    .hover-link:hover {
        color: #ff6347;  /* Tomato red on hover */
        text-decoration: underline;
    }
</style>

<div style='display: flex; gap: 20px; flex-wrap: wrap; padding-bottom: 16px'>SOURCES: 
    <a class='hover-link' href='https://www.airquality.cpcb.gov.in/ccr_docs/About_AQI.pdf' target='_blank'>CPCB AQI</a>
    <a class='hover-link' href='https://safar.tropmet.res.in/AQI-47-12-Details' target='_blank'>SAFAR India</a>
    <a class='hover-link' href='https://smartairfilters.com/en/blog/global-air-quality-standards-pm2-5-pm10/' target='_blank'>Smart Air Standards</a>
</div>
""", unsafe_allow_html=True)



# ============================
# KPI Metrics Table with AQI Category Filter
# ============================
styled_header("Key Metrics for Selected Locations")

# Define NAQI Ranges
naqi_ranges = [
    {"AQI Category": "Good", "PM2.5_min": 0, "PM2.5_max": 30, "PM10_min": 0, "PM10_max": 50, "Color": "#2ecc71"},
    {"AQI Category": "Satisfactory", "PM2.5_min": 31, "PM2.5_max": 60, "PM10_min": 51, "PM10_max": 100, "Color": "#f1c40f"},
    {"AQI Category": "Moderately Polluted", "PM2.5_min": 61, "PM2.5_max": 90, "PM10_min": 101, "PM10_max": 250, "Color": "#e67e22"},
    {"AQI Category": "Poor", "PM2.5_min": 91, "PM2.5_max": 120, "PM10_min": 251, "PM10_max": 350, "Color": "#e74c3c"},
    {"AQI Category": "Very Poor", "PM2.5_min": 121, "PM2.5_max": 250, "PM10_min": 351, "PM10_max": 430, "Color": "#8e44ad"},
    {"AQI Category": "Severe", "PM2.5_min": 251, "PM2.5_max": float('inf'), "PM10_min": 431, "PM10_max": float('inf'), "Color": "#7f0000"},
]

# Helper function to classify AQI Category
def get_aqi_category(pm25, pm10):
    for r in naqi_ranges:
        if r["PM2.5_min"] <= pm25 <= r["PM2.5_max"] or r["PM10_min"] <= pm10 <= r["PM10_max"]:
            return r["AQI Category"], r["Color"]
    return "Unknown", "#95a5a6"  # grey for unknown

# AQI Category filter
categories = ["All"] + [r["AQI Category"] for r in naqi_ranges]
status_filter = st.radio("Filter by AQI Category:", categories, horizontal=True)

# Prepare KPI table
metrics_list = []
for loc in selected_locations:
    loc_df = df_filtered[df_filtered['location_name'] == loc]
    avg_aqi = loc_df['air_quality_us-epa-index'].mean()
    avg_pm25 = loc_df['air_quality_PM2.5'].mean()
    avg_pm10 = loc_df['air_quality_PM10'].mean()
    avg_humidity = loc_df['humidity'].mean()
    lat = loc_df['latitude'].mean() if 'latitude' in loc_df.columns else None
    lon = loc_df['longitude'].mean() if 'longitude' in loc_df.columns else None

    aqi_category, color = get_aqi_category(avg_pm25, avg_pm10)

    # Apply filter
    if status_filter == "All" or status_filter == aqi_category:
        metrics_list.append({
            "Location": loc,
            "Avg AQI": f"{avg_aqi:.2f}",
            "PM2.5 (µg/m³)": f"{avg_pm25:.2f}",
            "PM10 (µg/m³)": f"{avg_pm10:.2f}",
            "AQI Category": aqi_category,
            "Humidity (%)": f"{avg_humidity:.2f}",
            "Latitude": lat,
            "Longitude": lon,
            "Color": color
        })

metrics_df = pd.DataFrame(metrics_list)

# Display KPI Table
st.dataframe(
    metrics_df[["Location", "Avg AQI", "PM2.5 (µg/m³)", "PM10 (µg/m³)", "AQI Category", "Humidity (%)"]],
    use_container_width=True
)


# ============================
# Most Polluted & Least Polluted Locations
# ============================
styled_header("🌆 Most Polluted vs. Least Polluted Locations")

if not df_filtered.empty:
    # Compute mean AQI per location
    pollutant_summary = (
        df_filtered.groupby('location_name')[['air_quality_us-epa-index', 'air_quality_PM2.5', 'air_quality_PM10']]
        .mean()
        .reset_index()
    )
    pollutant_summary['Overall_Score'] = (
        pollutant_summary['air_quality_us-epa-index'] * 0.5 +
        pollutant_summary['air_quality_PM2.5'] * 0.3 +
        pollutant_summary['air_quality_PM10'] * 0.2
    )

    most_polluted = pollutant_summary.loc[pollutant_summary['Overall_Score'].idxmax()]
    least_polluted = pollutant_summary.loc[pollutant_summary['Overall_Score'].idxmin()]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🚨 Most Polluted Location")
        st.metric(
            label=f"{most_polluted['location_name']}",
            value=f"AQI: {most_polluted['air_quality_us-epa-index']:.2f}",
            delta=f"PM2.5: {most_polluted['air_quality_PM2.5']:.2f}, PM10: {most_polluted['air_quality_PM10']:.2f}"
        )
        st.progress(min(1.0, most_polluted['Overall_Score'] / 500))  # visual indicator

    with col2:
        st.markdown("#### 🌿 Least Polluted Location")
        st.metric(
            label=f"{least_polluted['location_name']}",
            value=f"AQI: {least_polluted['air_quality_us-epa-index']:.2f}",
            delta=f"PM2.5: {least_polluted['air_quality_PM2.5']:.2f}, PM10: {least_polluted['air_quality_PM10']:.2f}"
        )
        st.progress(min(1.0, least_polluted['Overall_Score'] / 500))  # visual indicator
else:
    st.info("No data available to determine pollution extremes.")

# ============================
# Optional Year, Month, Day Filters
# ============================
st.sidebar.markdown("### 📅 PM Trend Date Filters")

# Extract year, month, day
df_filtered['Year'] = df_filtered['last_updated'].dt.year
df_filtered['Month'] = df_filtered['last_updated'].dt.month
df_filtered['Day'] = df_filtered['last_updated'].dt.day

# Year filter (optional)
years = sorted(df_filtered['Year'].unique())
selected_years = st.sidebar.multiselect("Select Year(s)", options=years, default=None)

# Month filter (optional)
months = list(range(1,13))
selected_months = st.sidebar.multiselect("Select Month(s)", options=months, default=None)

# Day filter (optional)
days = list(range(1,32))
selected_days = st.sidebar.multiselect("Select Day(s)", options=days, default=None)

# Apply filters only if selected
pm_trend_filtered = df_filtered.copy()
if selected_years:
    pm_trend_filtered = pm_trend_filtered[pm_trend_filtered['Year'].isin(selected_years)]
if selected_months:
    pm_trend_filtered = pm_trend_filtered[pm_trend_filtered['Month'].isin(selected_months)]
if selected_days:
    pm_trend_filtered = pm_trend_filtered[pm_trend_filtered['Day'].isin(selected_days)]

# ============================
# Multi-location Pollutant Comparison (Bar chart with values)
# ============================
styled_header("📊 Multi-location Pollutant Comparison")
pollutant_rename_map = {
    'air_quality_PM2.5': 'PM2.5',
    'air_quality_PM10': 'PM10',
    'air_quality_Nitrogen_dioxide': 'NO₂ (Nitrogen Dioxide)',
    'air_quality_Sulphur_dioxide': 'SO₂ (Sulphur Dioxide)',
    'air_quality_Carbon_Monoxide': 'CO (Carbon Monoxide)',
    'air_quality_Ozone': 'O₃ (Ozone)'
}


pollutant_cols = ['air_quality_PM2.5','air_quality_PM10','air_quality_Nitrogen_dioxide','air_quality_Sulphur_dioxide','air_quality_Carbon_Monoxide','air_quality_Ozone']
comparison_df = df_filtered.groupby('location_name')[pollutant_cols].mean().reset_index()
comparison_df = comparison_df.rename(columns=pollutant_rename_map)

# Bar chart with values displayed inside bars
short_pollutants = list(pollutant_rename_map.values())

melted_df = comparison_df.melt(id_vars='location_name', 
                               value_vars=short_pollutants, 
                               var_name='Pollutant', 
                               value_name='Value')

bar_fig = px.bar(
    melted_df,
    x='location_name',
    y='Value',
    color='Pollutant',
    text_auto=".2f",
    custom_data=['Pollutant'],
    title="Average Pollutant Levels per Location"
)

bar_fig.update_traces(
    hovertemplate='<b>Location:</b> %{x}<br><b>Pollutant:</b> %{customdata[0]}<br><b>Value:</b> %{y:.2f} µg/m³<br><extra></extra>'
)
st.plotly_chart(bar_fig, use_container_width=True)


# ============================
# Sub-filter: Greenhouse Gas / Pollutant Trends Over Time
# ============================
styled_header("♻️ Greenhouse Gas & Pollutant Trends Over Time")

# Define pollutant / GHG options
pollutant_display_map = {
    "PM2.5": "air_quality_PM2.5",
    "PM10": "air_quality_PM10",
    "CO (Carbon Monoxide)": "air_quality_Carbon_Monoxide",
    "NO₂ (Nitrogen Dioxide)": "air_quality_Nitrogen_dioxide",
    "SO₂ (Sulphur Dioxide)": "air_quality_Sulphur_dioxide",
    "O₃ (Ozone)": "air_quality_Ozone",
    "US EPA Index": "air_quality_us-epa-index"
}

# Add "All" option at top
pollutant_options = ["All"] + list(pollutant_display_map.keys())

# Allow multi-selection
selected_pollutants = st.multiselect(
    "Select Pollutant(s) or Greenhouse Gas(es)",
    options=pollutant_options,
    default=["PM2.5"]
)

# If "All" selected → use all pollutant columns
if "All" in selected_pollutants:
    selected_pollutant_cols = list(pollutant_display_map.values())
    selected_pollutant_names = list(pollutant_display_map.keys())
else:
    selected_pollutant_names = selected_pollutants
    selected_pollutant_cols = [pollutant_display_map[p] for p in selected_pollutants]

# Check data availability
if not pm_trend_filtered.empty and selected_pollutant_cols:

    # Melt dataframe to long format (so we can plot multiple pollutants together)
    pollutant_trend_df = (
        pm_trend_filtered.groupby(['last_updated', 'location_name'])[selected_pollutant_cols]
        .mean()
        .reset_index()
        .melt(id_vars=['last_updated', 'location_name'], 
              value_vars=selected_pollutant_cols,
              var_name='Pollutant', value_name='Concentration')
    )

    # Map back readable names
    reverse_map = {v: k for k, v in pollutant_display_map.items()}
    pollutant_trend_df['Pollutant'] = pollutant_trend_df['Pollutant'].map(reverse_map)

    # Create multi-line plot
    pollutant_trend_fig = px.line(
        pollutant_trend_df,
        x='last_updated',
        y='Concentration',
        color='Pollutant',
        line_dash='location_name',  # optional: differentiate by location
        markers=True,
        title=f"{', '.join(selected_pollutant_names)} Trend(s) Over Time"
    )

    pollutant_trend_fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Concentration (µg/m³ or Index)",
        legend_title="Pollutant / GHG",
        template="plotly_dark",
        height=500,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(pollutant_trend_fig, use_container_width=True)

else:
    st.info("No pollutant data available for the selected filters or date range.")


# ============================
# 🌎 Dynamic Air Quality Summary by Continent or Location
# ============================

styled_header("🌎 Air Quality Summary for Selected Dates")

# Let user choose grouping mode
group_option = st.radio(
    "View summary by:",
    options=["Continent", "Location"],
    horizontal=True
)

# Determine selected unique date(s) based on sidebar filters
if selected_years or selected_months or selected_days:
    selected_dates_mask = pd.Series([True] * len(df_filtered), index=df_filtered.index)

    if selected_years:
        selected_dates_mask &= df_filtered['Year'].isin(selected_years)
    if selected_months:
        selected_dates_mask &= df_filtered['Month'].isin(selected_months)
    if selected_days:
        selected_dates_mask &= df_filtered['Day'].isin(selected_days)

    selected_data = df_filtered[selected_dates_mask].copy()

    # Ensure datetime format
    selected_data['last_updated'] = pd.to_datetime(selected_data['last_updated'])

    # Group key based on user choice
    group_key = "continent" if group_option == "Continent" else "location_name"

    # Check for valid grouping key
    if group_key not in selected_data.columns:
        st.warning(f"'{group_key}' column not found in dataset.")
    else:
        # Compute averages for pollutants/greenhouse gases
        pollutant_cols = [
            'air_quality_us-epa-index',
            'air_quality_PM2.5',
            'air_quality_PM10',
            'air_quality_Carbon_Monoxide',
            'air_quality_Nitrogen_dioxide',
            'air_quality_Sulphur_dioxide',
            'air_quality_Ozone'
        ]

        # Define units for each pollutant
        pollutant_units = {
            'air_quality_us-epa-index': 'Index',
            'air_quality_PM2.5': 'µg/m³',
            'air_quality_PM10': 'µg/m³',
            'air_quality_Carbon_Monoxide': 'µg/m³',
            'air_quality_Nitrogen_dioxide': 'µg/m³',
            'air_quality_Sulphur_dioxide': 'µg/m³',
            'air_quality_Ozone': 'µg/m³'
        }

        available_cols = [col for col in pollutant_cols if col in selected_data.columns]

        summary_df = (
            selected_data.groupby([group_key, selected_data['last_updated'].dt.date])[available_cols]
            .mean()
            .reset_index()
        )

        # Display cards side by side (3 per row)
        cols = st.columns(3)
        idx = 0

        for entity in summary_df[group_key].unique():
            entity_data = summary_df[summary_df[group_key] == entity]

            with cols[idx % 3]:
                st.markdown(
                    f"""
                    <div style='background-color:#111827; padding:15px; border-radius:12px;
                                box-shadow:0 0 10px rgba(0,0,0,0.3); color:white; margin-bottom:15px;'>
                        <h4 style='color:#00C896; text-align:center;'>{entity}</h4>
                    """,
                    unsafe_allow_html=True
                )

                for _, row in entity_data.iterrows():
                    st.markdown(
                        f"""
                        <p><b>📅 Date:</b> {row['last_updated']}</p>
                        <ul style='margin-left:10px;'>
                            {"".join([
                                f"<li><b>{col.replace('air_quality_', '').replace('-', ' ').upper()}:</b> {row[col]:.2f} {pollutant_units.get(col, '')}</li>"
                                for col in available_cols
                            ])}
                        </ul>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown("</div>", unsafe_allow_html=True)

            idx += 1

else:
    st.info("Please select at least one Year, Month, or Day from 📅 PM Trend Date Filters in the sidebar to view the air quality summary.")


# ============================
# AQI Category Pie
# ============================
styled_header("🥧 AQI Category Distribution")
df_filtered['AQI_Category'] = df_filtered['air_quality_us-epa-index'].map(aqi_options)
aqi_counts = df_filtered.groupby('AQI_Category')['location_name'].count().reset_index()
aqi_counts.columns = ['AQI_Category','Count']

pie_fig = px.pie(
    aqi_counts,
    values='Count',
    names='AQI_Category',
    title="AQI Category Distribution",
    hole=0.4
)
pie_fig.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(pie_fig, use_container_width=True)

# ============================
# Correlation Heatmap
# ============================
# ============================
# 🔥 Correlation Analysis (Dark Theme)
# ============================

styled_header("🔥 Correlation Analysis")

corr_cols = [
    'air_quality_us-epa-index',
    'air_quality_PM2.5',
    'air_quality_PM10',
    'temperature_celsius',
    'humidity',
    'wind_mph',
    'uv_index'
]

# Filter only existing columns
corr_cols = [col for col in corr_cols if col in df_filtered.columns]

if corr_cols:
    corr = df_filtered[corr_cols].corr()

    # Dark style setup
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_alpha(0.0)   # transparent figure background
    ax.set_facecolor('#111827')  # dark axes background

    # Heatmap with dark aesthetics
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap='rocket',  # better contrast on dark bg
        linewidths=0.5,
        cbar_kws={'label': 'Correlation'},
        ax=ax,
        annot_kws={'color': 'white', 'size': 10}
    )

    # Style adjustments
    ax.set_title("Correlation Between Key Air Quality and Weather Parameters",
                 color='white', fontsize=12, pad=15)
    ax.tick_params(colors='white', labelsize=10)
    for spine in ax.spines.values():
        spine.set_visible(False)

    st.pyplot(fig)
else:
    st.warning("No valid columns found for correlation analysis.")


# ============================
# Raw Data
# ============================
st.markdown("---")
with st.expander("View Raw Filtered Air Quality Data"):
    st.dataframe(df_filtered.reset_index(drop=True), use_container_width=True)
