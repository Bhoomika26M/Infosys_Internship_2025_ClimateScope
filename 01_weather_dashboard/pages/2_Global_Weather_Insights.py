import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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



# =========================
# Load Data
# =========================
@st.cache_data
def load_data():
    #df = pd.read_csv("../data/processed/normalized_weather_data.csv", parse_dates=["last_updated"])
    df = pd.read_csv("../data/processed/processed_weather_data.csv", parse_dates=["last_updated"])

    df.columns = [col.strip() for col in df.columns]
    return df

df = load_data()

# =========================
# Map Country → Continent
# =========================
def country_to_continent(country_name):
    try:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        return {
            'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe', 'NA': 'North America',
            'OC': 'Oceania', 'SA': 'South America', 'AN': 'Antarctica'
        }[continent_code]
    except:
        return "Unknown"

if 'continent' not in df.columns:
    df['continent'] = df['country'].apply(country_to_continent)

# =========================
# Detect User Country
# =========================
def get_user_country():
    try:
        ip_info = requests.get('https://ipinfo.io').json()
        return ip_info.get('country', None)
    except:
        return None

user_country = get_user_country()
unique_countries = sorted(df['country'].unique())

# Default country and continent
default_country = user_country if user_country in unique_countries else "India"
default_continent = df[df['country']==default_country]['continent'].values[0]

# =========================
# Sidebar Filters
# =========================
st.sidebar.header("📍 Global Geographic Filters")

# Continent filter
continents = sorted(df['continent'].unique())
select_all_continents = st.sidebar.checkbox("Select All Continents", value=False)
if select_all_continents:
    selected_continents = continents
else:
    selected_continents = st.sidebar.multiselect(
        "Select Continents",
        options=continents,
        default=[default_continent]
    )

# AQI filter
aqi_options = {
    1: 'Good (1)', 2: 'Moderate (2)', 3: 'Unhealthy for Sensitive Groups (3)',
    4: 'Unhealthy (4)', 5: 'Very Unhealthy (5)', 6: 'Hazardous (6)'
}
selected_aqi_level = st.sidebar.select_slider(
    "Max Air Quality Index",
    options=list(aqi_options.keys()),
    value=6,
    format_func=lambda x: aqi_options[x]
)

# Dynamic ranges for weather parameters
st.sidebar.markdown("### Adjust Weather Parameter Ranges")
temp_range = st.sidebar.slider("Temperature (°C)", float(df['temperature_celsius'].min()), float(df['temperature_celsius'].max()), (float(df['temperature_celsius'].min()), float(df['temperature_celsius'].max())), 0.01)
precip_range = st.sidebar.slider("Precipitation (mm)", float(df['precip_mm'].min()), float(df['precip_mm'].max()), (float(df['precip_mm'].min()), float(df['precip_mm'].max())), 0.01)
wind_range = st.sidebar.slider("Wind Speed (mph)", float(df['wind_mph'].min()), float(df['wind_mph'].max()), (float(df['wind_mph'].min()), float(df['wind_mph'].max())), 0.01)
uv_range = st.sidebar.slider("UV Index", float(df['uv_index'].min()), float(df['uv_index'].max()), (float(df['uv_index'].min()), float(df['uv_index'].max())), 0.01)
humidity_range = st.sidebar.slider("Humidity (%)", float(df['humidity'].min()), float(df['humidity'].max()), (float(df['humidity'].min()), float(df['humidity'].max())), 0.01)

# =========================
# Country Selection on Main Page
# =========================
st.markdown("### 🌏 Select Countries by Continent")

selected_countries = []

for cont in selected_continents:
    countries_in_cont = sorted(df[df['continent'] == cont]['country'].unique())
    default_countries = [default_country] if default_country in countries_in_cont else []

    with st.expander(f"{cont} ({len(countries_in_cont)} countries)", expanded=True):

        # ✅ Add "Select all countries in {continent}" button
        select_all_clicked = st.button(f"Select all countries in {cont}", key=f"select_all_{cont}")

        # If the button is clicked → select all countries in that continent
        if select_all_clicked:
            st.session_state[f"countries_{cont}"] = countries_in_cont

        chosen = st.multiselect(
            f"Select countries in {cont}",
            options=countries_in_cont,
            default=st.session_state.get(f"countries_{cont}", default_countries),
            key=f"countries_{cont}"
        )

        selected_countries.extend(chosen)

