import streamlit as st

st.set_page_config(page_title="Help & User Guide", page_icon="❓", layout="wide")

st.title("❓ Help & User Guide")
st.markdown("### ClimateScope Analysis Platform Documentation")

st.markdown("---")

st.header("📖 Overview")
st.markdown("""
**ClimateScope** is a comprehensive climate data analysis platform designed for deep insight into global climate patterns.
The application provides professional-grade analytical tools for exploring temperature, humidity, wind speed, and precipitation data
across 211 countries.
""")

st.markdown("---")

st.header("🗺️ Navigation Structure")

st.subheader("Two-Level Navigation System")

st.markdown("""
The application uses a **two-level navigation system**:

1. **Sidebar Navigation (Primary Level)**
   - Navigate between main pages using the sidebar menu
   - Each page focuses on a specific analytical perspective
   
2. **Tab Navigation (Secondary Level)**
   - Within certain pages (Climate Trends, Statistical Analysis), tabs organize related visualizations
   - Tabs share common controls for streamlined analysis
""")

st.markdown("---")

st.header("📄 Page Descriptions")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Executive Dashboard")
    st.markdown("""
    **Purpose:** High-level overview and data quality indicators
    
    **Features:**
    - **KPIs:** Total records, unique countries, average temperature, data coverage
    - **Interactive Map:** Global visualization with dynamic projection switching
    - **Projections:** Natural Earth, Orthographic (3D Globe), Mercator
    """)
    
    st.subheader("📊 Statistical Analysis")
    st.markdown("""
    **Purpose:** Quantitative relationship analysis
    
    **Features:**
    - **Two-Metric Comparison:** Scatter plots showing correlation
    - **Comparative Bar Charts:** Side-by-side metric comparison by country
    - **Statistics Tables:** Detailed descriptive statistics by region
    """)

with col2:
    st.subheader("📈 Climate Trends")
    st.markdown("""
    **Purpose:** Temporal pattern analysis
    
    **Features (6 visualization types):**
    - **Trend Line:** Daily average trends over time
    - **Scatter Plot:** Primary vs secondary metric analysis
    - **Violin Plot:** Probability density distribution by month
    - **Heatmap:** Seasonal intensity patterns
    - **Box Plot:** Statistical distribution with outliers
    - **Radar Chart:** Multi-metric climate profile
    """)
    
    st.subheader("⚠️ Extreme Events")
    st.markdown("""
    **Purpose:** Climate extremes and frequency analysis
    
    **Features:**
    - **Extreme Records:** Global Top 5 vs Regional Top 5 comparison
    - **Custom Threshold Analysis:** User-defined extreme event tracking
    - **Frequency Charts:** Monthly distribution of hazardous conditions
    """)

st.markdown("---")

st.header("🎛️ Sidebar Filters")

st.markdown("""
The **sidebar filters** are global controls that affect all pages:

1. **Date Range Filter**
   - Select start and end dates to focus your analysis
   - Default: Full year (2023)
   - Affects all visualizations and statistics

2. **Country Selection**
   - Multi-select dropdown for choosing specific countries
   - Default: First 10 countries alphabetically
   - Leave unselected to include all countries
   
3. **Real-time Indicators**
   - **Records:** Shows number of data points in filtered dataset
   - **Countries:** Shows number of selected countries
""")

st.markdown("---")

st.header("🖱️ Chart Interactivity")

st.markdown("""
All visualizations support interactive controls:

- **🔍 Zoom:** Click and drag to zoom into specific areas
- **↔️ Pan:** Hold shift and drag to pan across the chart
- **📷 Download:** Use the camera icon to save charts as PNG
- **🔄 Reset:** Double-click to reset zoom and pan
- **👆 Hover:** Hover over data points for detailed information
- **🎨 Legend:** Click legend items to show/hide data series
""")

st.markdown("---")

st.header("📊 Data Source & Scope")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Dataset Characteristics:**
    - **Total Countries:** 211
    - **Regions:** 8 major geographical regions
    - **Temporal Coverage:** Full year 2023 (365 days)
    - **Frequency:** Daily observations
    """)

with col2:
    st.markdown("""
    **Climate Metrics:**
    - **Temperature:** Measured in degrees Celsius (°C)
    - **Humidity:** Measured as percentage (%)
    - **Wind Speed:** Measured in meters per second (m/s)
    - **Precipitation:** Measured in millimeters (mm)
    """)

st.markdown("---")

st.header("💡 Tips for Effective Analysis")

st.markdown("""
1. **Start with the Executive Dashboard** to understand the overall data scope and quality
2. **Use filters strategically** to focus on specific regions or time periods
3. **Compare Global vs Regional** extreme events to identify outliers
4. **Leverage the Radar Chart** for quick multi-metric country comparisons
5. **Use the Heatmap** to identify seasonal patterns at a glance
6. **Experiment with projections** on the map to better visualize polar and equatorial regions
7. **Set custom thresholds** in Extreme Events to track specific climate hazards
""")

st.markdown("---")

st.header("🚀 Getting Started")

st.markdown("""
1. Visit the **Executive Dashboard** (home page) to load data and see the overview
2. Adjust **sidebar filters** to focus your analysis
3. Navigate to specific pages based on your analytical goals:
   - For correlation analysis → **Statistical Analysis**
   - For time series patterns → **Climate Trends**
   - For extreme weather events → **Extreme Events**
4. Within each page, explore different tabs and visualizations
5. Use interactive controls to drill down into specific data points
""")

st.markdown("---")

st.success("**Need More Help?** Contact the ClimateScope development team at Infosys Internship 2025.")
