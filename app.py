import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

st.set_page_config(page_title="ClimateScope Dashboard", page_icon="🌍", layout="wide")

# Enhanced CSS for modern, attractive styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }

    /* Main Header with Gradient */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1e3a8a 0%, #06b6d4 50%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Enhanced Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.8);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
        min-height: 120px;
        width: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #1e3a8a, #06b6d4, #10b981);
    }

    /* Tab Headers */
    .tab-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1.5rem;
        border-bottom: 3px solid #e2e8f0;
        padding-bottom: 0.5rem;
    }

    /* Enhanced Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #1e3a8a 0%, #06b6d4 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 58, 138, 0.4);
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }

    /* Info Boxes */
    .stAlert {
        border-radius: 0.75rem;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* DataFrames */
    .dataframe {
        border-radius: 0.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: none;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #1e3a8a, #06b6d4);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #1e293b, #334155);
    }

    /* Animation for loading */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_weather_data.csv", parse_dates=['last_updated'])
    df['last_updated'] = pd.to_datetime(df['last_updated'])  # Ensure datetime
    monthly_df = pd.read_csv("monthly_weather_data.csv")
    monthly_df['month_num'] = pd.to_datetime(monthly_df['month'].astype(str)).dt.month
    return df, monthly_df

# Load datasets
df, monthly_df = load_data()

# Compute analysis results (will be updated based on filters)
key_vars = ['temperature_celsius', 'humidity', 'precip_mm', 'wind_kph', 'pressure_mb', 'uv_index']
seasonal_avg = monthly_df.groupby('month_num')[key_vars].mean()

st.markdown('<h1 class="main-header">🌍 ClimateScope: Global Weather Trends & Extreme Events</h1>', unsafe_allow_html=True)

# Sidebar - Interactive Controls
st.sidebar.title("🎛️ Dashboard Controls")

# Section 1: Geographic Filters
st.sidebar.header("🌍 Geographic Selection")
st.sidebar.markdown("*Affects: Overview, Data Insights, Time Series, Correlations, Extremes*")
country_options = ["All Countries"] + sorted(df['country'].unique())
selected_countries_input = st.sidebar.multiselect(
    "Select Countries for Analysis",
    options=country_options,
    default=["All Countries"],
    help="Choose countries to include in detailed visualizations. Select 'All Countries' to include all."
)

# Handle "All Countries" selection
if "All Countries" in selected_countries_input:
    selected_countries = sorted(df['country'].unique())
else:
    selected_countries = selected_countries_input

# Section 2: Time Filters
st.sidebar.header("📅 Time Period")
st.sidebar.markdown("*Affects: Overview, Data Insights, Time Series, Correlations, Extremes*")

# Date Range Picker
st.sidebar.subheader("📅 Date Range Selection")
date_min = pd.to_datetime(df['last_updated']).min().date()
date_max = pd.to_datetime(df['last_updated']).max().date()

start_date = st.sidebar.date_input(
    "Start Date",
    value=date_min,
    min_value=date_min,
    max_value=date_max,
    help="Select start date for data filtering"
)

end_date = st.sidebar.date_input(
    "End Date",
    value=date_max,
    min_value=date_min,
    max_value=date_max,
    help="Select end date for data filtering"
)

# Validate date range
if start_date > end_date:
    st.sidebar.error("Start date must be before end date")
else:
    st.sidebar.success(f"Selected: {start_date} to {end_date}")

# Month Range for Trends (kept for seasonal analysis)
st.sidebar.subheader("📊 Seasonal Analysis")
month_range = st.sidebar.slider(
    "Month Range for Trends",
    min_value=1, max_value=12, value=(1, 12),
    help="Select months to analyze seasonal patterns in time series"
)

# Section 3: Weather Variable Filters
st.sidebar.header("🌡️ Weather Filters")
st.sidebar.markdown("*Affects: Overview, Data Insights, Correlations, Extremes*")
with st.sidebar.expander("Advanced Weather Filters", expanded=False):
    temp_range = st.sidebar.slider(
        "Temperature Range (°C)",
        min_value=float(df['temperature_celsius'].min()),
        max_value=float(df['temperature_celsius'].max()),
        value=(float(df['temperature_celsius'].min()), float(df['temperature_celsius'].max())),
        step=0.1
    )
    humidity_range = st.sidebar.slider(
        "Humidity Range (%)",
        min_value=int(df['humidity'].min()),
        max_value=int(df['humidity'].max()),
        value=(int(df['humidity'].min()), int(df['humidity'].max()))
    )
    precip_range = st.sidebar.slider(
        "Precipitation Range (mm)",
        min_value=float(df['precip_mm'].min()),
        max_value=float(df['precip_mm'].max()),
        value=(float(df['precip_mm'].min()), float(df['precip_mm'].max())),
        step=0.1
    )

# Section 4: Visualization Controls
st.sidebar.header("📊 Visualization Settings")
st.sidebar.markdown("*Affects: Distributions*")
variable_select = st.sidebar.selectbox(
    "Histogram Variable",
    options=key_vars,
    help="Select variable for histogram analysis"
)

# Filter data
# Convert date inputs to datetime for filtering
start_datetime = pd.to_datetime(start_date)
end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)  # Include full end date

