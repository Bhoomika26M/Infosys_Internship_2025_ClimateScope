"""
ClimateScope - Milestone 2: Complete Analysis & Visualization Dashboard
Standalone script with statistical analysis, extreme detection, maps, and interactive visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from scipy import stats
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# PAGE CONFIGURATION

st.set_page_config(
    page_title="ClimateScope Analytics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {padding: 1rem;}
    h1 {color: #1f77b4; text-align: center; padding: 20px;}
    h2 {color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;}
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {font-size: 2em; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# DATA LOADING

@st.cache_data
def load_data():
    """Load cleaned dataset"""
    try:
        df = pd.read_csv('global_weather_cleaned.csv')
        
        # Convert date columns
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower() or 'updated' in col.lower()]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    except FileNotFoundError:
        st.error("❌ File 'global_weather_cleaned.csv' not found!")
        st.info("Please ensure your cleaned dataset is in the same directory.")
        return None

# HELPER FUNCTIONS

def identify_columns(df):
    """Identify key columns"""
    # Date column
    date_col = None
    date_candidates = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
    if date_candidates:
        date_col = max(date_candidates, key=lambda x: df[x].notna().sum())
    
    # Location columns
    location_col = None
    for col in ['location_name', 'country', 'region', 'location']:
        if col in df.columns:
            location_col = col
            break
    
    country_col = 'country' if 'country' in df.columns else None
    
    # Temperature column
    temp_col = None
    for col in df.columns:
        if 'temp' in col.lower() and 'celsius' in col.lower():
            temp_col = col
            break
    if not temp_col:
        temp_cols = [col for col in df.columns if 'temp' in col.lower() and df[col].dtype in [np.float64, np.int64]]
        if temp_cols:
            temp_col = temp_cols[0]
    
    # Wind column
    wind_col = None
    for col in df.columns:
        if 'wind' in col.lower() and any(x in col.lower() for x in ['kph', 'speed', 'mph', 'm/s']):
            wind_col = col
            break
    
    # Pressure column
    pressure_col = None
    for col in df.columns:
        if 'pressure' in col.lower():
            pressure_col = col
            break
    
    # Humidity column
    humidity_col = None
    for col in df.columns:
        if 'humidity' in col.lower():
            humidity_col = col
            break
    
    return date_col, location_col, country_col, temp_col, wind_col, pressure_col, humidity_col

def detect_extreme_events(df, col, sigma=3):
    """Detect extreme events using z-score method"""
    # Check if column has valid data
    if col not in df.columns or df[col].isna().all():
        return pd.DataFrame(), pd.DataFrame(), 0, 0
    
    valid_data = df[col].dropna()
    
    if len(valid_data) == 0:
        return pd.DataFrame(), pd.DataFrame(), 0, 0
    
    mean = valid_data.mean()
    std = valid_data.std()
    
    # Handle zero standard deviation
    if std == 0 or np.isnan(std):
        return pd.DataFrame(), pd.DataFrame(), mean, mean
    
    upper = mean + sigma * std
    lower = mean - sigma * std
    
    extreme_high = df[df[col] > upper]
    extreme_low = df[df[col] < lower]
    
    return extreme_high, extreme_low, upper, lower

# MAIN DASHBOARD

# Header
st.title("🌍 ClimateScope: Global Weather Analytics Dashboard")
st.markdown("### *Milestone 2: Statistical Analysis, Extreme Events & Regional Comparisons*")
st.markdown("---")

# Load data
df = load_data()

if df is None:
    st.stop()

# Identify columns
date_col, location_col, country_col, temp_col, wind_col, pressure_col, humidity_col = identify_columns(df)

# Display loading info
st.success(f"✅ Dataset loaded: **{len(df):,}** records | **{len(df.columns)}** columns")

# SIDEBAR FILTERS

st.sidebar.header("🎯 Dashboard Controls")
st.sidebar.markdown("---")

# Analysis sections
st.sidebar.subheader("📊 Analysis Sections")
show_stats = st.sidebar.checkbox("Statistical Summary", value=True)
show_distributions = st.sidebar.checkbox("Distributions", value=True)
show_extremes = st.sidebar.checkbox("Extreme Events", value=True)
show_regional = st.sidebar.checkbox("Regional Comparison", value=True)
show_timeseries = st.sidebar.checkbox("Time Series", value=True)
show_correlations = st.sidebar.checkbox("Correlations", value=True)
show_maps = st.sidebar.checkbox("Interactive Maps", value=True)

st.sidebar.markdown("---")

# Filters
st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Data Filters")

# Initialize session state for original data only once
if 'df_original' not in st.session_state:
    st.session_state.df_original = df.copy()

# Always start fresh from original data
df_filtered = st.session_state.df_original.copy()

# Date Filter
if date_col:
    st.sidebar.subheader("📅 Date Filter")
    try:
        # Get min and max dates from original data
        min_date = pd.Timestamp(st.session_state.df_original[date_col].min())
        max_date = pd.Timestamp(st.session_state.df_original[date_col].max())
        
        if pd.notna(min_date) and pd.notna(max_date):
            # Checkbox to use all dates
            use_all_dates = st.sidebar.checkbox("Use All Dates", value=True, key='use_all_dates_cb')
            
            if not use_all_dates:
                # Date range selector with proper handling
                col1, col2 = st.sidebar.columns(2)
                
                with col1:
                    start_date_input = st.date_input(
                        "Start",
                        value=min_date.date(),
                        min_value=min_date.date(),
                        max_value=max_date.date(),
                        key='start_date_input'
                    )
                
                with col2:
                    end_date_input = st.date_input(
                        "End",
                        value=max_date.date(),
                        min_value=min_date.date(),
                        max_value=max_date.date(),
                        key='end_date_input'
                    )
                
                # Convert to timestamps
                start_date = pd.Timestamp(start_date_input)
                end_date = pd.Timestamp(end_date_input) + pd.Timedelta(days=1)  # Include end date
                
                # Apply date filter
                df_filtered = df_filtered[(df_filtered[date_col] >= start_date) & (df_filtered[date_col] < end_date)]
                
                date_diff = (end_date - start_date).days
                st.sidebar.success(f"✅ {date_diff} days")
            else:
                date_range_days = (max_date - min_date).days
                st.sidebar.info(f"📅 {date_range_days} days (all)")
    except Exception as e:
        st.sidebar.error(f"Date error: {str(e)}")

# Country Filter
if country_col:
    st.sidebar.subheader("🌐 Country Filter")
    try:
        # Get countries from current filtered data
        all_countries = sorted([str(c) for c in df_filtered[country_col].dropna().unique() if str(c).strip()])
        
        if len(all_countries) > 0:
            # "All" checkbox
            use_all_countries = st.sidebar.checkbox(
                "Use All Countries", 
                value=True, 
                key='use_all_countries_cb'
            )
            
            if not use_all_countries:
                selected_countries = st.sidebar.multiselect(
                    "Choose Countries",
                    options=all_countries,
                    default=all_countries[:min(5, len(all_countries))],
                    key='country_select'
                )
                
                if selected_countries:
                    df_filtered = df_filtered[df_filtered[country_col].isin(selected_countries)]
                    st.sidebar.success(f"✅ {len(selected_countries)}/{len(all_countries)}")
                else:
                    st.sidebar.warning("⚠️ Select countries")
            else:
                st.sidebar.info(f"🌐 {len(all_countries)} countries")
        else:
            st.sidebar.warning("No countries in data")
    except Exception as e:
        st.sidebar.error(f"Country error: {str(e)}")

# Apply filtered data to main dataframe
df = df_filtered.copy()

# Show filter stats
st.sidebar.markdown("---")
total_records = len(st.session_state.df_original)
active_records = len(df)
filter_pct = (active_records / total_records * 100) if total_records > 0 else 0

st.sidebar.metric("📊 Active", f"{active_records:,}")
st.sidebar.metric("📊 Total", f"{total_records:,}")
st.sidebar.metric("📊 Showing", f"{filter_pct:.1f}%")

# KEY METRICS

st.header("📊 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if country_col:
        st.metric("🌍 Countries", f"{df[country_col].nunique():,}")
    else:
        st.metric("🌍 Countries", "N/A")

with col2:
    if location_col:
        st.metric("📍 Locations", f"{df[location_col].nunique():,}")
    else:
        st.metric("📍 Locations", "N/A")

with col3:
    if temp_col and temp_col in df.columns:
        avg_temp = df[temp_col].mean()
        if pd.notna(avg_temp):
            st.metric("🌡️ Avg Temp", f"{avg_temp:.1f}°C")
        else:
            st.metric("🌡️ Avg Temp", "N/A")
    else:
        st.metric("🌡️ Avg Temp", "N/A")

with col4:
    if wind_col and wind_col in df.columns:
        avg_wind = df[wind_col].mean()
        if pd.notna(avg_wind):
            st.metric("💨 Avg Wind", f"{avg_wind:.1f}")
        else:
            st.metric("💨 Avg Wind", "N/A")
    else:
        st.metric("💨 Avg Wind", "N/A")

with col5:
    if date_col:
        days_range = (df[date_col].max() - df[date_col].min()).days
        st.metric("📅 Days", f"{days_range}")
    else:
        st.metric("📅 Days", "N/A")

st.markdown("---")

# 1. STATISTICAL SUMMARY

if show_stats:
    st.header("1️⃣ Statistical Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Descriptive Statistics")
        numeric_cols = df.select_dtypes(include=[np.number]).columns[:8]
        st.dataframe(df[numeric_cols].describe().T.style.format("{:.2f}").background_gradient(cmap='YlOrRd'), width='stretch')
    
    with col2:
        st.subheader("🔢 Data Quality")
        missing_data = pd.DataFrame({
            'Column': df.columns,
            'Missing': df.isnull().sum(),
            'Percent': (df.isnull().sum() / len(df) * 100).round(2)
        })
        missing_data = missing_data[missing_data['Missing'] > 0].sort_values('Missing', ascending=False)
        
        if len(missing_data) > 0:
            st.dataframe(missing_data.style.background_gradient(cmap='Reds', subset=['Percent']))
        else:
            st.success("✅ No missing values detected!")
    
    st.markdown("---")

# 2. DISTRIBUTIONS

if show_distributions:
    st.header("2️⃣ Data Distributions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if temp_col:
            st.subheader("🌡️ Temperature Distribution")
            fig = px.histogram(df, x=temp_col, nbins=50, 
                             title="Temperature Distribution",
                             color_discrete_sequence=['#FF6B6B'])
            fig.add_vline(x=df[temp_col].mean(), line_dash="dash", 
                         line_color="green", annotation_text="Mean")
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if wind_col:
            st.subheader("💨 Wind Speed Distribution")
            fig = px.histogram(df, x=wind_col, nbins=50,
                             title="Wind Speed Distribution",
                             color_discrete_sequence=['#4ECDC4'])
            fig.add_vline(x=df[wind_col].mean(), line_dash="dash",
                         line_color="red", annotation_text="Mean")
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Additional distributions
    col1, col2 = st.columns(2)
    
    with col1:
        if pressure_col:
            st.subheader("🔽 Pressure Distribution")
            fig = px.box(df, y=pressure_col, 
                        title="Pressure Box Plot",
                        color_discrete_sequence=['#95E1D3'])
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if humidity_col:
            st.subheader("💧 Humidity Distribution")
            fig = px.violin(df, y=humidity_col,
                           box=True,
                           title="Humidity Violin Plot",
                           color_discrete_sequence=['#F38181'])
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

# 3. EXTREME EVENTS

if show_extremes:
    st.header("3️⃣ Extreme Weather Events Detection")
    
    # Threshold selector
    sigma_threshold = st.slider("Detection Threshold (Standard Deviations)", 1.0, 4.0, 3.0, 0.5)
    
    extreme_results = {}
    
    # Temperature extremes
    if temp_col:
        extreme_high_temp, extreme_low_temp, upper_temp, lower_temp = detect_extreme_events(df, temp_col, sigma_threshold)
        extreme_results['Temperature'] = {
            'high': len(extreme_high_temp),
            'low': len(extreme_low_temp),
            'high_data': extreme_high_temp,
            'low_data': extreme_low_temp,
            'upper': upper_temp,
            'lower': lower_temp
        }
    
    # Wind extremes
    if wind_col:
        extreme_high_wind, extreme_low_wind, upper_wind, lower_wind = detect_extreme_events(df, wind_col, sigma_threshold)
        extreme_results['Wind'] = {
            'high': len(extreme_high_wind),
            'low': len(extreme_low_wind),
            'high_data': extreme_high_wind,
            'low_data': extreme_low_wind,
            'upper': upper_wind,
            'lower': lower_wind
        }
    
    # Display metrics
    if len(extreme_results) > 0:
        cols = st.columns(len(extreme_results))
        for idx, (var_name, data) in enumerate(extreme_results.items()):
            with cols[idx]:
                total = data['high'] + data['low']
                percentage = (total / len(df) * 100) if len(df) > 0 else 0
                st.metric(
                    f"🔥 {var_name} Extremes",
                    f"{total:,}",
                    delta=f"{percentage:.2f}%"
                )
    
    # Visualization
    col1, col2 = st.columns(2)
    
    with col1:
        if temp_col:
            st.subheader("🌡️ Temperature Extremes")
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=df[temp_col], nbinsx=50, name='All Data', 
                                      marker_color='lightblue'))
            
            if len(extreme_results['Temperature']['high_data']) > 0:
                fig.add_trace(go.Histogram(x=extreme_results['Temperature']['high_data'][temp_col],
                                          nbinsx=50, name='Extreme High',
                                          marker_color='red', opacity=0.7))
            if len(extreme_results['Temperature']['low_data']) > 0:
                fig.add_trace(go.Histogram(x=extreme_results['Temperature']['low_data'][temp_col],
                                          nbinsx=50, name='Extreme Low',
                                          marker_color='blue', opacity=0.7))
            
            fig.add_vline(x=extreme_results['Temperature']['upper'], line_dash="dash",
                         line_color="red", annotation_text="Upper Threshold")
            fig.add_vline(x=extreme_results['Temperature']['lower'], line_dash="dash",
                         line_color="blue", annotation_text="Lower Threshold")
            
            fig.update_layout(title="Temperature with Extreme Thresholds",
                            xaxis_title=temp_col, yaxis_title="Frequency",
                            height=400, barmode='overlay')
            st.plotly_chart(fig, width='stretch')
    
    with col2:
        if wind_col:
            st.subheader("💨 Wind Speed Extremes")
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=df[wind_col], nbinsx=50, name='All Data',
                                      marker_color='lightgreen'))
            
            if len(extreme_results['Wind']['high_data']) > 0:
                fig.add_trace(go.Histogram(x=extreme_results['Wind']['high_data'][wind_col],
                                          nbinsx=50, name='Extreme High',
                                          marker_color='darkred', opacity=0.7))
            
            fig.add_vline(x=extreme_results['Wind']['upper'], line_dash="dash",
                         line_color="red", annotation_text="Upper Threshold")
            
            fig.update_layout(title="Wind Speed with Extreme Threshold",
                            xaxis_title=wind_col, yaxis_title="Frequency",
                            height=400, barmode='overlay')
            st.plotly_chart(fig, width='stretch')
    
    # Extreme events table
    st.subheader("📋 Recent Extreme Events")
    tab1, tab2 = st.tabs(["🔴 High Temperature", "🔵 Low Temperature"])
    
    with tab1:
        if temp_col and len(extreme_results['Temperature']['high_data']) > 0:
            display_cols = [col for col in [date_col, country_col, location_col, temp_col] if col and col in df.columns]
            st.dataframe(
                extreme_results['Temperature']['high_data'][display_cols].head(20).style.background_gradient(cmap='Reds', subset=[temp_col]),
                use_container_width=True
            )
    
    with tab2:
        if temp_col and len(extreme_results['Temperature']['low_data']) > 0:
            display_cols = [col for col in [date_col, country_col, location_col, temp_col] if col and col in df.columns]
            st.dataframe(
                extreme_results['Temperature']['low_data'][display_cols].head(20).style.background_gradient(cmap='Blues', subset=[temp_col]),
                use_container_width=True
            )
    
    st.markdown("---")

# 4. REGIONAL COMPARISON

if show_regional and country_col:
    st.header("4️⃣ Regional Comparison")
    
    # Top N selector
    top_n = st.slider("Number of Top Countries", 5, 30, 15)
    
    # Aggregate by country
    if temp_col and wind_col:
        country_stats = df.groupby(country_col).agg({
            temp_col: ['mean', 'std', 'min', 'max'],
            wind_col: ['mean', 'std'],
            country_col: 'count'
        }).reset_index()
        
        country_stats.columns = ['country', 'temp_mean', 'temp_std', 'temp_min', 'temp_max',
                                'wind_mean', 'wind_std', 'count']
        country_stats = country_stats.sort_values('temp_mean', ascending=False).head(top_n)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"🌡️ Top {top_n} Countries by Temperature")
            fig = px.bar(country_stats, x='country', y='temp_mean',
                        error_y='temp_std',
                        title="Average Temperature by Country",
                        color='temp_mean',
                        color_continuous_scale='RdYlBu_r',
                        labels={'temp_mean': 'Avg Temperature', 'country': 'Country'})
            fig.update_xaxes(tickangle=-45)
            fig.update_layout(height=450)
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            st.subheader(f"💨 Wind Speed Comparison")
            fig = px.scatter(country_stats, x='temp_mean', y='wind_mean',
                           size='count', hover_name='country',
                           title="Temperature vs Wind Speed by Country",
                           color='temp_mean',
                           color_continuous_scale='Viridis',
                           labels={'temp_mean': 'Avg Temperature', 'wind_mean': 'Avg Wind Speed'})
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)
        
        # Country statistics table
        st.subheader("📊 Country Statistics Table")
        st.dataframe(
            country_stats.style.format({
                'temp_mean': '{:.2f}',
                'temp_std': '{:.2f}',
                'temp_min': '{:.2f}',
                'temp_max': '{:.2f}',
                'wind_mean': '{:.2f}',
                'wind_std': '{:.2f}',
                'count': '{:,.0f}'
            }).background_gradient(cmap='RdYlGn', subset=['temp_mean']),
            use_container_width=True
        )
    
    st.markdown("---")

# 5. TIME SERIES ANALYSIS

if show_timeseries and date_col:
    st.header("5️⃣ Time Series Analysis")
    
    # Prepare time series data
    df_ts = df.copy()
    df_ts = df_ts.sort_values(date_col)
    
    # Aggregation selector
    agg_method = st.selectbox("Aggregation Method", ['Daily', 'Weekly', 'Monthly'])
    
    if agg_method == 'Daily':
        freq = 'D'
    elif agg_method == 'Weekly':
        freq = 'W'
    else:
        freq = 'M'
    
    col1, col2 = st.columns(2)
    
    with col1:
        if temp_col:
            st.subheader("🌡️ Temperature Trend")
            ts_data = df_ts.set_index(date_col)[temp_col].resample(freq).mean().dropna()
            
            if len(ts_data) > 1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=ts_data.index, y=ts_data.values,
                                        mode='lines+markers',
                                        name='Temperature',
                                        line=dict(color='#FF6B6B', width=2)))
                
                # Add trend line with error handling
                try:
                    if len(ts_data) >= 3:  # Need at least 3 points for trend
                        x_numeric = np.arange(len(ts_data))
                        y_values = ts_data.values
                        
                        # Remove any NaN or infinite values
                        mask = np.isfinite(y_values)
                        if mask.sum() >= 2:
                            z = np.polyfit(x_numeric[mask], y_values[mask], 1)
                            p = np.poly1d(z)
                            fig.add_trace(go.Scatter(x=ts_data.index, y=p(x_numeric),
                                                    mode='lines',
                                                    name='Trend',
                                                    line=dict(color='red', width=2, dash='dash')))
                except Exception as e:
                    st.warning(f"Could not calculate trend line: {str(e)}")
                
                fig.update_layout(title=f"{agg_method} Average Temperature",
                                xaxis_title="Date", yaxis_title=temp_col,
                                height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Not enough data points for time series visualization")
    
    with col2:
        if wind_col:
            st.subheader("💨 Wind Speed Trend")
            ts_data = df_ts.set_index(date_col)[wind_col].resample(freq).mean()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ts_data.index, y=ts_data.values,
                                    mode='lines+markers',
                                    name='Wind Speed',
                                    line=dict(color='#4ECDC4', width=2),
                                    fill='tozeroy'))
            
            fig.update_layout(title=f"{agg_method} Average Wind Speed",
                            xaxis_title="Date", yaxis_title=wind_col,
                            height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Seasonal patterns
    if temp_col:
        st.subheader("📅 Seasonal Patterns")
        df_ts['month'] = df_ts[date_col].dt.month
        df_ts['season'] = df_ts['month'].map({
            12: 'Winter', 1: 'Winter', 2: 'Winter',
            3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer',
            9: 'Fall', 10: 'Fall', 11: 'Fall'
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_avg = df_ts.groupby('month')[temp_col].mean().reset_index()
            monthly_avg.columns = ['month', 'avg_temp']
            
            fig = px.line(
                monthly_avg,
                x='month',
                y='avg_temp',
                markers=True,
                title="Average Temperature by Month",
                labels={'month': 'Month', 'avg_temp': temp_col}
            )
            fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)
            st.plotly_chart(fig, width='stretch')

        with col2:
            fig = px.box(df_ts, x='season', y=temp_col,
                        title="Temperature by Season",
                        color='season',
                        category_orders={'season': ['Winter', 'Spring', 'Summer', 'Fall']})
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

# 6. CORRELATIONS

if show_correlations:
    st.header("6️⃣ Correlation Analysis")
    
    # Select numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns[:10]
    
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🔗 Correlation Heatmap")
            fig = px.imshow(corr_matrix,
                           text_auto='.2f',
                           aspect='auto',
                           color_continuous_scale='RdBu_r',
                           zmin=-1, zmax=1,
                           title="Variable Correlation Matrix")
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("💪 Strong Correlations")
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > 0.7:
                        strong_corr.append({
                            'Variable 1': corr_matrix.columns[i],
                            'Variable 2': corr_matrix.columns[j],
                            'Correlation': corr_matrix.iloc[i, j]
                        })
            
            if strong_corr:
                st.dataframe(
                    pd.DataFrame(strong_corr).style.background_gradient(cmap='RdYlGn', subset=['Correlation']),
                    use_container_width=True
                )
            else:
                st.info("No strong correlations (|r| > 0.7) found")
        
        # Scatter plot for top correlation
        if temp_col and wind_col:
            st.subheader("📊 Temperature vs Wind Speed")
            sample_df = df[[temp_col, wind_col]].dropna().sample(min(5000, len(df)))
            
            fig = px.scatter(sample_df, x=temp_col, y=wind_col,
                           opacity=0.5,
                           trendline='ols',
                           title=f"{temp_col} vs {wind_col}",
                           color=temp_col,
                           color_continuous_scale='Turbo')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

# 7. INTERACTIVE MAPS

if show_maps and country_col:
    st.header("7️⃣ Interactive Geographic Visualizations")
    
    if temp_col:
        # Choropleth map
        country_avg = df.groupby(country_col)[temp_col].mean().reset_index()
        country_avg.columns = ['country', 'avg_temp']
        
        st.subheader("🗺️ Global Temperature Distribution")
        fig = px.choropleth(
            country_avg,
            locations='country',
            locationmode='country names',
            color='avg_temp',
            hover_name='country',
            color_continuous_scale='RdYlBu_r',
            title="Average Temperature by Country",
            labels={'avg_temp': 'Avg Temperature (°C)'}
        )
        fig.update_geos(showcountries=True, countrycolor="lightgray")
        fig.update_layout(height=600, margin={"r":0,"t":50,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        
        # Scatter geo map
        if location_col and 'latitude' in df.columns and 'longitude' in df.columns:
            st.subheader("📍 Location-based Temperature Map")
            sample_df = df[[location_col, 'latitude', 'longitude', temp_col]].dropna().sample(min(1000, len(df)))
            
            # Convert temperature to absolute values for size (handling negative temps)
            sample_df['temp_size'] = np.abs(sample_df[temp_col] - sample_df[temp_col].min()) + 1
            
            fig = px.scatter_geo(
                sample_df,
                lat='latitude',
                lon='longitude',
                color=temp_col,
                hover_name=location_col,
                size='temp_size',
                color_continuous_scale='RdYlBu_r',
                title="Temperature Distribution by Location",
                projection='natural earth'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

# FOOTER

st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; color: white;'>
        <h3>🌍 ClimateScope Dashboard - Milestone 2</h3>
        <p>Complete Statistical Analysis & Extreme Weather Detection</p>
        <p><strong>Last Updated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>Total Records Analyzed:</strong> {len(df):,}</p>
        <p style='margin-top: 10px; font-size: 0.9em;'>
            ✅ Statistical Analysis | 📊 Distributions | 🔥 Extreme Events<br>
            🗺️ Geographic Maps | 📈 Time Series | 🔗 Correlations
        </p>
    </div>
""", unsafe_allow_html=True)

