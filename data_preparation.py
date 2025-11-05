import pandas as pd

# Load the dataset
df = pd.read_csv("GlobalWeatherRepository.csv")

print("=== Dataset Inspection ===")
print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print("\nData types:")
print(df.dtypes)
print("\nMissing values per column:")
print(df.isnull().sum())
print("\nSample data:")
print(df.head())

# Data Cleaning
print("\n=== Data Cleaning ===")

# Convert last_updated to datetime
df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')

# Handle missing values
# For numeric columns, fill with mean
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

# For categorical columns, fill with mode or 'Unknown'
categorical_cols = df.select_dtypes(include=['object']).columns
for col in categorical_cols:
    df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown')

print("Missing values after cleaning:")
print(df.isnull().sum())

# Convert units if necessary (assuming data is already in metric, but check)
# Temperature is in Celsius, wind in kph, precip in mm, etc. Seems fine.

# Normalize values (optional, for now skip)

# Aggregate to monthly averages
print("\n=== Aggregation ===")
df['month'] = df['last_updated'].dt.to_period('M')

# Select key variables for aggregation
agg_cols = ['temperature_celsius', 'humidity', 'precip_mm', 'wind_kph', 'pressure_mb', 'uv_index']
monthly_avg = df.groupby(['country', 'month'])[agg_cols].mean().reset_index()

print(f"Monthly aggregated data shape: {monthly_avg.shape}")
print("Sample monthly data:")
print(monthly_avg.head())

# Save cleaned data
df.to_csv("cleaned_weather_data.csv", index=False)
monthly_avg.to_csv("monthly_weather_data.csv", index=False)

print("\nCleaned daily data saved to 'cleaned_weather_data.csv'")
print("Monthly aggregated data saved to 'monthly_weather_data.csv'")
