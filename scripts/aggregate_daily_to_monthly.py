import os
import pandas as pd
print("DEBUG: This is the exact script running")


INPUT_PARQUET = "data/processed/cleaned_weather.parquet"
INPUT_CSV = "data/processed/cleaned_weather.csv"
OUT_MONTHLY = "data/processed/monthly_agg.parquet"
OUT_SEASONAL = "data/processed/seasonal_agg.parquet"

def load_data():
    if os.path.exists(INPUT_PARQUET):
        print("📦 Found cleaned_weather.parquet")
        df = pd.read_parquet(INPUT_PARQUET)
    elif os.path.exists(INPUT_CSV):
        print("📦 Found cleaned_weather.csv")
        df = pd.read_csv(INPUT_CSV)
    else:
        raise FileNotFoundError("❌ No cleaned file found in data/processed/")
    return df

def main():
    print("🚀 Starting aggregation script...")
    df = load_data()
    print("✅ Data loaded successfully, shape:", df.shape)

    # Print all columns present
    print("🧾 Columns found:", list(df.columns))

    # Identify date-like column from candidates
    date_col = None
    for candidate in ['date', 'last_updated', 'datetime', 'timestamp']:
        if candidate in df.columns:
            date_col = candidate
            print(f"🕓 Using '{candidate}' as the date column")
            break

    if date_col is None:
        print("❌ No date-like column found. Please check your CSV.")
        return
    else:
        print(f"🕓 Using '{date_col}' as the date column")

    # Convert chosen date column to datetime and drop invalid rows
    df['date'] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=['date'])

    # Extract year and month (timestamp at month-start) for aggregation
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.to_period('M').dt.to_timestamp()

    # Monthly aggregation
    print("📊 Aggregating to monthly averages...")
    monthly = df.groupby(['country', 'year', 'month']).agg({
        'temperature_celsius': 'mean',
        'humidity': 'mean',
        'precip_mm': 'sum',
        'wind_mps': 'mean'
    }).reset_index()

    os.makedirs("data/processed", exist_ok=True)
    monthly.to_parquet(OUT_MONTHLY, index=False)
    print(f"✅ Saved monthly aggregates to {OUT_MONTHLY} ({len(monthly)} rows)")

    # Seasonal aggregation helper function
    def season_of_month(m):
        if m in [12, 1, 2]:
            return 'DJF'
        if m in [3, 4, 5]:
            return 'MAM'
        if m in [6, 7, 8]:
            return 'JJA'
        return 'SON'

    # Apply season assignment
    df['season'] = df['date'].dt.month.apply(season_of_month)

    # Seasonal aggregation
    print("📊 Aggregating to seasonal averages...")
    seasonal = df.groupby(['country', 'year', 'season']).agg({
        'temperature_celsius': 'mean',
        'humidity': 'mean',
        'precip_mm': 'sum',
        'wind_mps': 'mean'
    }).reset_index()

    seasonal.to_parquet(OUT_SEASONAL, index=False)
    print(f"✅ Saved seasonal aggregates to {OUT_SEASONAL} ({len(seasonal)} rows)")

    print("🎉 Aggregation complete!")

if __name__ == "__main__":
    main()
