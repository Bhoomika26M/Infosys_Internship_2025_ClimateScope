import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# ---------- Load Dataset ----------
df = pd.read_csv("../data/GlobalWeatherRepository.csv")
print("Initial dataset shape:", df.shape)
print("Initial columns:", list(df.columns))
print("Initial missing values:\n", df.isnull().sum().sort_values(ascending=False).head(10))

# ---------- Handle Missing Values ----------
for col in df.columns:
    if df[col].dtype in [np.float64, np.int64]:
        df[col] = df[col].fillna(df[col].median())
    else:
        
        df[col] = df[col].fillna(df[col].mode()[0])

print("\n✅ Missing values handled.")
print("Remaining missing values:\n", df.isnull().sum().sum())

# ---------- Convert Units ----------
if "temperature_fahrenheit" in df.columns and "temperature_celsius" in df.columns:
    df["temperature_celsius_calc"] = (df["temperature_fahrenheit"] - 32) * 5/9
    mismatched = np.sum(~np.isclose(df["temperature_celsius"], df["temperature_celsius_calc"], atol=0.5))
    print(f"\nTemperature mismatches corrected: {mismatched}")
    df["temperature_celsius"] = np.where(
        np.isclose(df["temperature_celsius"], df["temperature_celsius_calc"], atol=0.5),
        df["temperature_celsius"],
        df["temperature_celsius_calc"]
    )
    df.drop(columns=["temperature_celsius_calc"], inplace=True)

if "pressure_in" in df.columns and "pressure_mb" in df.columns:
    df["pressure_mb_calc"] = df["pressure_in"] * 33.8639
    mismatched = np.sum(~np.isclose(df["pressure_mb"], df["pressure_mb_calc"], atol=1))
    print(f"Pressure mismatches corrected: {mismatched}")
    df["pressure_mb"] = np.where(
        np.isclose(df["pressure_mb"], df["pressure_mb_calc"], atol=1),
        df["pressure_mb"],
        df["pressure_mb_calc"]
    )
    df.drop(columns=["pressure_mb_calc"], inplace=True)

# ---------- Normalize numeric values ----------
scaler = MinMaxScaler()
numeric_cols = df.select_dtypes(include=np.number).columns
print("\nNumeric columns to normalize:", list(numeric_cols))

before_norm_stats = df[numeric_cols].describe().loc[["min", "max"]]
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
after_norm_stats = df[numeric_cols].describe().loc[["min", "max"]]

print("\nBefore normalization:\n", before_norm_stats)
print("\nAfter normalization:\n", after_norm_stats)

# ---------- Date Parsing ----------
df["date"] = pd.to_datetime(df["last_updated"]).dt.date
print("\nDate range:", df["date"].min(), "to", df["date"].max())

# ---------- Aggregate Data (daily averages) ----------
daily_avg = df.groupby(["country", "location_name", "date"])[numeric_cols].mean().reset_index()
print("\nAggregated dataset shape:", daily_avg.shape)
print("Sample aggregated data:\n", daily_avg.head(3))

# ---------- Save Results ----------
df.to_csv("../data/GlobalWeatherRepository_cleaned.csv", index=False)
daily_avg.to_csv("../data/GlobalWeatherRepository_daily.csv", index=False)

print("\n✅ Cleaning completed successfully.")
print("Cleaned dataset saved as: GlobalWeatherRepository_cleaned.csv")
print("Daily averages saved as: GlobalWeatherRepository_daily.csv")
