
# Climatescope Project – Milestone 2 Analysis Document

## Objective
To perform **data aggregation and visualization** of global weather data in order to identify climate trends and extreme temperature patterns.

## Process Overview

After cleaning the dataset in Milestone 1, Milestone 2 focused on **aggregating**, **analyzing**, and **visualizing** the processed data.

### 1️⃣ Data Aggregation
- Used **Pandas** to group and summarize the daily weather data.
- Aggregations were done in two forms:
  - **Monthly Aggregation:** Summarized daily weather data into monthly averages and totals.
  - **Seasonal Aggregation:** Grouped data by seasons (Winter, Summer, Monsoon, Autumn).

**Code Example:**
```python
monthly_df = df.groupby(['country', 'month']).agg({
    'temperature': 'mean',
    'humidity': 'mean',
    'precipitation': 'sum'
}).reset_index()
```

**Files Created:**
- `data/processed/monthly_agg.parquet`
- `data/processed/seasonal_agg.parquet`

### 2️⃣ Streamlit Dashboard Creation
A **Streamlit dashboard** was built to visually represent climate data interactively.

**Key Components:**
- **Choropleth Map:** Displays average temperature by country using **Plotly**.  
Each country is shaded according to its temperature range.

```python
fig = px.choropleth(df, 
                    locations='country', 
                    color='temperature', 
                    title='Average Temperature by Country')
st.plotly_chart(fig, use_container_width=True)
```

- **Detected Extremes Section:** Highlights regions experiencing **maximum and minimum** values for weather parameters.

```python
max_temp = df.loc[df['temperature'].idxmax()]
min_temp = df.loc[df['temperature'].idxmin()]
```

### Technologies Used
| Category | Tools/Technologies |
|-----------|--------------------|
| Programming Language | Python |
| Data Handling | Pandas |
| Data Format | CSV, Parquet |
| Visualization | Plotly Express |
| Web Framework | Streamlit |

### Key Outputs and Visuals
- **Global Map Visualization:** Shows temperature distribution across countries.
- **Detected Extremes Table:** Lists countries with highest and lowest recorded temperatures.
- **Aggregated Files:** Monthly and seasonal summaries stored for future trend analysis.

## Insights Gained
- Seasonal and monthly averages help identify **temperature variations** across regions.
- Map visualization shows **geographical climate differences**.
- Detected extremes highlight **climate anomalies** and **potential risk zones**.
- Learned how to integrate **Plotly graphs with Streamlit** for interactive analysis.

## Understanding and Learning
Through Milestone 2, I understood:
- How to use **groupby()** for data aggregation.
- How to create **interactive dashboards**.
- The process of identifying **climate extremes and trends**.
- The importance of **visual storytelling** in analysis.

## Next Steps
- Add filters in dashboard (by year, parameter, country).
- Implement time-series charts for trend analysis.
- Explore anomaly detection models for forecasting.