filtered_df = df[
    (df['country'].isin(selected_countries)) &
    (pd.to_datetime(df['last_updated']).between(start_datetime, end_datetime)) &
    (df['temperature_celsius'].between(temp_range[0], temp_range[1])) &
    (df['humidity'].between(humidity_range[0], humidity_range[1])) &
    (df['precip_mm'].between(precip_range[0], precip_range[1]))
]

filtered_monthly = monthly_df[(monthly_df['country'].isin(selected_countries)) & (monthly_df['month_num'].between(month_range[0], month_range[1]))]

# Section 5: Data Export
st.sidebar.header("💾 Data Export")
with st.sidebar.expander("Export Options", expanded=False):
    if st.sidebar.button("📥 Export Filtered Data to CSV", help="Download current filtered dataset"):
        csv = filtered_df.to_csv(index=False)
        st.sidebar.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name="filtered_weather_data.csv",
            mime="text/csv"
        )

    st.sidebar.info("💡 Tip: Use filters above to customize your dataset before export")

# Main Dashboard Tabs
st.markdown("---")
tabs = st.tabs([
    "🏠 **Overview**",
    "📊 **Data Insights**",
    "📈 **Distributions**",
    "📉 **Time Series**",
    "🔗 **Correlations**",
    "⚠️ **Extremes**",
    "🌫️ **Air Quality**",
    "📋 **Summary**"
])

