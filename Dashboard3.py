import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="ClimateScope - Global Weather Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better aesthetics
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #2c3e50;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stMetric label {
        color: #ecf0f1 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #3498db !important;
        font-size: 28px !important;
        font-weight: bold !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #2ecc71 !important;
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 20px;
    }
    h2 {
        color: #2c3e50;
        padding-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data with caching
@st.cache_data
def load_data():
    """Load and prepare the weather dataset"""
    df = pd.read_csv(r"C:\Users\nithi\Downloads\GlobalWeatherRepository_Cleaned.csv")
    
    # Convert date columns if present
    date_columns = ['last_updated', 'date', 'timestamp']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

# Load the data
try:
    df = load_data()
    
    # Dashboard Title
    st.title("🌍 ClimateScope: Global Weather Analytics Dashboard")
    st.markdown("*Visualizing Weather Trends, Patterns, and Extreme Events Worldwide*")
    st.markdown("---")
    
    # Sidebar - Filters and Controls
    st.sidebar.header("🎛️ Dashboard Controls")
    st.sidebar.markdown("---")
    
    # Region/Country Filter
    if 'country' in df.columns:
        countries = sorted(df['country'].unique())
        selected_countries = st.sidebar.multiselect(
            "Select Countries",
            options=countries,
            default=countries[:5] if len(countries) > 5 else countries
        )
    else:
        selected_countries = None
    
    # Continent/Region Filter (if available)
    if 'continent' in df.columns or 'region' in df.columns:
        region_col = 'continent' if 'continent' in df.columns else 'region'
        regions = sorted(df[region_col].unique())
        selected_regions = st.sidebar.multiselect(
            f"Select {region_col.title()}s",
            options=regions,
            default=regions
        )
    else:
        selected_regions = None
        region_col = None
    
    # Temperature Range Slider
    if 'temperature_celsius' in df.columns:
        temp_col = 'temperature_celsius'
    elif 'temp_c' in df.columns:
        temp_col = 'temp_c'
    elif 'temperature' in df.columns:
        temp_col = 'temperature'
    else:
        temp_col = None
    
    if temp_col:
        min_temp = float(df[temp_col].min())
        max_temp = float(df[temp_col].max())
        temp_range = st.sidebar.slider(
            "Temperature Range (°C)",
            min_value=min_temp,
            max_value=max_temp,
            value=(min_temp, max_temp)
        )
    
    # Date Range Filter (if date column exists)
    date_col = None
    for col in ['last_updated', 'date', 'timestamp']:
        if col in df.columns:
            date_col = col
            break
    
    if date_col and df[date_col].notna().any():
        min_date = df[date_col].min()
        max_date = df[date_col].max()
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    st.sidebar.markdown("---")
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_countries and 'country' in df.columns:
        filtered_df = filtered_df[filtered_df['country'].isin(selected_countries)]
    
    if selected_regions and region_col:
        filtered_df = filtered_df[filtered_df[region_col].isin(selected_regions)]
    
    if temp_col:
        filtered_df = filtered_df[
            (filtered_df[temp_col] >= temp_range[0]) & 
            (filtered_df[temp_col] <= temp_range[1])
        ]
    
    if date_col and df[date_col].notna().any():
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df[date_col] >= pd.Timestamp(date_range[0])) & 
                (filtered_df[date_col] <= pd.Timestamp(date_range[1]))
            ]
    
    # Identify precipitation column
    if 'precipitation_mm' in df.columns:
        precip_col = 'precipitation_mm'
    elif 'precip_mm' in df.columns:
        precip_col = 'precip_mm'
    else:
        precip_col = None
    
    # Identify wind column
    if 'wind_kph' in df.columns:
        wind_col = 'wind_kph'
    elif 'wind_speed_kph' in df.columns:
        wind_col = 'wind_speed_kph'
    else:
        wind_col = None
    
    # Key Metrics Row
    st.header("📊 Key Weather Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if temp_col:
            avg_temp = filtered_df[temp_col].mean()
            st.metric(
                label="🌡️ Avg Temperature", 
                value=f"{avg_temp:.1f}°C",
                delta=None
            )
        else:
            st.metric("🌡️ Avg Temperature", "N/A")
    
    with col2:
        if 'humidity' in filtered_df.columns:
            avg_humidity = filtered_df['humidity'].mean()
            st.metric(
                label="💧 Avg Humidity", 
                value=f"{avg_humidity:.1f}%",
                delta=None
            )
        else:
            st.metric("💧 Avg Humidity", "N/A")
    
    with col3:
        if precip_col and precip_col in filtered_df.columns:
            total_precip = filtered_df[precip_col].sum()
            st.metric(
                label="🌧️ Total Precipitation", 
                value=f"{total_precip:.1f}mm",
                delta=None
            )
        else:
            st.metric("🌧️ Total Precipitation", "N/A")
    
    with col4:
        if wind_col and wind_col in filtered_df.columns:
            avg_wind = filtered_df[wind_col].mean()
            st.metric(
                label="💨 Avg Wind Speed", 
                value=f"{avg_wind:.1f} kph",
                delta=None
            )
        else:
            st.metric("💨 Avg Wind Speed", "N/A")
    
    with col5:
        st.metric(
            label="📊 Total Records", 
            value=f"{len(filtered_df):,}",
            delta=None
        )
    
    st.markdown("---")
    
    # Visualization Section 1: Geographic Patterns
    st.header("🗺️ Geographic Weather Patterns")
    
    tab1, tab2 = st.tabs(["Choropleth Map", "Regional Comparison"])
    
    with tab1:
        if 'country' in filtered_df.columns and temp_col:
            # Aggregate by country
            country_stats = filtered_df.groupby('country').agg({
                temp_col: 'mean',
                'humidity': 'mean' if 'humidity' in filtered_df.columns else temp_col,
            }).reset_index()
            
            fig_map = px.choropleth(
                country_stats,
                locations='country',
                locationmode='country names',
                color=temp_col,
                hover_name='country',
                hover_data={temp_col: ':.2f'},
                color_continuous_scale='RdYlBu_r',
                title='Average Temperature by Country'
            )
            fig_map.update_layout(
                height=600,
                geo=dict(showframe=False, showcoastlines=True)
            )
            st.plotly_chart(fig_map, use_container_width=True)
    
    with tab2:
        if 'country' in filtered_df.columns and temp_col:
            top_countries = filtered_df['country'].value_counts().head(10).index
            country_data = filtered_df[filtered_df['country'].isin(top_countries)]
            
            fig_bar = px.bar(
                country_data.groupby('country')[temp_col].mean().reset_index(),
                x='country',
                y=temp_col,
                title='Average Temperature Comparison (Top 10 Countries)',
                color=temp_col,
                color_continuous_scale='thermal'
            )
            fig_bar.update_layout(height=500, xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # Visualization Section 2: Time Series Trends
    st.header("📈 Time Series Analysis")
    
    if date_col and temp_col:
        col1, col2 = st.columns(2)
        
        with col1:
            # Temperature trend over time
            time_series = filtered_df.groupby(filtered_df[date_col].dt.date)[temp_col].mean().reset_index()
            time_series.columns = ['date', 'temperature']
            
            fig_temp_trend = px.line(
                time_series,
                x='date',
                y='temperature',
                title='Temperature Trend Over Time',
                labels={'temperature': 'Temperature (°C)', 'date': 'Date'}
            )
            fig_temp_trend.update_traces(line_color='#FF6B6B')
            fig_temp_trend.update_layout(height=400)
            st.plotly_chart(fig_temp_trend, use_container_width=True)
        
        with col2:
            if 'humidity' in filtered_df.columns:
                humidity_series = filtered_df.groupby(filtered_df[date_col].dt.date)['humidity'].mean().reset_index()
                humidity_series.columns = ['date', 'humidity']
                
                fig_humidity_trend = px.line(
                    humidity_series,
                    x='date',
                    y='humidity',
                    title='Humidity Trend Over Time',
                    labels={'humidity': 'Humidity (%)', 'date': 'Date'}
                )
                fig_humidity_trend.update_traces(line_color='#4ECDC4')
                fig_humidity_trend.update_layout(height=400)
                st.plotly_chart(fig_humidity_trend, use_container_width=True)
    
    st.markdown("---")
    
    # Visualization Section 3: Correlations and Distributions
    st.header("🔍 Weather Parameter Relationships")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if temp_col and 'humidity' in filtered_df.columns:
            fig_scatter = px.scatter(
                filtered_df.sample(min(5000, len(filtered_df))),
                x=temp_col,
                y='humidity',
                color='country' if 'country' in filtered_df.columns else None,
                title='Temperature vs Humidity',
                labels={temp_col: 'Temperature (°C)', 'humidity': 'Humidity (%)'},
                opacity=0.6
            )
            fig_scatter.update_layout(height=450)
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        if temp_col:
            fig_hist = px.histogram(
                filtered_df,
                x=temp_col,
                nbins=50,
                title='Temperature Distribution',
                labels={temp_col: 'Temperature (°C)'},
                color_discrete_sequence=['#FF6B6B']
            )
            fig_hist.update_layout(height=450, showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)
    
    st.markdown("---")
    
    # Visualization Section 4: Seasonal Heatmap
    st.header("🌡️ Seasonal Variation Analysis")
    
    if date_col and temp_col:
        # Extract month and create pivot table
        filtered_df['month'] = filtered_df[date_col].dt.month
        filtered_df['year'] = filtered_df[date_col].dt.year
        
        if 'country' in filtered_df.columns:
            # Heatmap by country and month
            top_10_countries = filtered_df['country'].value_counts().head(10).index
            heatmap_data = filtered_df[filtered_df['country'].isin(top_10_countries)]
            pivot_table = heatmap_data.pivot_table(
                values=temp_col,
                index='country',
                columns='month',
                aggfunc='mean'
            )
            
            fig_heatmap = px.imshow(
                pivot_table,
                labels=dict(x="Month", y="Country", color="Temperature (°C)"),
                x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][:pivot_table.shape[1]],
                y=pivot_table.index,
                color_continuous_scale='RdYlBu_r',
                title='Monthly Temperature Patterns by Country'
            )
            fig_heatmap.update_layout(height=500)
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("---")
    
    # Visualization Section 5: Extreme Events
    st.header("⚠️ Extreme Weather Events")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if temp_col:
            # Extreme temperatures
            temp_threshold = st.slider(
                "Temperature Extremes Threshold (percentile)",
                min_value=90,
                max_value=99,
                value=95,
                help="Show temperatures above this percentile"
            )
            
            threshold_value = filtered_df[temp_col].quantile(temp_threshold/100)
            extreme_temps = filtered_df[filtered_df[temp_col] >= threshold_value]
            
            if 'country' in extreme_temps.columns:
                extreme_by_country = extreme_temps['country'].value_counts().head(10)
                fig_extreme = px.bar(
                    x=extreme_by_country.values,
                    y=extreme_by_country.index,
                    orientation='h',
                    title=f'Top 10 Countries with Extreme Temperatures (>{threshold_value:.1f}°C)',
                    labels={'x': 'Number of Events', 'y': 'Country'},
                    color=extreme_by_country.values,
                    color_continuous_scale='Reds'
                )
                fig_extreme.update_layout(height=450, showlegend=False)
                st.plotly_chart(fig_extreme, use_container_width=True)
    
    with col2:
        if precip_col:
            # High precipitation events
            precip_threshold = st.slider(
                "Precipitation Threshold (mm)",
                min_value=float(filtered_df[precip_col].quantile(0.9)),
                max_value=float(filtered_df[precip_col].max()),
                value=float(filtered_df[precip_col].quantile(0.95))
            )
            
            high_precip = filtered_df[filtered_df[precip_col] >= precip_threshold]
            
            if 'country' in high_precip.columns:
                precip_by_country = high_precip['country'].value_counts().head(10)
                fig_precip = px.bar(
                    x=precip_by_country.values,
                    y=precip_by_country.index,
                    orientation='h',
                    title=f'Top 10 Countries with High Precipitation (>{precip_threshold:.1f}mm)',
                    labels={'x': 'Number of Events', 'y': 'Country'},
                    color=precip_by_country.values,
                    color_continuous_scale='Blues'
                )
                fig_precip.update_layout(height=450, showlegend=False)
                st.plotly_chart(fig_precip, use_container_width=True)
    
    st.markdown("---")
    
    # Visualization Section 6: Multi-Parameter Comparison
    st.header("📊 Multi-Parameter Weather Dashboard")
    
    if 'country' in filtered_df.columns:
        selected_country = st.selectbox(
            "Select a country for detailed analysis",
            options=sorted(filtered_df['country'].unique())
        )
        
        country_df = filtered_df[filtered_df['country'] == selected_country]
        
        # Create subplot with multiple parameters
        fig_multi = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Temperature Distribution',
                'Humidity Distribution',
                'Wind Speed Distribution' if wind_col else 'Precipitation',
                'Weather Parameters Over Time'
            ),
            specs=[[{'type': 'histogram'}, {'type': 'histogram'}],
                   [{'type': 'histogram'}, {'type': 'scatter'}]]
        )
        
        # Temperature histogram
        if temp_col:
            fig_multi.add_trace(
                go.Histogram(x=country_df[temp_col], name='Temperature', marker_color='#FF6B6B'),
                row=1, col=1
            )
        
        # Humidity histogram
        if 'humidity' in country_df.columns:
            fig_multi.add_trace(
                go.Histogram(x=country_df['humidity'], name='Humidity', marker_color='#4ECDC4'),
                row=1, col=2
            )
        
        # Wind or Precipitation histogram
        if wind_col:
            fig_multi.add_trace(
                go.Histogram(x=country_df[wind_col], name='Wind Speed', marker_color='#95E1D3'),
                row=2, col=1
            )
        elif precip_col:
            fig_multi.add_trace(
                go.Histogram(x=country_df[precip_col], name='Precipitation', marker_color='#3498db'),
                row=2, col=1
            )
        
        # Time series of multiple parameters
        if date_col and temp_col:
            time_data = country_df.sort_values(date_col).head(1000)
            fig_multi.add_trace(
                go.Scatter(x=time_data[date_col], y=time_data[temp_col], 
                          mode='lines', name='Temperature', line=dict(color='#FF6B6B')),
                row=2, col=2
            )
        
        fig_multi.update_layout(height=800, showlegend=True, title_text=f"Detailed Analysis: {selected_country}")
        st.plotly_chart(fig_multi, use_container_width=True)
    
    st.markdown("---")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #7f8c8d; padding: 20px;'>
            <p>ClimateScope Dashboard | Data Source: Global Weather Repository</p>
            <p>Built with Streamlit & Plotly | Project Milestone 3</p>
        </div>
    """, unsafe_allow_html=True)

except FileNotFoundError:
    st.error("❌ Dataset not found! Please ensure the file path is correct:")
    st.code(r"C:\Users\nithi\Downloads\GlobalWeatherRepository_Cleaned.csv")
    st.info("Update the file path in the code if your dataset is located elsewhere.")
except Exception as e:
    st.error(f"❌ An error occurred: {str(e)}")
    st.info("Please check your dataset format and ensure all required columns are present.")