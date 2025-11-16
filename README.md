# Infosys_Internship_2025_ClimateScope


# ** Final Dashboard Structure:ClimateScope Analysis **
    This platform represents the full completion of the core visualization phase of the ClimateScope project. It's a stable, professional, and feature-rich analytical system designed for deep insight into global climate patterns. The entire application is organized around five main pages accessible via the sidebar, with specialized analytical modules housed within internal tabs.
## 1. 🏠 Executive Dashboard : Global Overview
    Purpose:
     To provide immediate confidence in data quality, present high-level Key Performance Indicators (KPIs), and establish the dynamic geographical context.
       Key Performance Indicators (KPIs): 
         This section is critical, displaying the absolute health and scope of the analytical dataset. We showcase Total Records processed, the 211 Unique Countries represented, the overall Average Temperature, and the Data Coverage Duration across the selected date range.
       Geographical Context:
         The page features a robust map visualization used to plot the mean value of the chosen climate metric. To ensure compatibility and visual flexibility, I implemented a dynamic Projection Control.
         User Control: 
            Users can instantly switch the map view via a dropdown between a data-friendly Natural Earth projection, an engaging Orthographic (3D Globe) view, and a standard Mercator projection. This enhances the geographical appreciation of the data points.
2. ## 📊 Statistical Analysis: Correlation and Comparison
    Purpose: 
     This module is dedicated to quantitative verification, allowing users to analyze specific statistical relationships between any two metrics.
       Two-Metric Comparison: 
         This is the heart of the statistical inquiry. It features independent dropdowns allowing the user to select Metric A (X-Axis) and Metric B (Y-Axis).Scatter Plot: This chart visualizes the instantaneous relationship and covariance between Metric A and Metric B across the entire dataset for the selected countries, ideal for confirming correlation strength.
       Comparative Bar Chart:
         Provides a simplified, powerful summary by displaying the average value of both Metric A and Metric B for each individual selected country.Detailed Statistics Table: This serves as the definitive data validation source. It displays core descriptive statistics—Mean, Median, Min, Max, and Count—for all four core climate parameters, segmented by region.
## 3. 📈 Climate Trends: Temporal Analysis
   Purpose:
     The central analytical hub, which utilizes six distinct visualization types, all controlled by the single Primary Metric Selector above the content tabs.
      Trend Line:
        A clear Line Chart that tracks the daily average trend of the Primary Metric over the full date range, essential for identifying macro-level seasonal and long-term changes.
      Scatter Plot: 
        This plot has been fixed to ensure the Primary Metric is the static Y-Axis, while the user selects a Secondary Metric for the X-Axis, enabling focused analysis on how the main trend is influenced by another factor (e.g., Temperature vs. Wind)
      Violin Plot:
        A powerful distribution analysis tool that visualizes the probability density and full data shape of the Primary Metric, segmented by Month. This is superior to a Box Plot as it reveals underlying distribution anomalies.
      Heatmap:
        Tracks the seasonal intensity (daily average) of the Primary Metric across the months, allowing for easy identification of consistent annual patterns.
      Box Plot:
        Provides the traditional statistical summary, displaying the median, interquartile range (IQR), and outliers of the Primary Metric distribution by month.
      Radar Chart:
      The ultimate multi-metric comparison. It scales all four core metrics and plots them simultaneously to create an instant visual profile of each country's unique climate characteristics.
## 4. ⚠️ Extreme Events: Analysis
Purpose:
 This specialized module enables forensic analysis of climate extremes and their frequency.Extreme Records Tables:
  Provides definitive historical context by comparing the absolute Global Top 5 records against the Regional (Selected) Top 5 for metrics like Hottest, Coldest, and Windiest events.
 Extreme Frequency Analysis:
  A custom analytical tool where the user defines both the Metric and a Threshold (e.g., Precipitation $\ge 10 \text{mm}$). The resulting Bar Chart plots the number of days per month that the hazardous condition occurred, allowing for tracking of event vulnerability over time.
   ##  5. ❓ Help & User Guide
   Purpose:
    Serves as the comprehensive documentation, ensuring user understanding and project transparency.Content: Details the structure of the two-level navigation system, explains the function of the sidebar filters, outlines all Chart Interactivity controls (Zoom, Pan, Download), and provides full transparency regarding the Data Source and Scope (date range, geographical reach, and hourly frequency).                          
  ##  6. To Run the App
   To Run the dasbard use the command- >streamlit run app.py
   
    
    