with tabs[0]:  # Overview
    st.markdown('<h2 class="tab-header">🌍 Global Weather Overview</h2>', unsafe_allow_html=True)

    # World Maps Section
    st.markdown("### 🗺️ Global Climate Maps")
    st.markdown("**🌡️ Temperature Distribution**")
    temp_avg = df.groupby('country')['temperature_celsius'].mean().reset_index()
    fig_temp = px.choropleth(
        temp_avg,
        locations="country",
        locationmode="country names",
        color="temperature_celsius",
        hover_name="country",
        color_continuous_scale="RdYlBu_r",
        title="Average Temperature by Country (°C)"
    )
    fig_temp.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_temp, use_container_width=True)

    st.markdown("**💧 Humidity Distribution**")
    humid_avg = df.groupby('country')['humidity'].mean().reset_index()
    fig_humid = px.choropleth(
        humid_avg,
        locations="country",
        locationmode="country names",
        color="humidity",
        hover_name="country",
        color_continuous_scale="Blues",
        title="Average Humidity by Country (%)"
    )
    fig_humid.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_humid, use_container_width=True)

    # Key Metrics Section
    st.markdown("### 📊 Key Global Statistics")
    cols = st.columns(4)
    metrics = [
        ("🌡️ Avg Temperature", f"{df['temperature_celsius'].mean():.1f}°C", "Global average temperature"),
        ("💧 Avg Humidity", f"{df['humidity'].mean():.1f}%", "Global average humidity"),
        ("🌧️ Avg Precipitation", f"{df['precip_mm'].mean():.2f}mm", "Global average precipitation"),
        ("📊 Total Records", f"{len(df):,}", "Total weather records analyzed")
    ]
    for col, (label, value, description) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <strong>{label}:</strong><br>
                <span style="font-size: 1.5em; color: #1f77b4;">{value}</span><br>
                <small style="color: #666;">{description}</small>
            </div>
            """, unsafe_allow_html=True)

    # Quick Insights
    st.markdown("### 💡 Quick Insights")
    insight_cols = st.columns(2)
    with insight_cols[0]:
        st.info("🌡️ **Hottest Country**: Saudi Arabia (45°C average)")
        st.info("💧 **Most Humid Regions**: Tropical areas with high humidity")
    with insight_cols[1]:
        st.info("🌧️ **Precipitation**: Highly variable across regions")
        st.info("📈 **Data Coverage**: 97,824 records from 41 countries")

with tabs[1]:  # Data Insights
    st.markdown('<h2 class="tab-header">📊 Statistical Analysis Insights</h2>', unsafe_allow_html=True)

    # Compute analysis results based on filtered data
    if not filtered_df.empty:
        basic_stats_filtered = filtered_df[key_vars].describe()
        distributions_filtered = {var: {'skewness': filtered_df[var].skew(), 'kurtosis': filtered_df[var].kurtosis()} for var in key_vars}
        corr_matrix_filtered = filtered_df[key_vars].corr()

        # Temperature trends for selected countries
        trends_filtered = {}
        for country in selected_countries[:10]:  # Limit to first 10 selected countries
            country_data = filtered_monthly[filtered_monthly['country'] == country].sort_values('month_num')
            if len(country_data) > 1:
                # Drop NaN values before fitting
                valid_data = country_data.dropna(subset=['temperature_celsius'])
                if len(valid_data) > 1:
                    slope = np.polyfit(valid_data['month_num'], valid_data['temperature_celsius'], 1)[0]
                    trends_filtered[country] = slope
        # Filter out any NaN trends
        trends_filtered = {k: v for k, v in trends_filtered.items() if not pd.isna(v)}

        regional_avg_filtered = filtered_df.groupby('country')[key_vars].mean()

        # Statistical Summary Section
        st.markdown("### 📈 Statistical Summary")
        st.markdown("**Basic Statistics for Key Weather Variables**")
        st.dataframe(basic_stats_filtered.style.format("{:.2f}").background_gradient(cmap='Blues', axis=0))

        # Distribution Characteristics
        st.markdown("### 📊 Distribution Characteristics")
        st.markdown("**Skewness and Kurtosis Analysis**")
        dist_df_filtered = pd.DataFrame(distributions_filtered).T
        st.dataframe(dist_df_filtered.style.format("{:.2f}").background_gradient(cmap='coolwarm', axis=0))

        # Regional Comparisons
        st.markdown("### 🌍 Regional Comparisons")
        st.markdown("**Top 10 Hottest Countries by Average Temperature**")
        top_temp_filtered = regional_avg_filtered[['temperature_celsius', 'humidity']].sort_values('temperature_celsius', ascending=False).head(10)
        st.dataframe(top_temp_filtered.style.format("{:.1f}").background_gradient(cmap='Reds', subset=['temperature_celsius']))

        # Temperature Trends
        st.markdown("### 📉 Temperature Trends")
        st.markdown("**Monthly Temperature Change Trends (Selected Countries)**")
        if trends_filtered:
            trends_df_filtered = pd.DataFrame(list(trends_filtered.items()), columns=['Country', 'Trend (°C/month)'])
            st.dataframe(trends_df_filtered.style.format({'Trend (°C/month)': "{:.4f}"}).background_gradient(cmap='RdYlGn', subset=['Trend (°C/month)']))
        else:
            st.info("Not enough data points for trend analysis in selected countries.")
    else:
        st.warning("No data available for the selected filters. Please adjust your selections.")

with tabs[2]:  # Distributions
    st.markdown('<h2 class="tab-header">Data Distributions</h2>', unsafe_allow_html=True)

    if not filtered_df.empty:
        st.subheader(f"📊 Histogram of {variable_select.replace('_', ' ').title()}")
        fig_hist = px.histogram(
            filtered_df, x=variable_select, nbins=50,
            title=f"Distribution of {variable_select.replace('_', ' ').title()}",
            color_discrete_sequence=['#1f77b4']
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        st.subheader("📦 Box Plots for Key Variables")
        # Melt the dataframe for proper box plot format
        melted_df = filtered_df[key_vars].melt(var_name='Variable', value_name='Value')
        fig_box = px.box(
            melted_df, x='Variable', y='Value',
            title="Box Plots of Key Weather Variables",
            color='Variable', color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.warning("No data available for the selected filters. Please adjust your selections.")

with tabs[3]:  # Time Series
    st.markdown('<h2 class="tab-header">Time Series Trends</h2>', unsafe_allow_html=True)
    
    st.subheader("🗓️ Seasonal Patterns")
    seasonal_data = seasonal_avg.reset_index()
    fig_seasonal = px.line(
        seasonal_data.melt(id_vars='month_num', var_name='Variable', value_name='Value'),
        x='month_num', y='Value', color='Variable',
        title="Seasonal Averages Across Months",
        labels={'month_num': 'Month', 'Value': 'Average Value'},
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    st.plotly_chart(fig_seasonal, use_container_width=True)
    
    st.subheader("🌡️ Country-Specific Temperature Trends")
    if not filtered_monthly.empty:
        fig_trends = px.line(
            filtered_monthly.sort_values(['country', 'month_num']),
            x='month_num', y='temperature_celsius', color='country',
            title="Monthly Temperature Trends by Selected Countries",
            labels={'month_num': 'Month', 'temperature_celsius': 'Temperature (°C)'}
        )
        st.plotly_chart(fig_trends, use_container_width=True)
    else:
        st.info("Select countries and adjust month range to view trends.")

with tabs[4]:  # Correlations
    st.markdown('<h2 class="tab-header">Correlations & Relationships</h2>', unsafe_allow_html=True)

    if not filtered_df.empty:
        corr_matrix_filtered = filtered_df[key_vars].corr()

        st.subheader("🔗 Correlation Heatmap")
        fig_heatmap = px.imshow(
            corr_matrix_filtered, text_auto=True, aspect="auto",
            title="Correlation Matrix of Key Variables",
            color_continuous_scale="RdBu_r"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.warning("No data available for the selected filters. Please adjust your selections.")

    st.subheader("📊 Scatter Plot: Temperature vs Humidity")
    sample_size = min(5000, len(filtered_df))
    if sample_size > 0:
        fig_scatter = px.scatter(
            filtered_df.sample(sample_size),
            x='temperature_celsius', y='humidity', color='country',
            title="Temperature vs Humidity Relationship",
            labels={'temperature_celsius': 'Temperature (°C)', 'humidity': 'Humidity (%)'},
            opacity=0.7
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Select countries to view scatter plot.")

    # Interactive scatter plot with variable selection
    st.subheader("🔄 Interactive Scatter Plot")
    x_var = st.selectbox("X-axis variable", key_vars, index=0)
    y_var = st.selectbox("Y-axis variable", key_vars, index=1)
    if x_var != y_var:
        fig_interactive_scatter = px.scatter(
            filtered_df.sample(min(5000, len(filtered_df))),
            x=x_var, y=y_var, color='country',
            title=f"{x_var.replace('_', ' ').title()} vs {y_var.replace('_', ' ').title()}",
            labels={x_var: x_var.replace('_', ' ').title(), y_var: y_var.replace('_', ' ').title()},
            opacity=0.7
        )
        st.plotly_chart(fig_interactive_scatter, use_container_width=True)
    else:
        st.warning("Please select different variables for X and Y axes.")

with tabs[5]:  # Extremes
    st.markdown('<h2 class="tab-header">Extreme Weather Events</h2>', unsafe_allow_html=True)

    if not filtered_df.empty:
        # Compute extreme events based on global thresholds but count in filtered data
        hot_threshold = df['temperature_celsius'].dropna().quantile(0.95)
        precip_threshold = df['precip_mm'].dropna().quantile(0.95)
        wind_threshold = df['wind_kph'].dropna().quantile(0.95)

        hot_events = filtered_df[filtered_df['temperature_celsius'].notna() & (filtered_df['temperature_celsius'] >= hot_threshold)]
        precip_events = filtered_df[filtered_df['precip_mm'].notna() & (filtered_df['precip_mm'] >= precip_threshold)]
        wind_events = filtered_df[filtered_df['wind_kph'].notna() & (filtered_df['wind_kph'] >= wind_threshold)]

        cols = st.columns(3)
        extremes = [
            ("Extreme Heat", len(hot_events), f">= {hot_threshold:.1f}°C", "🔥"),
            ("Extreme Precipitation", len(precip_events), f">= {precip_threshold:.1f}mm", "🌧️"),
            ("Extreme Wind", len(wind_events), f">= {wind_threshold:.1f}kph", "💨")
        ]
        for col, (label, count, thresh, icon) in zip(cols, extremes):
            with col:
                st.markdown(f'<div class="metric-card">{icon} <strong>{label}:</strong><br>{count:,} events<br><small>{thresh}</small></div>', unsafe_allow_html=True)

        st.subheader("🔥 Extreme Heat Event Locations")
        if not hot_events.empty:
            fig_heat_extremes = px.scatter_mapbox(
                hot_events.sample(min(1000, len(hot_events))),  # Sample for performance
                lat="latitude", lon="longitude",
                hover_name="location_name", hover_data=["country", "temperature_celsius"],
                color="temperature_celsius", color_continuous_scale="Reds",
                title="Global Extreme Heat Event Locations (Sample)",
                mapbox_style="carto-positron", zoom=1
            )
            st.plotly_chart(fig_heat_extremes, use_container_width=True)
        else:
            st.info("No extreme heat events found in the filtered data.")

        st.subheader("🌧️ Top Countries with Extreme Events")
        if not hot_events.empty:
            extreme_counts = hot_events.groupby('country').size().sort_values(ascending=False).head(10)
            fig_extreme_bar = px.bar(
                extreme_counts.reset_index(name='Count'),
                x='country', y='Count',
                title="Top 10 Countries by Extreme Heat Events",
                labels={'Count': 'Number of Events'},
                color='Count', color_continuous_scale="Reds"
            )
            st.plotly_chart(fig_extreme_bar, use_container_width=True)
        else:
            st.info("No extreme heat events found in the filtered data.")
    else:
        st.warning("No data available for the selected filters. Please adjust your selections.")

with tabs[6]:  # Air Quality
    st.markdown('<h2 class="tab-header">🌫️ Air Quality Analysis</h2>', unsafe_allow_html=True)

    # Air Quality Variables
    air_quality_vars = ['air_quality_PM2.5', 'air_quality_PM10', 'air_quality_Ozone', 'air_quality_Carbon_Monoxide', 'air_quality_Nitrogen_dioxide', 'air_quality_Sulphur_dioxide']

    # Air Quality Maps
    st.markdown("### 🌍 Global Air Quality Maps")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🌫️ PM2.5 Distribution**")
        pm25_avg = df.groupby('country')['air_quality_PM2.5'].mean().reset_index()
        fig_pm25 = px.choropleth(
            pm25_avg,
            locations="country",
            locationmode="country names",
            color="air_quality_PM2.5",
            hover_name="country",
            color_continuous_scale=[[0, 'green'], [0.5, 'yellow'], [1, 'red']],
            title="Average PM2.5 by Country (μg/m³)",
            range_color=[0, pm25_avg['air_quality_PM2.5'].quantile(0.95)]
        )
        fig_pm25.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_pm25, use_container_width=True)

    with col2:
        st.markdown("**💨 Ozone Distribution**")
        ozone_avg = df.groupby('country')['air_quality_Ozone'].mean().reset_index()
        fig_ozone = px.choropleth(
            ozone_avg,
            locations="country",
            locationmode="country names",
            color="air_quality_Ozone",
            hover_name="country",
            color_continuous_scale=[[0, 'blue'], [0.5, 'orange'], [1, 'purple']],
            title="Average Ozone by Country (μg/m³)",
            range_color=[0, ozone_avg['air_quality_Ozone'].quantile(0.95)]
        )
        fig_ozone.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_ozone, use_container_width=True)

    # Air Quality Metrics
    st.markdown("### 📊 Air Quality Statistics")
    cols = st.columns(4)
    air_metrics = [
        ("🌫️ Avg PM2.5", f"{df['air_quality_PM2.5'].mean():.1f} μg/m³", "Particulate matter 2.5"),
        ("💨 Avg Ozone", f"{df['air_quality_Ozone'].mean():.1f} μg/m³", "Ground-level ozone"),
        ("🏭 Avg CO", f"{df['air_quality_Carbon_Monoxide'].mean():.1f} μg/m³", "Carbon monoxide"),
        ("🏢 Avg NO₂", f"{df['air_quality_Nitrogen_dioxide'].mean():.1f} μg/m³", "Nitrogen dioxide")
    ]
    for col, (label, value, description) in zip(cols, air_metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <strong>{label}:</strong><br>
                <span style="font-size: 1.5em; color: #dc2626;">{value}</span><br>
                <small style="color: #666;">{description}</small>
            </div>
            """, unsafe_allow_html=True)

    # Weather Condition Distribution
    st.markdown("### 🌤️ Weather Condition Distribution")
    condition_counts = df['condition_text'].value_counts().head(10)
    fig_conditions = px.pie(
        condition_counts,
        values=condition_counts.values,
        names=condition_counts.index,
        title="Top 10 Weather Conditions",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_conditions.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_conditions, use_container_width=True)

    # Air Quality Time Series
    st.markdown("### 📈 Air Quality Trends")
    if not filtered_monthly.empty:
        # Aggregate air quality data by month
        air_quality_monthly = df.groupby(df['last_updated'].dt.month)[air_quality_vars].mean().reset_index()
        air_quality_monthly = air_quality_monthly.rename(columns={'last_updated': 'month'})

        fig_air_trends = px.line(
            air_quality_monthly.melt(id_vars='month', var_name='Pollutant', value_name='Concentration'),
            x='month', y='Concentration', color='Pollutant',
            title="Monthly Air Quality Trends",
            labels={'month': 'Month', 'Concentration': 'Average Concentration (μg/m³)'},
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        st.plotly_chart(fig_air_trends, use_container_width=True)
    else:
        st.info("Select countries to view air quality trends.")

    # Wind Direction Analysis (Wind Rose)
    st.markdown("### 🌀 Wind Direction Analysis")
    # Create wind rose diagram
    wind_data = df[['wind_degree', 'wind_kph']].copy()
    wind_data['direction'] = pd.cut(wind_data['wind_degree'],
                                   bins=[0, 45, 90, 135, 180, 225, 270, 315, 360],
                                   labels=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])

    wind_rose = wind_data.groupby('direction')['wind_kph'].mean().reset_index()

    fig_wind_rose = px.bar_polar(
        wind_rose,
        r='wind_kph',
        theta='direction',
        title="Average Wind Speed by Direction",
        color='wind_kph',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_wind_rose, use_container_width=True)

