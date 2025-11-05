import pandas as pd


# 1. Load the dataset
data = pd.read_csv(r"C:\Users\malle\OneDrive\Desktop\climate-project\GlobalWeatherRepository.csv")

# 2. Inspect dataset structure
print("----- Dataset Structure -----")
print(data.info())  # Shows rows, columns, data types, memory usage
print("\n")

# 3. View first few rows
print("----- First 5 Rows -----")
print(data.head())
print("\n")

# 4. Identify missing values
print("----- Missing Values -----")
print(data.isnull().sum())
print("\n")

# 5. Identify anomalies (example: negative temperatures or wind speeds)
print("----- Anomalies Check -----")
print("Rows with negative temperatures:")
print(data[(data['temperature_celsius'] < -90) | (data['temperature_celsius'] > 60)])  # adjust realistic limits
print("Rows with negative wind speeds:")
print(data[data['wind_kph'] < 0])
print("\n")

# 6. Data coverage (basic statistics)
print("----- Data Coverage / Statistics -----")
print(data.describe())
print("\n")

# 7. Handle missing or inconsistent entries
# Example: Fill missing numeric values with column mean
numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
for col in numeric_cols:
    data[col].fillna(data[col].mean(), inplace=True)

# Fill missing text/objects with "Unknown"
text_cols = data.select_dtypes(include=['object']).columns
for col in text_cols:
    data[col].fillna("Unknown", inplace=True)

# 8. Convert units if needed
# Example: Celsius to Fahrenheit (if not already available)
if 'temperature_fahrenheit' not in data.columns:
    data['temperature_fahrenheit'] = data['temperature_celsius'] * 9/5 + 32

# 9. Normalize values (example: scale wind speed to 0-1)
data['wind_kph_normalized'] = (data['wind_kph'] - data['wind_kph'].min()) / (data['wind_kph'].max() - data['wind_kph'].min())

# 10. Aggregate or filter data
# Example: Filter rows for a specific country
country_data = data[data['country'] == "India"]

# Example: Aggregate by country (mean values)
agg_data = data.groupby('country')[['temperature_celsius', 'wind_kph']].mean().reset_index()

# 11. Save the cleaned and prepared dataset
data.to_csv("Clean_GlobalWeatherRepository.csv", index=False)
print("----- Cleaned dataset saved as 'Clean_GlobalWeatherRepository.csv' -----")