# EXPORT SECTION

st.markdown("---")
st.header("💾 Export Analysis Results")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Download Statistics Summary"):
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary = df[numeric_cols].describe()
            csv = summary.to_csv()
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"statistics_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No numeric data available to export")

with col2:
    if temp_col and st.button("🔥 Download Extreme Events"):
        if 'extreme_results' in locals() and len(extreme_results) > 0:
            extreme_high_temp = extreme_results.get('Temperature', {}).get('high_data', pd.DataFrame())
            if len(extreme_high_temp) > 0:
                csv = extreme_high_temp.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"extreme_events_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No extreme events to export")
        else:
            st.warning("Please view Extreme Events section first")

with col3:
    if country_col and st.button("🌍 Download Country Stats"):
        if temp_col and wind_col:
            try:
                country_stats = df.groupby(country_col).agg({
                    temp_col: ['mean', 'std', 'min', 'max'],
                    wind_col: ['mean', 'std']
                }).reset_index()
                csv = country_stats.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"country_statistics_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error generating country stats: {str(e)}")
        else:
            st.warning("Temperature and wind data required")

# INSIGHTS & RECOMMENDATIONS

st.markdown("---")
st.header("💡 Key Insights & Recommendations")

insights_col1, insights_col2 = st.columns(2)