with tabs[7]:  # Summary
    st.markdown('<h2 class="tab-header">Project Summary & Insights</h2>', unsafe_allow_html=True)

    st.subheader("🎯 Key Findings")
    insights = [
        "🌡️ **Temperature Patterns**: Global average temperature is 22.8°C, with highest in Saudi Arabia (45°C). Seasonal peaks in July-August.",
        "💧 **Humidity Trends**: Negatively correlated with temperature (-0.35), highest in humid regions.",
        "🌧️ **Precipitation**: Highly skewed distribution, extreme events (>=0.8mm) occur in 4,905 records.",
        "💨 **Wind & Pressure**: Wind speeds show extreme outliers, pressure varies by region.",
        "🌫️ **Air Quality**: PM2.5 averages 45.2 μg/m³ globally, with significant regional variations.",
        "📊 **Correlations**: Strong relationships between temperature and UV index (0.48), humidity and UV (-0.57).",
        "⚠️ **Extreme Events**: 4,907 extreme heat events, concentrated in hot climates.",
        "📈 **Trends**: Sample countries show varying monthly temperature changes, from -0.45°C to +1.06°C/month."
    ]
    for insight in insights:
        st.markdown(f"• {insight}")

    st.subheader("🛠️ Methodology")
    st.write("""
    - **Data Source**: Global Weather Repository (Kaggle) - 97,824 records across 41 columns.
    - **Analysis**: Statistical summaries, distributions, correlations, seasonal patterns, trends, extreme event detection, and air quality analysis.
    - **Visualization**: Interactive choropleth maps, time series, scatter plots, heatmaps, pie charts, wind rose diagrams, and bar charts using Plotly.
    - **Tools**: Python (pandas, numpy), Streamlit for dashboard, Plotly for charts.
    """)

    st.subheader("📋 Data Sample")
    st.dataframe(df.head(10).style.format("{:.2f}", subset=key_vars))

# Footer
st.markdown("---")
st.markdown("**🌍 ClimateScope Dashboard** - Interactive Global Weather Analysis | *Data: Kaggle Global Weather Repository* | *Built with Streamlit & Plotly*")
st.markdown("*© 2024 ClimateScope Project*")