if not selected_countries:
    st.warning("Please select at least one country to view data.")
    st.stop()


# =========================
# Filter Data
# =========================
df_filtered = df[
    (df['country'].isin(selected_countries)) &
    (df['air_quality_us-epa-index'] <= selected_aqi_level) &
    (df['temperature_celsius'] >= temp_range[0]) & (df['temperature_celsius'] <= temp_range[1]) &
    (df['precip_mm'] >= precip_range[0]) & (df['precip_mm'] <= precip_range[1]) &
    (df['wind_mph'] >= wind_range[0]) & (df['wind_mph'] <= wind_range[1]) &
    (df['uv_index'] >= uv_range[0]) & (df['uv_index'] <= uv_range[1]) &
    (df['humidity'] >= humidity_range[0]) & (df['humidity'] <= humidity_range[1])
]

df_filtered['latitude'] = pd.to_numeric(df_filtered['latitude'], errors='coerce')
df_filtered['longitude'] = pd.to_numeric(df_filtered['longitude'], errors='coerce')
df_filtered = df_filtered.dropna(subset=['latitude', 'longitude'])

if df_filtered.empty:
    st.warning("No data found for selected filters.")
    st.stop()

# =========================
# Global Map
# =========================
st.title("🌍 Global Weather Map")
df_filtered['humidity_size'] = df_filtered['humidity'] - df_filtered['humidity'].min() + 1e-3

map_fig = px.scatter_geo(
    df_filtered,
    lat='latitude',
    lon='longitude',
    color='temperature_celsius',
    hover_name='location_name',
    size='humidity_size',
    hover_data={
        'humidity': ':.2f',
        'wind_mph': ':.2f',
        'uv_index': ':.2f',
        'air_quality_us-epa-index': ':.2f'
    },
    color_continuous_scale=px.colors.sequential.Plasma,
    title=f"Weather Overview ({len(selected_continents)} continents, {len(selected_countries)} countries)",
    template="plotly_dark",
    height=600
)

if default_country in df_filtered['country'].values:
    user_data = df_filtered[df_filtered['country']==default_country].iloc[0]
    map_fig.update_geos(center={"lat": user_data['latitude'], "lon": user_data['longitude']}, projection_scale=2)

map_fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
st.plotly_chart(map_fig, use_container_width=True)

# =========================
# Weather Overview Tabs with Sub-filter and Graph Selection
# =========================
#
#Bar	Clear comparison of averages across locations
#Box	Shows spread, outliers, and variability
#Scatter	Reveals relationships between metrics
#Line	Tracks changes over time

st.markdown("## 📊 Weather Overview by Selected Locations")

# --- Brief Explanation of Graph Types ---
with st.expander("📘 What Each Graph Type Shows", expanded=False):
    st.markdown("""
    <div style="
        background-color: #1a1a1a;
        padding: 15px 18px;
        border-radius: 10px;
        color: #bbbbbb;
        font-size: 13px;
        line-height: 1.6;
    ">
    • <b>Bar Chart</b> — Compares <i>average values</i> (like temperature or humidity) across locations.<br>
    Ideal for spotting which areas are hotter, more humid, or windier overall.<br><br>

    • <b>Line Chart</b> — Tracks how a metric <i>changes over time</i> for each location.<br>
    Useful for observing temperature fluctuations or UV trends.<br>

    • <b>Box Plot</b> — Reveals <i>data spread, variability</i>, and <i>outliers</i>.<br>
    Helpful for identifying extreme or unstable weather conditions.<br>

    • <b>Scatter Plot</b> — Displays <i>relationships between two metrics</i> (e.g., temperature vs humidity).<br>
    Great for exploring correlations such as “higher temperature → lower humidity”.
    </div>
    """, unsafe_allow_html=True)