with insights_col1:
    st.subheader("🎯 Key Findings")
    
    findings = []
    
    if temp_col:
        avg_temp = df[temp_col].mean()
        std_temp = df[temp_col].std()
        if pd.notna(avg_temp) and pd.notna(std_temp):
            findings.append(f"• Average global temperature: **{avg_temp:.2f}°C** (σ = {std_temp:.2f})")
        
        if 'Temperature' in extreme_results:
            total_extremes = extreme_results['Temperature']['high'] + extreme_results['Temperature']['low']
            percentage = (total_extremes / len(df) * 100) if len(df) > 0 else 0
            findings.append(f"• Detected **{total_extremes:,}** temperature extreme events ({percentage:.2f}%)")
    
    if country_col:
        num_countries = df[country_col].nunique()
        findings.append(f"• Data covers **{num_countries}** countries/regions")
    
    if date_col:
        date_range = (df[date_col].max() - df[date_col].min()).days
        findings.append(f"• Time period: **{date_range}** days of data")
    
    if wind_col:
        avg_wind = df[wind_col].mean()
        max_wind = df[wind_col].max()
        findings.append(f"• Wind speed ranges from 0 to **{max_wind:.1f}** (avg: {avg_wind:.1f})")
    
    for finding in findings:
        st.markdown(finding)

