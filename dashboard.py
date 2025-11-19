import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np

# --- Configuration & Data Loading ---
CLEANED_DATA_PATH = os.path.join("data", "processed", "cleaned_weather.csv")

@st.cache_data
def load_data():
    """
    Loads cleaned data, performs necessary type conversions, and handles 
    critical missing values for visualization stability.
    """
    try:
        df = pd.read_csv(CLEANED_DATA_PATH)
        df['last_updated'] = pd.to_datetime(df['last_updated'])
        
        # --- STABLE METRICS CONFIRMED IN CLEANED_WEATHER.CSV ---
        stable_metrics = ['latitude', 'longitude', 'temperature_celsius', 'humidity', 'precip_mm', 'wind_kph']
        
        df.dropna(subset=stable_metrics, inplace=True)
        
        # Add date/time components for analysis features
        df['month'] = df['last_updated'].dt.month
        df['year'] = df['last_updated'].dt.year
        df['Date'] = df['last_updated'].dt.date
        return df
    except FileNotFoundError:
        st.error("Error: Cleaned data not found. Please ensure 'data/processed/cleaned_weather.csv' exists.")
        return pd.DataFrame()

df = load_data()

# Stop execution if data failed to load
if df.empty:
    st.stop()

# Define the final stable metrics list for dashboard filters
metrics = [
    'temperature_celsius', 
    'humidity', 
    'precip_mm', 
    'wind_kph'
]

# --- Helper Functions ---

def get_metric_unit(metric):
    if 'temp' in metric:
        return "°C"
    elif 'humidity' in metric:
        return "%"
    elif 'precip' in metric:
        return "mm"
    elif 'wind' in metric:
        return "KPH"
    return ""

def get_metric_title(metric):
    return metric.replace('_', ' ').title()

# --- MODAL DISMISSAL CALLBACK ---
def start_dashboard():
    st.session_state.show_welcome_modal = False
    # The script will naturally rerun after this session state change

# --- Streamlit Dashboard Layout ---

