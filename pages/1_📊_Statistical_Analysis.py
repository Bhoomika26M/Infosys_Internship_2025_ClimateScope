import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_generator import generate_climate_data
from sidebar_filters import render_sidebar_filters

st.set_page_config(page_title="Statistical Analysis", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    return generate_climate_data()

df = load_data()
filtered_df = render_sidebar_filters(df)

st.session_state['filtered_df'] = filtered_df
st.session_state['full_df'] = df

st.title("📊 Statistical Analysis")
st.markdown("### Correlation and Comparison")

st.markdown("---")
st.subheader("Two-Metric Comparison")

metrics = ['Temperature', 'Humidity', 'Wind Speed', 'Precipitation']

col1, col2 = st.columns(2)

with col1:
    metric_a = st.selectbox("Metric A (X-Axis)", metrics, index=0)

with col2:
    metric_b = st.selectbox("Metric B (Y-Axis)", metrics, index=1)

st.markdown("#### Scatter Plot: Correlation Analysis")

fig_scatter = px.scatter(
    filtered_df,
    x=metric_a,
    y=metric_b,
    color='Country',
    title=f"{metric_a} vs {metric_b} - Correlation Analysis",
    hover_data=['Date', 'Country', 'Region'],
    opacity=0.6
)

fig_scatter.update_layout(
    height=500,
    showlegend=False
)

st.plotly_chart(fig_scatter, use_container_width=True)

correlation = filtered_df[[metric_a, metric_b]].corr().iloc[0, 1]
st.info(f"**Correlation Coefficient:** {correlation:.3f}")

st.markdown("---")
st.markdown("#### Comparative Bar Chart")

country_avg = filtered_df.groupby('Country').agg({
    metric_a: 'mean',
    metric_b: 'mean'
}).reset_index()

fig_bar = go.Figure()

fig_bar.add_trace(go.Bar(
    name=metric_a,
    x=country_avg['Country'],
    y=country_avg[metric_a],
    marker_color='#636EFA'
))

fig_bar.add_trace(go.Bar(
    name=metric_b,
    x=country_avg['Country'],
    y=country_avg[metric_b],
    marker_color='#EF553B'
))

fig_bar.update_layout(
    title=f"Average {metric_a} and {metric_b} by Country",
    barmode='group',
    height=500,
    xaxis_tickangle=-45
)

st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.subheader("Detailed Statistics Table")
st.markdown("Core descriptive statistics segmented by region")

region_stats = filtered_df.groupby('Region').agg({
    'Temperature': ['mean', 'median', 'min', 'max', 'count'],
    'Humidity': ['mean', 'median', 'min', 'max', 'count'],
    'Wind Speed': ['mean', 'median', 'min', 'max', 'count'],
    'Precipitation': ['mean', 'median', 'min', 'max', 'count']
}).round(2)

region_stats.columns = [f"{metric}_{stat}" for metric, stat in region_stats.columns]

st.dataframe(region_stats, use_container_width=True)

st.markdown("---")
st.subheader("Summary Statistics by Metric")

tab1, tab2, tab3, tab4 = st.tabs(['Temperature', 'Humidity', 'Wind Speed', 'Precipitation'])

with tab1:
    temp_stats = filtered_df.groupby('Country')['Temperature'].describe().round(2)
    st.dataframe(temp_stats, use_container_width=True)

with tab2:
    hum_stats = filtered_df.groupby('Country')['Humidity'].describe().round(2)
    st.dataframe(hum_stats, use_container_width=True)

with tab3:
    wind_stats = filtered_df.groupby('Country')['Wind Speed'].describe().round(2)
    st.dataframe(wind_stats, use_container_width=True)

with tab4:
    prec_stats = filtered_df.groupby('Country')['Precipitation'].describe().round(2)
    st.dataframe(prec_stats, use_container_width=True)
