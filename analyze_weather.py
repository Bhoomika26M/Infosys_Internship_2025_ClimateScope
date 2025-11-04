import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Step 1: Load Dataset
df = pd.read_csv(r"C:\Users\nithi\Downloads\GlobalWeatherRepository.csv")  # change filename if needed

# Step 2: Inspect Dataset
print("\n--- Dataset Head ---")
print(df.head())

print("\n--- Info ---")
print(df.info())

print("\n--- Summary Statistics ---")
print(df.describe(include='all'))

print("\n--- Column Names ---")
print(df.columns)

# Step 3: Identify Missing Values and Anomalies
print("\n--- Missing Values ---")
print(df.isnull().sum())

print("\n--- Duplicate Rows ---")
print(df.duplicated().sum())

# Optional: Heatmap of missing values
sns.heatmap(df.isnull(), cbar=False)
plt.title("Missing Values Heatmap")
plt.show()

# Step 4: Handle Missing or Inconsistent Entries
# Option 1: Drop rows with missing critical values
df_cleaned = df.dropna(subset=["temperature", "humidity", "date"])  # change as needed

# Option 2: Fill missing with mean/median (for continuous variables)
df_cleaned["temperature"] = df_cleaned["temperature"].fillna(df_cleaned["temperature"].mean())

# Step 5: Convert Units / Normalize
# Example: Convert temperature from Kelvin to Celsius
if df_cleaned["temperature"].max() > 100:  # likely in Kelvin
    df_cleaned["temperature_C"] = df_cleaned["temperature"] - 273.15

# Normalize a variable (e.g., humidity 0-1)
df_cleaned["humidity_norm"] = df_cleaned["humidity"] / 100

# Step 6: Convert date column and aggregate (e.g., daily to monthly average)
df_cleaned["date"] = pd.to_datetime(df_cleaned["date"])
df_cleaned.set_index("date", inplace=True)

monthly_avg = df_cleaned.resample("M").mean(numeric_only=True)
print("\n--- Monthly Averages ---")
print(monthly_avg.head())

# Save cleaned dataset and summary
df_cleaned.to_csv("cleaned_weather_data.csv")
monthly_avg.to_csv("monthly_averages.csv")

# Optional: Save summary info to a text file
with open("data_summary.txt", "w") as f:
    f.write(str(df_cleaned.describe()))
    f.write("\n\nMissing Values:\n")
    f.write(str(df_cleaned.isnull().sum()))
    f.write("\n\nColumns:\n")
    f.write(str(df_cleaned.columns.tolist()))