metric_map = {
    "Temperature": "temperature_celsius",
    "Humidity": "humidity",
    "Wind Speed": "wind_mph",
    "UV Index": "uv_index"
}
graph_options = ["Bar", "Line", "Box", "Scatter"]

tabs = st.tabs(list(metric_map.keys()))

for tab_name, tab in zip(metric_map.keys(), tabs):
    with tab:
        # --- Filter Locations ---
        sub_locations = st.multiselect(
            f"Filter Locations for {tab_name}",
            options=df_filtered['location_name'].unique(),
            default=df_filtered['location_name'].unique(),
            key=f"sub_{tab_name}_location"
        )
        df_tab = df_filtered[df_filtered['location_name'].isin(sub_locations)]

        # --- Select Graph Type ---
        graph_selected = st.selectbox(f"Select Graph Type for {tab_name}", graph_options, key=f"{tab_name}_graph")

        col = metric_map[tab_name]

        # --- Plot Function ---
        def plot_metric(df_plot, col, graph_type):
            if df_plot.empty:
                st.warning("No data for selected locations")
                return None

            color_scales = {
                "temperature_celsius": "Reds",
                "humidity": "Blues",
                "wind_mph": "Greens",
                "uv_index": "solar"
            }
            units = {
                "temperature_celsius": "°C",
                "humidity": "%",
                "wind_mph": "mph",
                "uv_index": "UV"
            }
            display_names = {
                "temperature_celsius": "Temperature",
                "humidity": "Humidity",
                "wind_mph": "Wind Speed",
                "uv_index": "UV Index"
            }

            scale = color_scales.get(col, "Plasma")
            unit = units.get(col, "")
            display_name = display_names.get(col, col)

            if graph_type == "Line":
                df_plot['last_updated'] = pd.to_datetime(df_plot['last_updated'], errors='coerce')
                df_plot = df_plot.dropna(subset=['last_updated'])
                fig = px.line(
                    df_plot,
                    x='last_updated',
                    y=col,
                    color='location_name',
                    markers=True,
                    hover_data=['country'],
                    title=f"{display_name} Trend Over Time by Location"
                )
                fig.update_traces(
                    hovertemplate="Location: %{customdata[0]}<br>" +
                                  "Date: %{x}<br>" +
                                  f"{display_name}: "+"%{y:.2f} "+unit
                )
            elif graph_type == "Bar":
                # Prepare the data
                df_avg = (
                    df_plot.groupby(['country', 'location_name'])[col]
                    .mean()
                    .reset_index()
                )

                # Format temperature to two decimal places
                df_avg[col] = df_avg[col].round(2)

                
                # Create the bar chart
                fig = px.bar(
                    df_avg,
                    x='location_name',
                    y=col,
                    color=col,
                    color_continuous_scale=scale,
                    title=f"Average {display_name} by Location",
                    hover_data={
                        'country': True,
                        'location_name': True,
                        col: ':.2f'
                    }
                )

            elif graph_type == "Box":
                fig = px.box(df_plot, x='location_name', y=col, color='location_name',
                             title=f"{display_name} Distribution by Location")
            elif graph_type == "Scatter":
                other_metric = np.random.choice([c for c in metric_map.values() if c != col])
                fig = px.scatter(df_plot, x=col, y=other_metric, color='location_name',
                                 hover_data=['country'],
                                 title=f"{display_name} vs {other_metric} by Location")

            fig.update_layout(height=450, xaxis_title="Location")
            return fig

        fig = plot_metric(df_tab, col, graph_selected)
        if fig:
            st.plotly_chart(fig, use_container_width=True)




# =========================
# KPI Cards
# =========================
st.markdown("## 🔹 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Temperature", f"{df_filtered['temperature_celsius'].mean():.2f} °C")
col2.metric("Avg Humidity", f"{df_filtered['humidity'].mean():.2f} %")
col3.metric("Avg Wind Speed", f"{df_filtered['wind_mph'].mean():.2f} mph")
col4.metric("Avg UV Index", f"{df_filtered['uv_index'].mean():.2f}")