with insights_col2:
    st.subheader("📋 Recommendations")
    
    recommendations = [
        "• Focus monitoring on regions with high extreme event frequency",
        "• Investigate seasonal patterns for predictive modeling",
        "• Consider climate zone classification for better analysis",
        "• Implement real-time alerting for extreme weather conditions",
        "• Conduct deeper analysis on regional climate trends",
        "• Correlate weather patterns with geographic features"
    ]
    
    for rec in recommendations:
        st.markdown(rec)

# METHODOLOGY NOTES

with st.expander("📚 Methodology & Technical Notes"):
    st.markdown("""
    ### Statistical Methods Used:
    
    **1. Extreme Event Detection:**
    - Uses **z-score method** (standard deviations from mean)
    - Default threshold: 3σ (99.7% confidence interval)
    - Events beyond threshold classified as extreme
    
    **2. Aggregation Techniques:**
    - Daily: Raw daily averages
    - Weekly: 7-day rolling averages
    - Monthly: Calendar month aggregations
    
    **3. Correlation Analysis:**
    - Pearson correlation coefficient
    - Range: -1 (perfect negative) to +1 (perfect positive)
    - Strong correlation: |r| > 0.7
    
    **4. Regional Comparison:**
    - Country-level aggregation
    - Mean, standard deviation, min/max calculations
    - Statistical significance testing
    
    **5. Data Quality:**
    - Missing value detection and reporting
    - Outlier identification using IQR method
    - Data validation checks
    
    ### Visualization Libraries:
    - **Plotly**: Interactive charts and maps
    - **Matplotlib/Seaborn**: Static statistical plots
    - **Streamlit**: Dashboard framework
    
    ### Performance Optimizations:
    - Data sampling for large datasets (>5000 records)
    - Efficient aggregation using pandas groupby
    - Cached data loading with @st.cache_data
    """)

