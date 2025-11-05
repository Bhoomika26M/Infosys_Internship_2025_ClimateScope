import pandas as pd
df = pd.read_csv("data/GlobalWeatherRepository.csv")
# # Check missing values
print("\nMissing values per column:")
print(df.isnull().sum())

# Percentage of missing values
print("\nPercentage of missing values per column:")
print((df.isnull().sum() / len(df)) * 100)

# Check data ranges 
print("\nData Ranges:")
for col in df.select_dtypes(include=['float64', 'int64']).columns:
    print(f"{col}: min={df[col].min()}, max={df[col].max()}")

df = pd.read_csv("data/GlobalWeatherRepository.csv")
df_cleaned = df.dropna()
df_filled = df.fillna(df.mean(numeric_only=True))
df_filled.to_csv("data/GlobalWeatherRepository_cleaned.csv", index=False)
print("\nCleaned dataset saved as 'GlobalWeatherRepository_cleaned.csv'")


df = pd.read_csv("data/GlobalWeatherRepository.csv")
if 'temperature' in df.columns:
    df['temperature_C'] = df['temperature'] - 273.15
    print("Temperature column converted from Kelvin to Celsius ")
    print(df[['temperature', 'temperature_C']].head())  # show first 5 rows
else:
    print("No 'temperature' column found in dataset ")



from sklearn.preprocessing import MinMaxScaler
df = pd.read_csv("data/GlobalWeatherRepository_cleaned.csv")
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
scaler = MinMaxScaler()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
df.to_csv("data/GlobalWeatherRepository_normalized.csv", index=False)
print("Normalized dataset saved as GlobalWeatherRepository_normalized.csv")



df = pd.read_csv("data/GlobalWeatherRepository_cleaned.csv")
df['last_updated'] = pd.to_datetime(df['last_updated'])
monthly_avg = df.groupby(df['last_updated'].dt.to_period('M')).mean(numeric_only=True)
monthly_avg.to_csv("data/GlobalWeatherRepository_monthly.csv")
print(" Monthly aggregated dataset saved as GlobalWeatherRepository_monthly.csv")