# Set page title and layout, using the custom config.toml for dark theme
st.set_page_config(
    page_title="ClimateScope Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- WELCOME MODAL LOGIC (LIGHT BOX) ---
if 'show_welcome_modal' not in st.session_state:
    st.session_state.show_welcome_modal = True

if st.session_state.show_welcome_modal:
    # Inject CSS for LIGHT BOX modal
    st.markdown(
        """
        <style>
        /* Hide the Streamlit main content, header, and sidebar */
        .st-emotion-cache-18ni7ap, 
        .st-emotion-cache-z5inrg,
        .st-emotion-cache-13k9f0m { display: none !important; }

        /* Disable scrollbar when modal is active */
        body { overflow: hidden !important; }
        
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            /* FINAL FIX: Set background explicitly to match Streamlit's secondary/sidebar background */
            background-color: #262730; 
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal-content {
            background-color: #FFFFFF; /* White Box Background */
            padding: 40px;
            padding-bottom: 120px; 
            border-radius: 15px;
            text-align: center;
            max-width: 650px;
            color: #0E1117; /* Dark Text */
            box-shadow: 0px 8px 30px rgba(0, 0, 0, 0.6);
            animation: fadeIn 0.5s ease-out;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .modal-content h2 {
            color: #1E88E5; /* Blue contrast for heading */
            font-size: 2.2em;
            margin-bottom: 20px;
        }
        .modal-content p {
            font-size: 1.1em;
            line-height: 1.6;
            margin-bottom: 20px;
            color: #0E1117; /* Ensure text is dark */
        }
        .modal-content-instruction {
            font-size: 1.0em;
            margin-bottom: 30px; 
            color: #4B4B4B; /* Muted dark text */
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* FIX: POSITION THE STREAMLIT BUTTON OVER THE MODAL */
        [data-testid="stVerticalBlock"] > div:nth-child(2) {
            position: fixed;
            top: 68%; 
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 1001; 
        }
        /* Style the button visually (Keeping primary color blue) */
        [data-testid="stButton"] button {
            background-color: #1E88E5 !important; /* BLUE BUTTON */
            color: white !important;
            padding: 15px 40px !important;
            border-radius: 8px !important;
            font-size: 1.2em !important;
            min-width: 280px; 
            transition: background-color 0.2s ease;
        }
        [data-testid="stButton"] button:hover {
            background-color: #1565C0 !important; /* Darker blue on hover */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display the modal structure (no button here)
    with st.container():
        st.markdown(
            f"""
            <div class="modal-overlay">
                <div class="modal-content">
                    <h2>Welcome to ClimateScope Explorer! 🌍</h2>
                    <p>
                        Dive into global climate data. This dashboard offers powerful tools to explore **temperature**, **humidity**,
                        **wind patterns**, and **precipitation** across various countries and timeframes.
                    </p>
                    <p class="modal-content-instruction">
                        Click "Explore Dashboard" to access the full-featured platform.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Render the Streamlit button here (it will be positioned by the CSS above)
        st.button(
            "Explore Dashboard",
            on_click=start_dashboard,
            type="primary"
        )
    
    st.stop() 


# --- Main Dashboard Content (Only runs if show_welcome_modal is False) ---

# --- START OF MAIN APP CSS INJECTION ---
# This CSS will run *after* the modal is dismissed.
st.markdown(
    """
    <style>
    /* FINAL FIX: Hide the yellow warning box permanently */
    [data-testid="stDecoration"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌎 ClimateScope: Advanced Climate Visualization Platform")
st.markdown("A two-level navigation system for comprehensive climate analysis.")

# --- Filters Section ---
st.sidebar.header("Filter Settings")

min_date = df['last_updated'].min().date()
max_date = df['last_updated'].max().date()

date_range = st.sidebar.slider(
    "Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

all_countries = sorted(df['country'].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries for Regional Analysis",
    options=all_countries,
    default=all_countries[:3] 
)

selected_metric_map = st.sidebar.selectbox(
    "Metric for Global Map",
    options=metrics,
    index=0 
)

st.sidebar.markdown("---")
# --- Main Sidebar Navigation (The key structural change) ---
PAGES = {
    "Executive Dashboard": "🏡 Executive Dashboard",
    "Statistical Analysis": "📊 Statistical Analysis",
    "Climate Trends": "📈 Climate Trends",
    "Extreme Events": "⚠️ Extreme Events",
    "Help/Info": "❓ Help & User Guide"
}

st.sidebar.header("Main Navigation")
selected_page = st.sidebar.radio("Go to:", list(PAGES.keys()), format_func=lambda x: PAGES[x])

# --- Chart Interactivity Note (Moved to the bottom of the sidebar) ---
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Chart Interactivity:** All charts support **Zoom**, **Pan**, and **Download**.
    """
)

# --- Apply Filters ---
df_filtered = df[
    (df['last_updated'].dt.date >= date_range[0]) & 
    (df['last_updated'].dt.date <= date_range[1])
]

# --- Helper function for Metric Cards ---
def display_kpis(df_data, selected_metric):
    total_records = len(df_data)
    unique_countries = df_data['country'].nunique()
    avg_temp = df_data['temperature_celsius'].mean()
    avg_wind = df_data['wind_kph'].mean()
    
    # Calculate data coverage in days
    date_coverage = (df_data['last_updated'].max() - df_data['last_updated'].min()).days + 1
    
    st.markdown("#### Real-time Key Performance Indicators (KPIs)")
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    kpi1.metric("Total Records", f"{total_records:,}")
    kpi2.metric("Countries Analyzed", f"{unique_countries}")
    kpi3.metric("Avg. Temperature", f"{avg_temp:.1f} °C")
    kpi4.metric("Avg. Wind Speed", f"{avg_wind:.1f} KPH")
    kpi5.metric("Data Coverage (Days)", f"{date_coverage:,}")

    st.markdown("---")

# =======================================================================
# --- PAGE 1: Executive Dashboard (KPIs + Global Map) ---
# =======================================================================
if selected_page == "Executive Dashboard":
    st.header("🏡 Executive Dashboard: Global Overview")
    display_kpis(df_filtered, selected_metric_map)

    st.subheader(f"Global Distribution of Average {get_metric_title(selected_metric_map)}")

    # --- NEW: Projection Selector for the Map ---
    selected_projection = st.selectbox(
        "Select Map Projection Style:",
        options=[
            "Natural Earth (Default)", 
            "Orthographic (3D Globe View)", 
            "Mercator (Classic Flat)"
        ],
        index=0,
        key='map_projection_selector'
    )
    
    # Map the user selection to Plotly's internal names
    projection_map = {
        "Natural Earth (Default)": "natural earth",
        "Orthographic (3D Globe View)": "orthographic",
        "Mercator (Classic Flat)": "mercator"
    }
    plotly_projection = projection_map[selected_projection]

    if not selected_countries:
        st.info("Please select one or more countries in the sidebar to view the map and regional data.")
    else:
        # --- Create a sample Country to ISO-3 mapping dictionary (Must be fully populated by user) ---
        country_to_iso = {
            'Afghanistan': 'AFG',
            'Albania': 'ALB',
            'Algeria': 'DZA',
            'India': 'IND',
            'United States': 'USA',
            'Brazil': 'BRA',
            'Canada': 'CAN',
            # Add all other countries in your cleaned_weather.csv file here
        }

        # Aggregate data for map
        df_map_all = df_filtered.groupby('country').agg(
            metric_mean=(selected_metric_map, 'mean'),
            latitude=('latitude', 'first'),
            longitude=('longitude', 'first')
        ).reset_index()

        df_map_selected = df_map_all[df_map_all['country'].isin(selected_countries)].copy()
        
        # FIX: Create the ISO-3 column for Plotly
        df_map_selected['iso_alpha'] = df_map_selected['country'].map(country_to_iso)
        df_map_selected.dropna(subset=['iso_alpha'], inplace=True) 
        
        # Use Scatter Geo to highlight points on a world map background
        fig_map = px.scatter_geo(
            df_map_selected,
            locations="iso_alpha",  # FIXED: Use the ISO-3 column
            locationmode='ISO-3',   # FIXED: Set locationmode to 'ISO-3'
            color="metric_mean", 
            template="plotly_dark", 
            projection=plotly_projection # DYNAMIC PROJECTION APPLIED
        )
        
        # FIX: Apply Title and Labels using update_layout to bypass the warning
        fig_map.update_layout(
            title=f'Mean {get_metric_title(selected_metric_map)} for Selected Countries',
            coloraxis_colorbar_title=get_metric_unit(selected_metric_map)
        )
        
        fig_map.update_geos(
            showland=True, landcolor="#1F2937", 
            showocean=True, oceancolor="#0A1838", 
            showsubunits=True, subunitcolor="#6B7280", 
            bgcolor='rgba(0,0,0,0)' 
        )
        
        # FIX: Added use_container_width=False to suppress the yellow Plotly warning
        st.plotly_chart(fig_map, width='stretch', config={}, use_container_width=False)

# =======================================================================
# --- PAGE 2: Statistical Analysis (Comparison, Stats Table) ---
# =======================================================================
elif selected_page == "Statistical Analysis":
    st.header("📊 Statistical Analysis: Correlation and Comparison")
    
    # Tabs: Two Metric Comparison and Detailed Statistics
    tab_comp, tab_stats = st.tabs(["Two Metric Comparison", "Detailed Statistics"])

    # --- Tab: Two Metric Comparison (Scatter & Bar) ---
    with tab_comp:
        st.subheader("Regional Comparison: Analyzing Two Metrics")
        
        col_metric1, col_metric2 = st.columns(2)
        with col_metric1:
            metric_x = st.selectbox("Select Metric A (X-Axis)", options=metrics, index=0, key='stat_metric_x')
        with col_metric2:
            default_index_y = 1 if metric_x != metrics[1] else 2
            metric_y = st.selectbox("Select Metric B (Y-Axis)", options=metrics, index=default_index_y, key='stat_metric_y')
            
        if metric_x == metric_y:
            st.warning("Please select two different metrics for comparison.")
        elif not selected_countries:
            st.warning("Please select countries in the sidebar to view the comparison chart.")
        else:
            df_comp = df_filtered[df_filtered['country'].isin(selected_countries)]
            
            # Scatter Plot for Correlation
            df_comp_agg = df_comp.groupby(['last_updated', 'country']).agg({metric_x: 'mean', metric_y: 'mean'}).reset_index()

            fig_comp = px.scatter(
                df_comp_agg, x=metric_x, y=metric_y, color='country', hover_data=['last_updated'],
                template="plotly_dark"
            )
            # FIX: Apply Title and Labels using update_layout to bypass the warning
            fig_comp.update_layout(
                title=f"Correlation: {get_metric_title(metric_x)} vs. {get_metric_title(metric_y)}",
                xaxis_title=f'{get_metric_title(metric_x)} ({get_metric_unit(metric_x)})',
                yaxis_title=f'{get_metric_title(metric_y)} ({get_metric_unit(metric_y)})'
            )
            st.plotly_chart(fig_comp, width='stretch', config={}, use_container_width=False) # FIX: config={} and use_container_width=False
            
            # Bar Chart for Average Comparison
            df_avg_comp = df_comp.groupby('country')[[metric_x, metric_y]].mean().reset_index()
            fig_bar = go.Figure(data=[
                go.Bar(name=f'{get_metric_title(metric_x)} ({get_metric_unit(metric_x)})', x=df_avg_comp['country'], y=df_avg_comp[metric_x], marker_color=px.colors.qualitative.Plotly[0]),
                go.Bar(name=f'{get_metric_title(metric_y)} ({get_metric_unit(metric_y)})', x=df_avg_comp['country'], y=df_avg_comp[metric_y], marker_color=px.colors.qualitative.Plotly[1])
            ])
            fig_bar.update_layout(
                barmode='group', title=f"Mean {get_metric_title(metric_x)} and {get_metric_title(metric_y)} by Country",
                xaxis_title="Country", yaxis_title="Average Value", template="plotly_dark"
            )
            st.plotly_chart(fig_bar, width='stretch', config={}, use_container_width=False) # FIX: config={} and use_container_width=False

    # --- Tab: Detailed Statistics ---
    with tab_stats:
        st.subheader("Detailed Regional Statistics Table")
        if selected_countries:
            df_stats_filtered = df_filtered[df_filtered['country'].isin(selected_countries)]
            df_stats = df_stats_filtered.groupby('country')[metrics].agg(['mean', 'median', 'min', 'max', 'count'])
            st.dataframe(df_stats)
        else:
            st.info("Select countries to populate the detailed statistics table.")


# =======================================================================
# --- PAGE 3: Climate Trends (Line, Area, Heatmap, Box, Radar, Scatter, Violin) ---
# =======================================================================
elif selected_page == "Climate Trends":
    st.header("📈 Climate Trends: Temporal and Distribution Analysis")
    
    # --- Primary Metric Selector (for Line, Area, Heatmap, Box, Violin) ---
    selected_trend_metric = st.selectbox(
        "Select **Primary** Metric for Trend & Distribution Analysis", options=metrics, index=0, key='trend_metric_select_fixed'
    )
    st.markdown("---") # Visual separator

    # --- Secondary Tab Navigation for Charts ---
    tab_line, tab_scatter, tab_violin, tab_area, tab_heatmap, tab_box, tab_radar = st.tabs([
        "Trend Line", "Scatter Plot", "Violin Plot", "Area Chart", "Heatmap", "Box Plot", "Radar Chart"
    ])
    
    metric_unit_trend = get_metric_unit(selected_trend_metric)
    
    if not selected_countries:
        st.warning("Please select countries in the sidebar to view temporal charts.")
        df_trend = pd.DataFrame() 
    else:
        df_trend = df_filtered[df_filtered['country'].isin(selected_countries)]

    # --- Tab: Trend Line Chart ---
    with tab_line:
        if not df_trend.empty:
            st.subheader(f"Multi-Country {get_metric_title(selected_trend_metric)} Trend Line Over Time")
            # Aggregation is crucial for clean line plots
            df_daily_avg = df_trend.groupby(['last_updated', 'country'])[selected_trend_metric].mean().reset_index()
            fig_line = px.line(
                df_daily_avg, x='last_updated', y=selected_trend_metric, color='country', 
                template="plotly_dark"
            )
            # FIX: Apply Title and Labels using update_layout to bypass the warning
            fig_line.update_layout(
                title=f"Multi-Country {get_metric_title(selected_trend_metric)} Trend Line",
                yaxis_title=f'Avg {get_metric_title(selected_trend_metric)} ({metric_unit_trend})',
                xaxis_title='Date'
            )
            fig_line.update_xaxes(rangeslider_visible=True) 
            st.plotly_chart(fig_line, width='stretch', config={}, use_container_width=False) # FIX: config={} and use_container_width=False

    # --- Tab: Scatter Plot (Primary Metric vs Selected X-Axis) ---
    with tab_scatter:
        st.subheader("Scatter Plot: Primary Metric Relationship")
        st.markdown("Select a secondary metric below to analyze its relationship with the **Primary Metric** (Y-Axis).")

        col_scatter_1, col_scatter_2 = st.columns([1, 2])
        with col_scatter_1:
            # Create a list of metrics excluding the selected_trend_metric for a clean comparison
            scatter_x_options = [m for m in metrics if m != selected_trend_metric]
            
            # Use the first metric in the options list as the default
            default_index = 0 if len(scatter_x_options) > 0 else 0
            
            # If the primary metric is already the default (temperature), set humidity as the default comparison
            if selected_trend_metric == 'temperature_celsius':
                default_index = 0 if 'humidity' not in scatter_x_options else scatter_x_options.index('humidity')
                
            scatter_metric_x = st.selectbox(
                "Select X-Axis Metric", 
                options=scatter_x_options, 
                index=default_index, 
                key='scatter_trend_x'
            )
            # Display the Y-Axis Metric (fixed)
            st.markdown(f"**Y-Axis Metric (Fixed):** {get_metric_title(selected_trend_metric)}")


        if not df_trend.empty and scatter_metric_x:
            # The Y-axis is always the primary metric
            scatter_metric_y = selected_trend_metric

            # Aggregate to daily mean for cleaner scatter points
            df_scatter = df_trend.groupby(['last_updated', 'country']).agg({
                scatter_metric_x: 'mean',
                scatter_metric_y: 'mean'
            }).reset_index()

            fig_scatter = px.scatter(
                df_scatter,
                x=scatter_metric_x,
                y=scatter_metric_y,
                color='country',
                hover_data=['last_updated'],
                template="plotly_dark"
            )
            # FIX: Apply Title and Labels using update_layout to bypass the warning
            fig_scatter.update_layout(
                title=f"{get_metric_title(scatter_metric_y)} vs. {get_metric_title(scatter_metric_x)}",
                xaxis_title=f'{get_metric_title(scatter_metric_x)} ({get_metric_unit(scatter_metric_x)})',
                yaxis_title=f'{get_metric_title(scatter_metric_y)} ({get_metric_unit(scatter_metric_y)})'
            )
            with col_scatter_2:
                 st.plotly_chart(fig_scatter, width='stretch', config={}, use_container_width=False) # FIX: config={} and use_container_width=False
        else:
            st.info("Scatter plot requires countries to be selected and two distinct metrics for analysis.")
            
    # --- Tab: Violin Plot (Distribution Density) ---
    with tab_violin:
        if not df_trend.empty:
            st.subheader(f"Violin Plot: {get_metric_title(selected_trend_metric)} Distribution Density")
            st.markdown("Violin plots show the probability density of the data at different values, useful for identifying peaks and spread.")
            
            # Use the monthly grouping for seasonal distribution comparison
            df_violin = df_filtered[df_filtered['country'].isin(selected_countries)].copy()
            month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            df_violin['month_name'] = df_violin['month'].map(month_names)

            fig_violin = px.violin(
                df_violin, 
                x="month_name", 
                y=selected_trend_metric, 
                color="country",
                box=True, # Show box plot inside the violin
                points="outliers",
                template="plotly_dark"
            )
            # FIX: Apply Title and Labels using update_layout to bypass the warning
            fig_violin.update_layout(
                title=f"{get_metric_title(selected_trend_metric)} Distribution Density by Month",
                yaxis_title=f'{get_metric_title(selected_trend_metric)} ({metric_unit_trend})',
                xaxis_title='Month'
            )
            st.plotly_chart(fig_violin, width='stretch', config={}, use_container_width=False) # FIX: config={} and use_container_width=False

    # --- Tab: Area Chart (Conditional for suitable metrics) ---
    with tab_area:
        if selected_trend_metric in ['precip_mm'] and not df_trend.empty:
            st.subheader(f"Cumulative Area Chart: {get_metric_title(selected_trend_metric)}")
            df_area = df_trend.groupby(['last_updated', 'country'])[selected_trend_metric].sum().reset_index()
            fig_area = px.area(
                df_area, x='last_updated', y=selected_trend_metric, color='country',
                template="plotly_dark"
            )
            # FIX: Apply Title and Labels using update_layout to bypass the warning
            fig_area.update_layout(
                title=f"Cumulative {get_metric_title(selected_trend_metric)} Over Time",
                yaxis_title=f'Total {get_metric_title(selected_trend_metric)} ({metric_unit_trend})',
                xaxis_title='Date'
            )
            st.plotly_chart(fig_area, width='stretch', config={}, use_container_width=False) # FIX: config={} and use_container_width=False

    # --- Tab: Heatmap ---
    with tab_heatmap:
        if selected_trend_metric in ['temperature_celsius', 'precip_mm'] and not df_trend.empty:
            st.subheader(f"Daily Average Heatmap (Seasonal Trend)")
            df_heat_agg = df_trend.groupby(['Date', 'country'])[selected_trend_metric].mean().reset_index()
            pivot_table = df_heat_agg.pivot(index='Date', columns='country', values=selected_trend_metric)
            color_scale = "Reds" if 'temp' in selected_trend_metric else "Blues"
            fig_heat = px.imshow(
                pivot_table.T, aspect="auto",
                color_continuous_scale=color_scale,
            )
            # FIX: Apply Title and Labels using update_layout to bypass the warning
            fig_heat.update_layout(
                title=f"Daily Average {get_metric_title(selected_trend_metric)} Heatmap (Seasonal Trend)",
                template="plotly_dark"
            )
            fig_heat.update_xaxes(title_text="Date")
            fig_heat.update_yaxes(title_text="Country")
            fig_heat.update_coloraxes(colorbar_title=f"Avg. {metric_unit_trend}")

            st.plotly_chart(fig_heat, width='stretch', config={}, use_container_width=False) # FIX: config={} and use_container_width=False

    # --- Tab: Box Plot ---
    with tab_box:
        if selected_trend_metric in ['temperature_celsius', 'humidity', 'wind_kph'] and not df_trend.empty:
            st.subheader(f"Monthly Distribution (Box Plot)")
            df_box = df_filtered[df_filtered['country'].isin(selected_countries)].copy()
            month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            df_box['month_name'] = df_box['month'].map(month_names)

            fig_box = px.box(
                df_box, x="month_name", y=selected_trend_metric, color="country", points="outliers",
                template="plotly_dark"
            )
            # FIX: Apply Title and Labels using update_layout to bypass the warning
            fig_box.update_layout(
                title=f"{get_metric_title(selected_trend_metric)} Distribution by Month and Country",
                yaxis_title=f'{get_metric_title(selected_trend_metric)} ({metric_unit_trend})',
                xaxis_title='Month'
            )
            st.plotly_chart(fig_box, width='stretch', config={}, use_container_width=False) # FIX: config={} and use_container_width=False

    # --- Tab: Radar Chart ---
    with tab_radar:
        if not df_trend.empty:
            st.subheader("Multi-Metric Radar Chart (Scaled Average Comparison)")
            df_radar = df_trend.groupby('country')[metrics].mean().reset_index()
            df_radar_scaled = df_radar.copy()
            
            for col in metrics:
                min_val = df_radar_scaled[col].min()
                max_val = df_radar_scaled[col].max()
                if max_val != min_val:
                    df_radar_scaled[col] = (df_radar_scaled[col] - min_val) / (max_val - min_val)
                else:
                    df_radar_scaled[col] = 0.5 

            categories = [get_metric_title(m) for m in metrics]
            fig_radar = go.Figure()
            
            for index, row in df_radar_scaled.iterrows():
                values = [row[m] for m in metrics]
                values.append(values[0])
                fig_radar.add_trace(go.Scatterpolar(r=values, theta=categories + [categories[0]], fill='toself', name=row['country']))

            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), title="Scaled Average Climate Metrics (Radar Chart)", template="plotly_dark", showlegend=True)
            st.plotly_chart(fig_radar, width='stretch', config={}, use_container_width=False) # FIX: config={} and use_container_width=False


