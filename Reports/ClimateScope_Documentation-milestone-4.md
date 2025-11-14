# ClimateScope Project --- Detailed Documentation 

## Project Overview

ClimateScope is a comprehensive data visualization project designed to
analyze and represent global weather trends, variations, and extreme
events through an interactive dashboard. The project leverages the
Global Weather Repository dataset to deliver real-time insights on
climate behavior, offering decision-making support and promoting global
climate awareness.

## Objectives

-   Analyze worldwide weather data to uncover patterns, anomalies, and
    seasonal variations.
-   Create an interactive visualization dashboard for exploratory data
    analysis.
-   Enable comparative climate studies across countries and regions.
-   Detect and visualize extreme weather events.
-   Provide predictive insights and trend forecasting.

## Dataset Details

The project uses the **Global Weather Repository Dataset** from Kaggle.
It contains worldwide daily weather observations, including metrics such
as temperature, humidity, precipitation, pressure, wind, and air
quality.

**Key Attributes:** - Temperature (°C, °F, Feels-like) - Humidity (%) -
Wind speed (kph, mph) - Precipitation (mm, in) - Air Quality indices
(PM2.5, PM10, NO₂, O₃, CO, etc.) - Pressure (mb, inHg) - Visibility (km,
miles) - Geographic coordinates (latitude, longitude) - Country and
location details - Date and last update timestamps

## Data Cleaning & Preprocessing (clean1.py)

The preprocessing pipeline implemented in `clean1.py` ensures data
quality and consistency before analysis. The cleaning steps include:

1.  **Handling Missing Values:** Missing numeric values were replaced
    with column medians, while categorical missing entries were replaced
    with mode values.

2.  **Unit Conversion:** Fahrenheit to Celsius and pressure from inches
    to millibars were standardized for consistency.

3.  **Normalization:** Using `MinMaxScaler`, numeric features were
    normalized to scale values between 0 and 1 for uniformity.

4.  **Date Parsing:** Derived a clean date column using timestamps from
    `last_updated`.

5.  **Aggregation:** Generated daily averaged datasets grouped by
    `country`, `location_name`, and `date`.

6.  **Export:** Saved processed data as
    `GlobalWeatherRepository_cleaned.csv` and daily averages as
    `GlobalWeatherRepository_daily.csv`.

## Architecture and Workflow

The ClimateScope architecture follows a modular structure aligned with
the Data Visualization milestones:

1.  **Data Acquisition:** Collected global weather data from Kaggle.

2.  **Preprocessing:** Cleaned and transformed raw CSV data using pandas
    and NumPy.

3.  **Backend Analysis:** Implemented core analytics in `Analyse.py` for
    trend detection, correlation, forecasting, and extreme event
    analysis.

4.  **Frontend Dashboard:** Designed the Streamlit interface
    (`Streamlit-app.py`) for user interaction and visualization.

5.  **Visualization Engine:** Plotly is used to create dynamic,
    interactive charts and maps.

6.  **Output Layer:** Insights are generated in the form of interactive
    dashboards with metrics, plots, and maps.

## Libraries and Tools Used

**Core Libraries:** - pandas --- Data manipulation and analysis. - numpy
--- Numerical computation. - sklearn --- StandardScaler, PCA, and
clustering algorithms. - plotly.express & plotly.graph_objects ---
Interactive visualizations. - seaborn & matplotlib --- Statistical
visualization. - streamlit --- Dashboard development. -
scipy.interpolate --- Grid data interpolation for 3D visualizations.

## Backend Module (Analyse.py)

`Analyse.py` forms the analytical core of ClimateScope, containing
reusable data analysis and visualization functions. Each function is
optimized for performance and modular integration.

**Key Functions:**

• `load_data(path)` --- Loads and preprocesses data, handling missing
values and timestamps.

• `descriptive_stats(df)` --- Computes descriptive statistics, skewness,
kurtosis, and missing value percentages.

• `country_aggregates(df)` --- Aggregates weather metrics by country
(mean, median, std, etc.).

• `correlation_matrix(df)` --- Generates a Pearson correlation heatmap
between all numeric variables.

