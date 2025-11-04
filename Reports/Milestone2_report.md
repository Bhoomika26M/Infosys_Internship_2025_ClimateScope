# ClimateScope — Global Weather Data Analysis Dashboard  

###  Milestone 2: Core Analysis & Visualization Design

**Objectives:**  
- Perform statistical and comparative analysis on weather metrics.  
- Identify extreme weather events.  
- Visualize metric-wise patterns and correlations.  
- Design a structured dashboard layout with appropriate charts and maps.

## Metric-Wise Analysis and Visualizations 

### 1 Temperature Metrics  
**Columns used:**  
`temperature_celsius`, `feels_like_celsius`, `date`

| Visualization Type | Purpose | Parameters |
|--------------------|----------|-------------|
| **Line Chart** | Shows temperature trend over time | x=`date`, y=`temperature_celsius`, `feels_like_celsius` |
| **Histogram + KDE** | Displays temperature distribution density | `temperature_celsius` |
| **Boxplot (by Month)** | Shows monthly temperature variation | x=`month`, y=`temperature_celsius` |

---

### 2 Humidity & Visibility  
**Columns used:**  
`humidity`, `visibility_km`, `temperature_celsius`, `date`

| Visualization Type | Purpose | Parameters |
|--------------------|----------|-------------|
| **Scatter Plot** | Relation between humidity and temperature | x=`humidity`, y=`temperature_celsius` |
| **Line Chart** | Visibility trend over time | x=`date`, y=`visibility_km` |
| **Heatmap** | Correlation among humidity, visibility, and temperature | Columns: `humidity`, `visibility_km`, `temperature_celsius` |

---

### 3 Wind Metrics  
**Columns used:**  
`wind_kph`, `gust_kph`, `precip_mm`, `date`

| Visualization Type | Purpose | Parameters |
|--------------------|----------|-------------|
| **Line Chart** | Wind and gust trends | x=`date`, y=`wind_kph`, `gust_kph` |
| **Scatter Plot** | Relation between gusts and precipitation | x=`gust_kph`, y=`precip_mm` |

---

### 4 Precipitation & Pressure  
**Columns used:**  
`precip_mm`, `pressure_mb`, `date`

| Visualization Type | Purpose | Parameters |
|--------------------|----------|-------------|
| **Bar Chart** | Average monthly precipitation | x=`month`, y=`precip_mm` |
| **Line Chart** | Pressure trend over time | x=`date`, y=`pressure_mb` |
| **Scatter Plot** | Relation between pressure and precipitation | x=`pressure_mb`, y=`precip_mm` |

---

### 5 Air Quality Metrics  
**Columns used:**  
`air_quality_PM2.5`, `air_quality_PM10`, `air_quality_us-epa-index`, `country`, `date`

| Visualization Type | Purpose | Parameters |
|--------------------|----------|-------------|
| **Line Chart** | Air pollutant trends over time | x=`date`, y=`pollutant columns` |
| **Heatmap** | Correlation between air quality indicators | Columns: `air_quality_PM2.5`, `air_quality_PM10`, `air_quality_us-epa-index` |
| **Bar Chart** | Top 20 countries by AQI | Group by `country`, mean(`air_quality_us-epa-index`) |

---

### 6 Regional / Geographical Analysis  
**Columns used:**  
`country`, `latitude`, `longitude`, `temperature_celsius`, `humidity`, `pressure_mb`, `precip_mm`, `air_quality_us-epa-index`

| Visualization Type | Purpose | Parameters |
|--------------------|----------|-------------|
| **Choropleth Map** | Country-wise metric visualization | location=`country`, color=`selected metric` |
| **Scatter Mapbox** *(optional)* | Point-based map visualization | lat=`latitude`, lon=`longitude`, color=`selected parameter` |
| **Table** | Country-wise aggregate statistics | Group by `country`, metrics=`KEY_NUMERIC_COLUMNS` |

---

### 7 Temporal / Seasonal Patterns  
**Columns used:**  
`date`, `temperature_celsius`, `humidity`, `air_quality_PM2.5`

| Visualization Type | Purpose | Parameters |
|--------------------|----------|-------------|
| **Line Chart** | Monthly temperature trend | x=`month`, y=`temperature_celsius` |
| **Multi-Line Chart** | Seasonal comparison | y=`temperature_celsius`, `humidity`, `air_quality_PM2.5` |

---

### 8 Extreme Weather Events  
**Columns used:**  
`temperature_celsius`, `wind_kph`, `precip_mm`, `visibility_km`, `country`

**Analysis Steps:**  
- Calculate quantile thresholds:  
  - High temperature (≥ 95th percentile)  
  - High wind (≥ 95th percentile)  
  - Heavy precipitation (≥ 95th percentile)  
  - Low visibility (≤ 5th percentile)  
- Flag extreme records per country.  

| Visualization Type | Purpose | Parameters |
|--------------------|----------|-------------|
| **Data Table** | Display extreme events with flags | Columns: `country`, metric columns, `extreme_types` |
| **JSON Summary** | Display threshold values | Output from `detect_extreme_events()` |

---

##  Functions in `Analyse.py`  

| Function | Purpose | Description |
|-----------|----------|-------------|
| **`load_data(path)`** | Data loading & preprocessing | Reads CSV, converts date columns to datetime format, returns cleaned DataFrame. |
| **`descriptive_stats(df)`** | Statistical summary | Generates descriptive stats (mean, std, skew, kurtosis) for numeric columns. |
| **`country_aggregates(df, cols)`** | Aggregated country-level stats | Computes mean, median, std, min, max, count for each numeric column grouped by country. |
| **`correlation_matrix(df)`** | Correlation heatmap | Calculates Pearson correlation between numeric variables and plots a heatmap. |
| **`monthly_trends(df, cols)`** | Monthly analysis | Groups data by month and computes mean trends (especially temperature). Returns DataFrame and line plot. |
| **`detect_extreme_events(df)`** | Extreme weather detection | Calculates percentile-based thresholds for temp, wind, precip, and visibility; flags extreme rows; summarizes by country. |
| **`region_comparisons(df, metric)`** | Country comparisons | Aggregates statistics by metric (mean, median, std) and generates bar plots for top 20 countries. |

---

## Dashboard Design — `Streamlit-app.py`  

### Structure  
- **Sidebar Filters:**  
  - Country selection  
  - Date range filter  
  - Metric group selector  
- **Main Area:** Displays visualizations based on selected metric group.  
- **Tabs (Metric Groups):**  
  - Temperature  
  - Humidity & Visibility  
  - Wind  
  - Precipitation & Pressure  
  - Air Quality  
  - Regional / Geographical  
  - Temporal / Seasonal  
  - Extreme Events  

---