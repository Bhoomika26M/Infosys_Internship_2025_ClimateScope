import pandas as pd
import numpy as np

df = pd.read_csv("GlobalWeatherRepository.csv")  

print( df.shape)
print( df.dtypes)
print( df.head())

print(df.isnull().sum())

df=df.dropna(axis=1, thresh=len(df)*0.5)

num_cols = df.select_dtypes(include=[np.number]).columns
for col in num_cols:
    df[col] = df[col].fillna(df[col].median())  

cat_cols = df.select_dtypes(include=['object']).columns
for col in cat_cols:
    if df[col].isnull().sum() >0:
        df[col] = df[col].fillna(df[col].mode()[0])

df.columns =[col.strip().lower() for col in df.columns] 

if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

if 'temperature' in df.columns and df['temperature'].max() > 70:
    df['temperature'] = (df['temperature'] - 32) * 5.0/9.0

if 'wind_speed' in df.columns:
    df['wind_speed'] = df['wind_speed'] / 3.6

df = df.drop_duplicates()

if 'date' in df.columns:
    df = df.sort_values('date')
    monthly_data = df.resample('M').mean().reset_index()
else:
    monthly_data = df.copy()

monthly_data.to_csv("Cleaned_GlobalWeatherRepository.csv", index=False)