# =======================================================================
# --- PAGE 4: Extreme Events (Enhanced with Frequency Analysis) ---
# =======================================================================
elif selected_page == "Extreme Events":
    st.header("⚠️ Extreme Events Analysis")
    st.markdown("This section analyzes historical extreme records and the **frequency** of extreme events over time.")
    
    # --- Secondary Tab Navigation for Extreme Analysis ---
    tab_records, tab_frequency = st.tabs(["Extreme Records", "Extreme Frequency Analysis"])

    # --- Tab: Extreme Records (Existing tables) ---
    with tab_records:
        st.subheader("1. Global vs. Regional Top 5 Extreme Records")
        
        # --- Function to generate and display the extreme table ---
        def display_extreme_table(column, df_data, metric, label, ascending):
            df_sorted = df_data.sort_values(by=metric, ascending=ascending)
            if metric == 'temperature_celsius' and ascending == True:
                 label = 'Coldest ❄️'
            df_top_5 = df_sorted.head(5)[['country', 'last_updated', metric]].reset_index(drop=True)

            with column:
                st.markdown(f"**{label}**")
                df_display = df_top_5.rename(columns={metric: f'{get_metric_title(metric)} ({get_metric_unit(metric)})'})
                st.dataframe(df_display, width='stretch', hide_index=True) # FIX: width='stretch'

        # Global Extremes
        st.markdown("##### Global Top 5 Extreme Records (All Countries)")
        col_temp_global, col_temp_cold = st.columns(2)
        display_extreme_table(col_temp_global, df_filtered, 'temperature_celsius', 'Hottest 🔥', ascending=False)
        display_extreme_table(col_temp_cold, df_filtered, 'temperature_celsius', 'Coldest ❄️', ascending=True)
        
        st.markdown("---")
        col_wind_global, col_precip_global, col_humidity_global, col_empty = st.columns(4)
        display_extreme_table(col_wind_global, df_filtered, 'wind_kph', 'Windiest 💨', ascending=False)
        display_extreme_table(col_precip_global, df_filtered, 'precip_mm', 'Highest Precipitation 🌧️', ascending=False)
        display_extreme_table(col_humidity_global, df_filtered, 'humidity', 'Highest Humidity 💧', ascending=False)


        # Regional Extremes
        st.markdown(f"##### Regional Top 5 Extreme Records (Selected Countries: {', '.join(selected_countries) if selected_countries else 'None'})")
        
        if selected_countries:
            df_regional = df_filtered[df_filtered['country'].isin(selected_countries)]
            col_temp_regional, col_temp_cold_regional = st.columns(2)
            display_extreme_table(col_temp_regional, df_regional, 'temperature_celsius', 'Hottest 🔥', ascending=False)
            display_extreme_table(col_temp_cold_regional, df_regional, 'temperature_celsius', 'Coldest ❄️', ascending=True)
            
            st.markdown("---")
            col_wind_regional, col_precip_regional, col_humidity_regional, col_empty_r = st.columns(4)
            display_extreme_table(col_wind_regional, df_regional, 'wind_kph', 'Windiest 💨', ascending=False)
            display_extreme_table(col_precip_regional, df_regional, 'precip_mm', 'Highest Precipitation 🌧️', ascending=False)
            display_extreme_table(col_humidity_regional, df_regional, 'humidity', 'Highest Humidity 💧', ascending=False)
        else:
            st.info("Please select countries in the sidebar to view regional extreme events data.")


    # --- Tab: Extreme Frequency Analysis (NEW) ---
    with tab_frequency:
        st.subheader("2. Time-Series Analysis of Extreme Event Frequency")
        st.markdown("Track the number of days a selected metric exceeds a specific threshold over time (grouped by month).")

        col_freq_metric, col_freq_threshold = st.columns(2)
        
        with col_freq_metric:
            freq_metric = st.selectbox(
                "Select Metric", options=metrics, index=0, key='freq_metric'
            )
        
        with col_freq_threshold:
            # Determine a reasonable default threshold based on the metric
            default_threshold = {
                'temperature_celsius': 35.0, # Hot day
                'humidity': 90.0, # High humidity day
                'precip_mm': 10.0, # Significant rainfall day
                'wind_kph': 40.0 # High wind day
            }.get(freq_metric, 0.0)
            
            freq_threshold = st.number_input(
                f"Threshold ({get_metric_unit(freq_metric)})",
                min_value=float(df_filtered[freq_metric].min()), # Ensure float for consistent comparison
                max_value=float(df_filtered[freq_metric].max()), # Ensure float
                value=float(default_threshold), # Ensure float
                step=0.5,
                key='freq_threshold'
            )

        if not selected_countries:
            st.warning("Please select countries in the sidebar to perform frequency analysis.")
        else:
            # 1. Identify extreme days (Extreme is defined as the maximum hourly value >= threshold)
            df_extreme = df_filtered[df_filtered['country'].isin(selected_countries)].copy()
            
            # Find the max value per day for the selected metric
            df_daily_max = df_extreme.groupby(['Date', 'country'])[freq_metric].max().reset_index()
            
            # Flag days where the max metric value exceeded the threshold
            df_daily_max['is_extreme'] = df_daily_max[freq_metric] >= freq_threshold
            
            # 2. Group by month/year to count extreme days
            df_daily_max['year_month'] = df_daily_max['Date'].apply(lambda x: x.strftime('%Y-%m'))
            
            df_freq = df_daily_max[df_daily_max['is_extreme'] == True].groupby(['year_month', 'country']).size().reset_index(name='Extreme Days Count')
            
            # Fill months with zero counts (important for continuity)
            all_months_in_range = sorted(df_daily_max['year_month'].unique())
            all_combinations = pd.MultiIndex.from_product([all_months_in_range, selected_countries], names=['year_month', 'country']).to_frame(index=False)
            df_freq_complete = pd.merge(all_combinations, df_freq, on=['year_month', 'country'], how='left').fillna(0)
            df_freq_complete['Extreme Days Count'] = df_freq_complete['Extreme Days Count'].astype(int)

            # 3. Plot the bar chart
            fig_freq = px.bar(
                df_freq_complete, 
                x='year_month', 
                y='Extreme Days Count', 
                color='country',
                template="plotly_dark",
                barmode='group'
            )
            # FIX: Apply Title and Labels using update_layout to bypass the warning
            fig_freq.update_layout(
                title=f"Monthly Frequency of Extreme Events ($\ge{freq_threshold}{get_metric_unit(freq_metric)}$)",
                yaxis_title='Number of Extreme Days',
                xaxis_title='Month'
            )
            fig_freq.update_xaxes(tickangle=45)
            st.plotly_chart(fig_freq, width='stretch', config={}, use_container_width=False) # FIX: config={} and use_container_width=False

