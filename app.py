import streamlit as st
import pandas as pd
from datetime import datetime
from data_generator import generate_climate_data
from sidebar_filters import render_sidebar_filters

st.set_page_config(
    page_title="ClimateScope Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    return generate_climate_data()

df = load_data()

filtered_df = render_sidebar_filters(df)

st.session_state['filtered_df'] = filtered_df
st.session_state['full_df'] = df

st.title("🏠 Executive Dashboard")
st.markdown("### Global Climate Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Records", f"{len(filtered_df):,}")

with col2:
    st.metric("Unique Countries", len(filtered_df['Country'].unique()))

with col3:
    avg_temp = filtered_df['Temperature'].mean()
    st.metric("Average Temperature", f"{avg_temp:.2f}°C")

with col4:
    duration = (filtered_df['Date'].max() - filtered_df['Date'].min()).days + 1
    st.metric("Data Coverage", f"{duration} days")

st.markdown("---")
st.subheader("Geographical Context")

import plotly.express as px

metric_for_map = st.selectbox(
    "Select Climate Metric",
    ['Temperature', 'Humidity', 'Wind Speed', 'Precipitation']
)

projection_type = st.selectbox(
    "Map Projection",
    ['Natural Earth', 'Orthographic', 'Mercator'],
    help="Switch between different map projections"
)

projection_map = {
    'Natural Earth': 'natural earth',
    'Orthographic': 'orthographic',
    'Mercator': 'mercator'
}

country_avg = filtered_df.groupby('Country').agg({
    metric_for_map: 'mean',
    'Latitude': 'first',
    'Longitude': 'first'
}).reset_index()

min_val = country_avg[metric_for_map].min()
max_val = country_avg[metric_for_map].max()

if max_val == min_val:
    country_avg['size_normalized'] = 15
else:
    country_avg['size_normalized'] = ((country_avg[metric_for_map] - min_val) / (max_val - min_val) * 30) + 5

fig = px.scatter_geo(
    country_avg,
    lat='Latitude',
    lon='Longitude',
    color=metric_for_map,
    hover_name='Country',
    size='size_normalized',
    projection=projection_map[projection_type],
    color_continuous_scale='RdYlBu_r',
    title=f"Global Distribution of Mean {metric_for_map}"
)

fig.update_layout(
    height=600,
    margin=dict(l=0, r=0, t=40, b=0)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("""
**Navigation:** Use the sidebar to access different analysis modules:
- 📊 Statistical Analysis
- 📈 Climate Trends
- ⚠️ Extreme Events
- ❓ Help & User Guide
""")
