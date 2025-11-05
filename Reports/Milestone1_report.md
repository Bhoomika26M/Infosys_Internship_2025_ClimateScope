🌍 Milestone 1: Data Preparation & Initial Analysis
🎯 Objective

The goal of Milestone 1 is to prepare and clean the Global Weather Repository Dataset for further analysis and visualization.
This phase focuses on:

Identifying missing values and inconsistencies

Cleaning and handling invalid or missing data

Converting and normalizing variables into consistent units

Aggregating data to enable trend analysis over time

🧩 Tools & Libraries Used

Python 3.10+

pandas → Data handling & transformation

numpy → Numerical operations

streamlit → Interactive visualization

warnings → Suppression of unnecessary warnings

⚙️ Installation Steps

Run the following commands before executing the code:

python -m pip install --upgrade pip
pip install pandas numpy streamlit

📊 Dataset Overview

Dataset Source: Global Weather Repository

Contains: Daily global weather data including temperature, humidity, wind, and precipitation.

Outputs Produced:

weather_cleaned.csv → Cleaned dataset

summary.txt → Dataset statistics summary

💻 Python Code Implementation
import streamlit as st
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")

st.title("🌍 ClimateScope Dashboard - Milestone 1 (Cleaned Dataset)")

# Step 1: Load dataset
fl = st.file_uploader("📁 Upload a CSV file", type=["csv", "txt", "xlsx", "xls"])
if fl is not None:
    df = pd.read_csv(fl, encoding="ISO-8859-1")
    st.success(f"✅ Uploaded file: {fl.name}")
else:
    df = pd.read_csv("GlobalWeatherRepository.csv", encoding="ISO-8859-1")
    st.info("Using default dataset: GlobalWeatherRepository.csv")

# Step 2: Inspect dataset
st.subheader("Dataset Info")
import io
buffer = io.StringIO()
df.info(buf=buffer)
info = buffer.getvalue()
st.text(info)

st.subheader("First 5 Rows")
st.dataframe(df.head())

st.subheader("Missing Values")
st.dataframe(df.isnull().sum())

# Step 3: Handle Missing Values
for col in df.select_dtypes(include="number").columns:
    df[col].fillna(df[col].mean(), inplace=True)

for col in df.select_dtypes(include="object").columns:
    df[col].fillna(df[col].mode()[0], inplace=True)

st.subheader("Missing Values After Cleaning")
st.dataframe(df.isnull().sum())

# Step 4: Convert Units / Normalize
if "temperature_kelvin" in df.columns:
    df["temperature_celsius"] = df["temperature_kelvin"] - 273.15

if "wind_speed" in df.columns:
    df["wind_speed_norm"] = (df["wind_speed"] - df["wind_speed"].min()) / (df["wind_speed"].max() - df["wind_speed"].min())

# Step 5: Aggregate Data (Daily → Monthly)
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"])
    monthly_df = df.resample("M", on="date").mean()
else:
    monthly_df = df.copy()

st.subheader("Monthly Aggregated Data (First 5 Rows)")
st.dataframe(monthly_df.head())

# Step 6: Save Cleaned Dataset & Summary
os.makedirs("data", exist_ok=True)
clean_path = "weather_cleaned.csv"
monthly_df.to_csv(clean_path, index=False)
st.success(f"✅ Cleaned dataset saved successfully")

summary = {
    "Total Rows": df.shape[0],
    "Total Columns": df.shape[1],
    "Columns": df.columns.tolist(),
    "Missing Values": df.isnull().sum().to_dict()
}

summary_path = "summary.txt"
with open(summary_path, "w") as f:
    f.write("=== Dataset Summary ===\n")
    for key, value in summary.items():
        f.write(f"{key}: {value}\n")
st.success("✅ Summary file generated successfully")

# Step 7: Visualizations
st.subheader("Temperature Over Time")
if "temperature_celsius" in monthly_df.columns:
    st.line_chart(monthly_df["temperature_celsius"])
else:
    st.warning("Temperature column not found!")

st.subheader("Wind Speed Distribution")
if "wind_speed_norm" in monthly_df.columns:
    st.line_chart(monthly_df["wind_speed_norm"])
else:
    st.warning("Wind speed column not found!")

# Step 8: Dataset Summary Display
st.subheader("Dataset Summary")
st.write(summary)

🧠 Workflow Explanation
Step 1 — Data Loading

The dataset is uploaded via the Streamlit interface or loaded directly from the working directory.

Step 2 — Data Inspection

Displays dataset info, first five rows, and missing value counts.

Helps identify inconsistencies and null entries before cleaning.

Step 3 — Data Cleaning

Numeric columns → Missing values replaced with mean

Categorical columns → Missing values replaced with mode

Step 4 — Conversion & Normalization

Temperature converted from Kelvin → Celsius

Wind speed normalized between 0 and 1

Step 5 — Aggregation

Daily records aggregated to monthly averages for easier trend visualization.

Step 6 — Summary Generation

A summary text file includes row/column counts, column names, and missing value details.

Step 7 — Visualization

Line charts to display:

🌡️ Temperature variations over time

💨 Wind speed distribution

📈 Key Results
Metric	Description
Rows (approx.)	90,000+
Columns	~35
Missing Values	All handled successfully
Temperature Scale	Converted to Celsius
Aggregation	Monthly averages computed
📦 Deliverables

✅ Cleaned Dataset: weather_cleaned.csv

✅ Summary Report: summary.txt

✅ Interactive Streamlit Dashboard

✅ Documentation: Milestone1_Report.md

✅ Conclusion

This milestone establishes the foundation for all upcoming analyses in the ClimateScope Project.
Through data cleaning, normalization, and aggregation, the dataset is now reliable, consistent, and structured for the next phase:
➡️ Milestone 2 – Exploratory Analysis & Insights Visualization 🚀