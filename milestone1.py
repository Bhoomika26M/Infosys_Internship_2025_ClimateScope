import pandas as pd
import os

# --- Configuration (UPDATED PATH) ---
RAW_DATA_PATH = os.path.join("data", "raw_data", "GlobalWeatherRepository.csv")
PROCESSED_DATA_DIR = os.path.join("data", "processed")
CLEANED_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "cleaned_weather.csv")
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Define the essential columns for the ClimateScope project (Total 10 columns)
REQUIRED_COLUMNS = [
    'country',             # For regional comparison [cite: 82]
    'location_name',       # Specific location reference
    'latitude',            # For map visualizations [cite: 86]
    'longitude',           # For map visualizations [cite: 86]
    'last_updated',        # For time-series analysis [cite: 88]
    'temperature_celsius', # Key variable for analysis [cite: 72]
    'humidity',            # Key variable for analysis [cite: 72]
    'precip_mm',           # Key variable for analysis [cite: 72]
    'wind_kph',            # Key variable for analysis (in KPH) [cite: 72]
    'condition_text'       # General weather state
]


def load_raw_data():
    """Loads the raw weather data from the specified path."""
    try:
        # Load the raw data
        df = pd.read_csv(RAW_DATA_PATH)
        print(f"Raw data loaded successfully! Shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"FATAL ERROR: Raw data file not found at the confirmed path: {RAW_DATA_PATH}")
        print("Please ensure your data is named 'GlobalWeatherRepository.csv' and placed in the 'data/raw_data/' folder.")
        return None

def clean_and_preprocess(df):
    """
    Handles cleaning, type conversion, and feature selection (Milestone 1 tasks).
    """
    print("\nStarting data cleaning and preprocessing...")

    # 1. Feature Selection: Keep only the 10 required columns
    # This guarantees 'wind_kph' is present for Milestone 2[cite: 72].
    df_clean = df[REQUIRED_COLUMNS].copy()

    # 2. Convert Data Types [cite: 77]
    # Convert 'last_updated' to datetime
    df_clean['last_updated'] = pd.to_datetime(df_clean['last_updated'])

    # 3. Handle Missing or Inconsistent Entries (Missing Values/Anomalies) [cite: 74, 76]
    initial_rows = len(df_clean)
    
    # Drop rows where coordinates or primary metrics are completely null
    df_clean.dropna(subset=['latitude', 'longitude', 'temperature_celsius', 'wind_kph', 'humidity'], inplace=True)
    rows_dropped = initial_rows - len(df_clean)
    
    print(f"Dropped {rows_dropped} rows with critical missing values.")

    # Convert remaining primary numerical columns to numeric, coercing errors
    for col in ['temperature_celsius', 'humidity', 'precip_mm', 'wind_kph']:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        # Impute non-critical numerical missing values with the mean [cite: 76]
        df_clean[col].fillna(df_clean[col].mean(), inplace=True)
    
    # Check for the expected 10-column shape (98555, 10) found in your logs
    print(f"Cleaning complete. Final shape: {df_clean.shape}")
    return df_clean

# --- Main Execution Block ---
if __name__ == "__main__":
    if os.path.exists(CLEANED_DATA_PATH):
        # Always re-run the cleaning process if you are fixing an error
        print("Cleaned data file exists. Re-running cleaning to ensure 'wind_kph' is included.")
    
    df_raw = load_raw_data()
    
    if df_raw is not None:
        df_cleaned = clean_and_preprocess(df_raw)
        
        # Save the cleaned dataset (Milestone 1 Deliverable)
        df_cleaned.to_csv(CLEANED_DATA_PATH, index=False)
        print(f"\nSUCCESS: Cleaned and preprocessed data saved to: {CLEANED_DATA_PATH}")
        print("Milestone 1 is now complete. You can proceed to re-run milestone2_analysis.py with confidence!")