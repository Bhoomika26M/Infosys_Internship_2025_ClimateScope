 feature/milestone2
import pandas as pd
import numpy as np
import os

# === 1. Load Dataset ===
file_path = "data/global-weather-repository.csv"
df = pd.read_csv(file_path)
print("✅ Data loaded successfully!")
print("Shape:", df.shape)
print(df.head())

# === 2. Inspect Columns & Data Types ===
print("\nColumn info:")
print(df.info())

# === 3. Handle Missing Values ===
# Drop rows with missing critical weather data
critical_cols = [c for c in df.columns if any(k in c.lower() for k in ["temp", "humid", "precip", "wind"])]
df = df.dropna(subset=critical_cols, how="any")

# Fill remaining missing numeric values with column means
df = df.fillna(df.mean(numeric_only=True))

# === 4. Convert Temperature Units if needed ===
if "temperature" in df.columns:
    if df["temperature"].mean() > 100:  # likely Kelvin
        df["temperature"] = df["temperature"] - 273.15

# === 5. Normalize Temperature ===
if "temperature" in df.columns:
    df["temperature_norm"] = (df["temperature"] - df["temperature"].min()) / (
        df["temperature"].max() - df["temperature"].min()
    )

# === 6. Convert Date & Aggregate to Monthly ===
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year_month"] = df["date"].dt.to_period("M")
    monthly = df.groupby(["year_month", "country"], as_index=False).mean(numeric_only=True)
else:
    monthly = df.copy()

# === 7. Save Cleaned Data ===
os.makedirs("processed", exist_ok=True)
out_path = "processed/cleaned_weather.csv"
monthly.to_csv(out_path, index=False)
print(f"✅ Cleaned dataset saved → {out_path}")

# === 8. Generate Summary ===
summary = {
    "num_rows": len(monthly),
    "columns": monthly.columns.tolist(),
    "missing_values": monthly.isna().sum().to_dict()
}

print("\n=== Summary ===")
for k, v in summary.items():
    print(f"{k}: {v}")


df = df[(df["temperature"] >= -90) & (df["temperature"] <= 60)]
df = df[(df["humidity"] >= 0) & (df["humidity"] <= 100)]
if "precip_mm" in df.columns:
    df = df[df["precip_mm"] >= 0]

# Remove duplicate rows if any
duplicate_count = df.duplicated().sum()
print("Duplicate rows found:", duplicate_count)
df = df.drop_duplicates()

import pandas as pd
import numpy as np
import os
file_path = "data/global-weather-repository.csv"
df = pd.read_csv(file_path)
print("Data loaded successfully!")
print("Shape:", df.shape)
print(df.head())
print("\nColumn info:")
print(df.info())
critical_cols = [c for c in df.columns if any(k in c.lower() for k in ["temp", "humid", "precip", "wind"])]
df = df.dropna(subset=critical_cols, how="any")
df = df.fillna(df.mean(numeric_only=True))
if "temperature" in df.columns:
    if df["temperature"].mean() > 100:  # likely Kelvin
        df["temperature"] = df["temperature"] - 273.15
if "temperature" in df.columns:
    df["temperature_norm"] = (df["temperature"] - df["temperature"].min()) / (
        df["temperature"].max() - df["temperature"].min()
    )
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year_month"] = df["date"].dt.to_period("M")
    monthly = df.groupby(["year_month", "country"], as_index=False).mean(numeric_only=True)
else:
    monthly = df.copy()
os.makedirs("processed", exist_ok=True)
out_path = "processed/cleaned_weather.csv"
monthly.to_csv(out_path, index=False)
print(f"Cleaned dataset saved → {out_path}")
summary = {
    "num_rows": len(monthly),
    "columns": monthly.columns.tolist(),
    "missing_values": monthly.isna().sum().to_dict()
}

print("\n=== Summary ===")
for k, v in summary.items():
    print(f"{k}: {v}")

main
