import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from data_generator import generate_climate_data
from sidebar_filters import render_sidebar_filters

st.set_page_config(page_title="Climate Trends", page_icon="📈", layout="wide")

@st.cache_data
def load_data():
    return generate_climate_data()

df = load_data()
filtered_df = render_sidebar_filters(df)

st.session_state['filtered_df'] = filtered_df
st.session_state['full_df'] = df

st.title("📈 Climate Trends")
st.markdown("### Temporal Analysis")

filtered_df = filtered_df.copy()
filtered_df['Month'] = filtered_df['Date'].dt.month_name()
filtered_df['Month_Num'] = filtered_df['Date'].dt.month

metrics = ['Temperature', 'Humidity', 'Wind Speed', 'Precipitation']

st.markdown("---")
primary_metric = st.selectbox(
    "Select Primary Metric",
    metrics,
    help="This metric will be used across all visualization tabs below"
)

st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    '📉 Trend Line', 
    '🔸 Scatter Plot', 
    '🎻 Violin Plot', 
    '🔥 Heatmap', 
    '📦 Box Plot', 
    '🎯 Radar Chart'
])

with tab1:
    st.subheader(f"{primary_metric} Trend Over Time")
    
    daily_avg = filtered_df.groupby('Date')[primary_metric].mean().reset_index()
    
    fig_line = px.line(
        daily_avg,
        x='Date',
        y=primary_metric,
        title=f"Daily Average {primary_metric} Trend",
        markers=True
    )
    
    fig_line.update_layout(height=500)
    st.plotly_chart(fig_line, use_container_width=True)

with tab2:
    st.subheader(f"{primary_metric} vs Secondary Metric")
    
    secondary_metric = st.selectbox(
        "Select Secondary Metric (X-Axis)",
        [m for m in metrics if m != primary_metric],
        key='scatter_secondary'
    )
    
    fig_scatter = px.scatter(
        filtered_df,
        x=secondary_metric,
        y=primary_metric,
        color='Country',
        title=f"{primary_metric} (Y-Axis) vs {secondary_metric} (X-Axis)",
        hover_data=['Date', 'Region'],
        opacity=0.6
    )
    
    fig_scatter.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.subheader(f"{primary_metric} Distribution by Month")
    
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    filtered_df['Month'] = pd.Categorical(filtered_df['Month'], categories=month_order, ordered=True)
    
    fig_violin = px.violin(
        filtered_df,
        x='Month',
        y=primary_metric,
        box=True,
        title=f"{primary_metric} Probability Density by Month",
        color='Month'
    )
    
    fig_violin.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_violin, use_container_width=True)

with tab4:
    st.subheader(f"{primary_metric} Seasonal Intensity Heatmap")
    
    heatmap_data = filtered_df.groupby(['Month_Num', 'Country'])[primary_metric].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='Country', columns='Month_Num', values=primary_metric)
    
    fig_heatmap = px.imshow(
        heatmap_pivot,
        labels=dict(x="Month", y="Country", color=primary_metric),
        x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        color_continuous_scale='RdYlBu_r',
        title=f"Monthly Average {primary_metric} by Country"
    )
    
    fig_heatmap.update_layout(height=600)
    st.plotly_chart(fig_heatmap, use_container_width=True)

with tab5:
    st.subheader(f"{primary_metric} Statistical Distribution by Month")
    
    fig_box = px.box(
        filtered_df,
        x='Month',
        y=primary_metric,
        title=f"{primary_metric} Distribution (Median, IQR, Outliers) by Month",
        color='Month'
    )
    
    fig_box.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

with tab6:
    st.subheader("Multi-Metric Climate Profile")
    st.markdown("Radar chart showing scaled comparison of all climate metrics by country")
    
    country_avg = filtered_df.groupby('Country').agg({
        'Temperature': 'mean',
        'Humidity': 'mean',
        'Wind Speed': 'mean',
        'Precipitation': 'mean'
    }).reset_index()
    
    for metric in metrics:
        min_val = country_avg[metric].min()
        max_val = country_avg[metric].max()
        if max_val == min_val:
            country_avg[f'{metric}_scaled'] = 50
        else:
            country_avg[f'{metric}_scaled'] = (country_avg[metric] - min_val) / (max_val - min_val) * 100
    
    selected_country = st.selectbox("Select Country for Radar Chart", country_avg['Country'].unique())
    
    country_data = country_avg[country_avg['Country'] == selected_country].iloc[0]
    
    categories = metrics
    values = [country_data[f'{m}_scaled'] for m in metrics]
    values.append(values[0])
    
    fig_radar = go.Figure()
    
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],
        fill='toself',
        name=selected_country
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title=f"Climate Profile for {selected_country}",
        height=500
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
    st.markdown("**Actual Values:**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Temperature", f"{country_data['Temperature']:.2f}°C")
    with col2:
        st.metric("Humidity", f"{country_data['Humidity']:.2f}%")
    with col3:
        st.metric("Wind Speed", f"{country_data['Wind Speed']:.2f} m/s")
    with col4:
        st.metric("Precipitation", f"{country_data['Precipitation']:.2f} mm")