# DASHBOARD USAGE GUIDE

with st.expander("❓ How to Use This Dashboard"):
    st.markdown("""
    ### Navigation Guide:
    
    **Sidebar Controls:**
    - ✅ Check/uncheck sections to show/hide
    - 📅 Filter by date range
    - 🌐 Filter by country
    - 🎚️ Adjust extreme event thresholds
    
    **Interactive Features:**
    - 🖱️ Hover over charts for detailed information
    - 🔍 Zoom and pan on visualizations
    - 📊 Click legend items to show/hide series
    - 💾 Download data using export buttons
    
    **Analysis Sections:**
    1. **Statistical Summary**: Overall data statistics
    2. **Distributions**: Data distribution patterns
    3. **Extreme Events**: Anomaly detection and analysis
    4. **Regional Comparison**: Country-level comparisons
    5. **Time Series**: Temporal trends and patterns
    6. **Correlations**: Variable relationships
    7. **Maps**: Geographic visualizations
    
    **Tips:**
    - Start with Statistical Summary for overview
    - Use filters to focus on specific regions/periods
    - Check Extreme Events for anomalies
    - Explore Correlations to understand relationships
    - Use Maps for geographic context
    """)

# DATA SAMPLE PREVIEW

with st.expander("👀 View Raw Data Sample"):
    st.subheader("Dataset Preview (First 100 rows)")
    st.dataframe(df.head(100), use_container_width=True)
    
    st.subheader("Dataset Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    st.subheader("Column Data Types")
    dtypes_df = pd.DataFrame({
        'Column': df.columns.tolist(),
        'Data Type': [str(dtype) for dtype in df.dtypes.values],  # Convert to string
        'Non-Null Count': df.count().values.tolist(),
        'Null Count': df.isnull().sum().values.tolist()
    })
    st.dataframe(dtypes_df, width='stretch')

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; padding: 10px;'>
        <p>Built with ❤️ using Streamlit, Plotly, and Pandas</p>
        <p>ClimateScope © 2024 | Global Weather Analytics Platform</p>
    </div>
""", unsafe_allow_html=True)