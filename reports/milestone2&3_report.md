Milestone 2 & 3 – Core Analysis and Interactive Visualization Development


1. Objective

The goal of Milestones 2 and 3 was to analyze the Global Weather Repository dataset and develop an interactive dashboard to visualize global weather and air quality patterns.
The process included statistical analysis, trend identification, and the creation of an interactive Streamlit dashboard to communicate insights effectively.


2. Analytical Goals

- Explore temperature, humidity, wind, and air quality trends across different regions.
- Identify extreme weather and pollution events using percentile-based thresholds.
- Examine correlations among multiple environmental parameters.
- Analyze temporal and regional variations in climate indicators.
- Design an engaging, user-friendly dashboard to support interactive exploration.


3. Tools and Libraries

The analysis and dashboard were built using Python with the following core libraries:

- pandas – Data handling and preprocessing
- plotly.express – Interactive visualizations
- streamlit – Dashboard design and deployment
- numpy – Numerical operations


4. Data Analysis Summary

The analytical workflow in "finalised.py" consisted of the following stages:

- Computed descriptive statistics and analyzed data distributions.
- Identified seasonal and temporal patterns in temperature and humidity.
- Generated correlation heatmaps for numeric weather variables.
- Detected extreme weather and air quality events using dynamic thresholds.
- Visualized regional patterns using geospatial scatter maps.
- Compared multiple parameters interactively (temperature, humidity, pressure, air quality).


5. Dashboard Design and Development

All analyses were integrated into a single Streamlit dashboard with a clean, modern layout.

Key Features:

- 🔍 Dynamic Filters – Filter data by country, year, and temperature range.
- 🌡 Temperature & Trend Analysis – Interactive line, scatter, and bar charts.
- 💨 Air Quality Visualization – PM2.5, PM10, and gaseous pollutants tracking.
- 🌍 Geospatial Mapping – Global representation of temperature and humidity levels.
- 📊 Correlation Heatmap – Relationships among key weather indicators.
- ⚠ Extreme Events Detector – Identification of temperature or pollution anomalies.
- 🧭 Insight Summary – Consolidated findings displayed in the final dashboard tab.

Design Highlights:

- Dark theme for improved contrast and focus.
- Consistent color palette: Cyan (#00FFFF) and Orange (#FFA500).
- Responsive, tab-based structure for organized navigation.


6. Results and Insights

Aspect Key Findings
Temperature Trends: Daily and seasonal fluctuations were visible, with low humidity corresponding to temperature peaks.
Air Quality: PM2.5 and PM10 levels showed a strong correlation (>0.9). CO and NO₂ concentrations tended to rise when visibility decreased.
Geospatial Patterns: Coastal regions displayed stable temperatures and higher humidity, while inland areas experienced more extremes.
Correlation Analysis: Temperature and humidity were inversely correlated. Wind speed played a role in dispersing pollutants.
Extreme Events: Several temperature and pollution outliers were detected above the 95th percentile threshold.


7. Conclusion

Milestones 2 and 3 successfully transitioned from core data analysis to a comprehensive, interactive visualization platform.
The Streamlit dashboard integrates statistical insights, geospatial views, and dynamic interactivity — enabling users to explore global climate and air quality patterns intuitively and effectively.