• `monthly_trends(df)` --- Detects average monthly trends for
temperature and humidity using time-period grouping.

• `detect_extreme_events(df)` --- Identifies extreme weather conditions
like heatwaves, storms, floods, and droughts based on quantile
thresholds.

• `region_comparisons(df)` --- Compares metrics (like temperature)
across countries with top 20 rankings visualized in bar charts.

• `forecast_weather(df)` --- Uses polynomial trend fitting to predict
future temperature or humidity for 30 days.

• `forecast_multiple_metrics(df)` --- Extends forecasting for multiple
weather metrics simultaneously.

• `generate_heatmap(df)` --- Displays a geographic scatter map showing
metric intensity across lat-long coordinates.

• `generate_3d_chart(df)` --- Creates multiple 3D visualizations
(Scatter, Surface, Line, Mesh, Bubble) for multi-variable relationships.

• `perform_pca_analysis(df)` --- Reduces dimensionality using PCA to
reveal main influencing weather factors.

## Frontend Dashboard (Streamlit-app.py)

The Streamlit frontend script transforms the backend analytics into an
interactive, user-driven web dashboard. It provides multi-level data
filtering, metric selection, visualization modules, and dynamic
insights.

**Interface Design:** - Sidebar filters for country, date range, and
analysis category. - Metrics displayed using KPI cards (temperature,
humidity, wind, pressure, etc.). - Tabs for different analysis
sections: 1. Executive Summary 2. Temperature Analysis 3. Humidity &
Visibility 4. Wind Patterns 5. Precipitation & Pressure 6. Air Quality
7. Geographic Analysis 8. Extreme Events 9. Forecasting 10. Advanced
Analytics

**Key Streamlit Features:** - Dynamic interactivity using
`st.multiselect()`, `st.date_input()`, and `st.selectbox()`. -
Visualization rendering via `st.plotly_chart()`. - Cache optimization
through `@st.cache_data` for faster reloading. - Configurable Plotly
chart settings for zoom, pan, and reset controls. - Custom CSS styling
for modern UI experience.

## Dashboard Features and Insights

1. **Executive Summary:** Displays KPIs, temperature distribution, and
    3D weather visualization.

2. **Temperature Analysis:** Shows detailed statistical and comparative
    country-wise temperature behavior.

3. **Humidity & Visibility:** Analyzes atmospheric moisture, visibility
    trends, and correlation between them.

4. **Wind Patterns:** Compares average and gust speeds, distributions,
    and storm trends.

5. **Precipitation & Pressure:** Highlights rainfall patterns, pressure
    changes, and correlations.

6. **Air Quality:** Examines PM2.5, PM10, CO, and O₃ metrics and their
    correlations with temperature and humidity.

7. **Extreme Events:** Visualizes identified anomalies and weather
    extremes by region.

8. **Forecasting:** Predicts near-future climate behavior using
    regression-based models.

9. **Advanced Analytics:** Includes PCA, clustering, and anomaly
    detection for advanced pattern recognition.

## Results & Insights

-   Identified heatwave-prone and flood-vulnerable countries.
-   Revealed strong correlation between temperature and humidity in
    tropical regions.
-   Observed inverse relationship between visibility and humidity.
-   Demonstrated predictive temperature rise trends for several regions.
-   Detected multiple extreme weather patterns including drought zones
    and storms.

## Challenges & Solutions

-   **Challenge:** Handling massive dataset with missing and
    inconsistent values.\
    **Solution:** Applied automated median/mode imputation and
    normalization using sklearn.

-   **Challenge:** Maintaining visualization performance for large
    datasets.\
    **Solution:** Used Streamlit caching and optimized Plotly rendering.

-   **Challenge:** Interpreting extreme events objectively.\
    **Solution:** Quantile-based thresholds (95th percentile) used for
    robust classification.


## Conclusion

ClimateScope successfully combines data analytics, visualization, and
interactivity to create an all-in-one platform for understanding global
weather patterns. It bridges raw data with meaningful insights through
advanced analytics and intuitive design, supporting environmental
studies and climate impact analysis worldwide.
