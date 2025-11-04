import os
import pandas as pd
import numpy as np

# Input/output directories
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def main():
    # -----------------------------
    # 1. Load dataset
    # -----------------------------
    file = os.path.join(RAW_DIR, "GlobalWeatherRepository.csv")
    df = pd.read_csv(file, low_memory=False)

    # -----------------------------
    # 2. Parse dates
    # -----------------------------
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # -----------------------------
    # 3. Drop duplicates
    # -----------------------------
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    print(f"Dropped {before - after} duplicate rows.")

    # -----------------------------
    # 4. Handle missing values
    # -----------------------------
    num_cols = df.select_dtypes(include=[np.number]).columns
    for c in num_cols:
        df[c] = df[c].fillna(df[c].median())

    obj_cols = df.select_dtypes(include=["object"]).columns
    for c in obj_cols:
        df[c] = df[c].fillna("unknown")

    # -----------------------------
    # 5. Unit conversions
    # -----------------------------
    # Temperature
    if "temperature" in df.columns:
        # Detect if original is Kelvin
        if df["temperature"].dropna().min() > 180:
            df["temperature_c"] = df["temperature"] - 273.15
        else:
            df["temperature_c"] = df["temperature"]

        # Celsius → Fahrenheit
        df["temperature_f"] = (df["temperature_c"] * 9/5) + 32
        # Celsius → Kelvin
        df["temperature_k"] = df["temperature_c"] + 273.15

    # Wind speed
    if "wind_kph" in df.columns:
        df["wind_mph"] = df["wind_kph"] * 0.621371   # km/h → mph
        df["wind_mps"] = df["wind_kph"] / 3.6        # km/h → m/s

    # Precipitation
    if "precip_mm" in df.columns:
        df["precip_in"] = df["precip_mm"] / 25.4     # mm → inches

    # Pressure
    if "pressure_mb" in df.columns:
        df["pressure_hpa"] = df["pressure_mb"]       # mb → hPa (alias)

    # -----------------------------
    # 6. Save cleaned dataset
    # -----------------------------
    cleaned_path = os.path.join(PROCESSED_DIR, "cleaned_weather.csv")
    df.to_csv(cleaned_path, index=False)
    print(f"Cleaned dataset saved to {cleaned_path}")

    # -----------------------------
    # 7. Aggregate monthly averages
    # -----------------------------
    date_cols = [c for c in df.columns if str(df[c].dtype).startswith("datetime")]
    if date_cols:
        dt = date_cols[0]
        df = df.set_index(dt)

        monthly = df.resample("M").mean(numeric_only=True).reset_index()

        monthly_path = os.path.join(PROCESSED_DIR, "monthly_avg.csv")
        monthly.to_csv(monthly_path, index=False)
        print(f"Monthly averages saved to {monthly_path}")
    else:
        print("⚠️ No datetime column found for monthly aggregation.")

if __name__ == "__main__":
    main()
