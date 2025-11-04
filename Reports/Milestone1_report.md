# Milestone 1: Data Preparation & Initial Analysis

## Objective

Preparing and cleaning the **Global Weather Repository Dataset** for further analysis. This includes:

1. Identifying missing values, anomalies, and data coverage
2. Handling missing or inconsistent entries
3. Converting units and normalizing values
4. Aggregating data for time-based analysis



### Install required packages

```powershell
python -m pip install --upgrade pip
pip install pandas numpy scikit-learn
pip install plotly
pip install streamlit
pip install folium
pip install python-dotenv 
```



##  Dataset Location

* Raw dataset: `../data/GlobalWeatherRepository.csv`
* Cleaned dataset: `../data/Cleaned_GlobalWeatherRepository.csv`
* Aggregated daily averages: `../data/DailyAvg_GlobalWeatherRepository.csv`



## Data Cleaning Script

Below is the Python script (`clean_data.py`) used to preprocess the dataset.

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Load dataset from data/ folder
df = pd.read_csv("../data/GlobalWeatherRepository.csv")

# -------------------------------
# 1. Identify missing values & anomalies
# -------------------------------
print("Missing values:\n", df.isnull().sum())
print("\nDataset shape:", df.shape)
print("\nData coverage (unique countries):", df['country'].nunique())
print("Time coverage:", df['last_updated'].min(), "→", df['last_updated'].max())

# -------------------------------
# 2. Handle missing values
# -------------------------------
for col in df.columns:
    if df[col].dtype in ['float64', 'int64']:
        df[col].fillna(df[col].median(), inplace=True)
    else:
        df[col].fillna(df[col].mode()[0], inplace=True)

# -------------------------------
# 3. Convert units (keep SI units only)
# -------------------------------
drop_cols = [
    'temperature_fahrenheit', 'wind_mph', 'pressure_in',
    'precip_in', 'feels_like_fahrenheit', 'visibility_miles',
    'gust_mph'
]
df.drop(columns=drop_cols, inplace=True, errors="ignore")

df['last_updated'] = pd.to_datetime(df['last_updated'])

for col in ['sunrise', 'sunset', 'moonrise', 'moonset']:
    try:
        df[col] = pd.to_datetime(df[col], format='%I:%M %p').dt.time
    except:
        pass  

# -------------------------------
# 4. Normalize continuous variables
# -------------------------------
scaler = MinMaxScaler()
num_cols = df.select_dtypes(include=[np.number]).columns
df[num_cols] = scaler.fit_transform(df[num_cols])

# -------------------------------
# 5. Aggregate / Filter Data
# -------------------------------
df['date'] = df['last_updated'].dt.date
daily_avg = df.groupby(['country', 'location_name', 'date']).mean().reset_index()

# -------------------------------
# 6. Save cleaned dataset
# -------------------------------
df.to_csv("../data/Cleaned_GlobalWeatherRepository.csv", index=False)
daily_avg.to_csv("../data/DailyAvg_GlobalWeatherRepository.csv", index=False)

print("\n✅ Cleaning complete!")
```



## Results

* **Original dataset**: 97,824 rows × 41 columns
* **Cleaned dataset**: Redundant imperial units removed, missing values imputed, timestamps standardized, numeric values normalized
* **Aggregated dataset**: Daily averages per country and location


## Deliverables

* `../data/Cleaned_GlobalWeatherRepository.csv` → ready-to-use cleaned dataset
* `../data/DailyAvg_GlobalWeatherRepository.csv` → aggregated dataset for trend analysis
* `../data/MISSINGVALUES.txt` → missing values identified
* This `Milestone1.md` as documentation