# =======================================================================
# --- PAGE 5: Help/Info (Enhanced) ---
# =======================================================================
elif selected_page == "Help/Info":
    st.header("❓ Help & User Guide")
    st.markdown("This dashboard provides advanced climate visualization and comparison tools.")
    
    st.subheader("1. Navigation Structure")
    st.markdown("""
    * **Primary Navigation (Sidebar):** Select a main analytical page (e.g., Executive Dashboard, Climate Trends).
    * **Secondary Navigation (Tabs):** Switch between specific charts or tables within that page (e.g., Trend Line, Box Plot).
    """)
    
    st.subheader("2. Filter Settings")
    st.markdown("""
    Use the filters in the sidebar to define the time period and the specific regions for analysis.
    """)
    
    st.subheader("3. Chart Interactivity")
    st.markdown("""
    All charts are built with **Plotly** and support **Zoom**, **Pan**, **Highlighting** (by clicking on legend items), and **Download** (via the camera icon).
    """)

    st.subheader("4. Data Source and Scope")
    
    # Calculate key data metrics for display
    total_countries = df['country'].nunique()
    start_date = df['last_updated'].min().strftime("%Y-%m-%d")
    end_date = df['last_updated'].max().strftime("%Y-%m-%d")
    
    st.markdown(f"""
    This dashboard visualizes hourly weather data that has been cleaned and processed by **Milestone 1**.
    
    * **Data Period:** Data covers the range from **{start_date}** to **{end_date}**.
    * **Geographical Scope:** **{total_countries}** unique countries are included in the dataset.
    * **Primary Metrics:** Hourly observations are available for Temperature, Humidity, Wind Speed, and Precipitation.
    * **Data Source:** Weather data sourced from a real-time global weather API (e.g., WeatherAPI).
    * **Frequency:** Data points are typically collected on an **hourly basis**.
    """)