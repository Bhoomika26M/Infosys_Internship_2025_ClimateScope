print("DEBUG: Running make_visuals.py")  # Debug print to confirm running file

import os
import pandas as pd
import plotly.express as px

IN_MONTHLY = "data/processed/monthly_agg.parquet"

def make_choropleth(df):
    print("Creating choropleth...")
    country_avg = df.groupby('country')[['temperature_celsius', 'precip_mm']].mean().reset_index()
    fig = px.choropleth(
        country_avg,
        locations='country',
        locationmode='country names',
        color='temperature_celsius',
        hover_data=['precip_mm'],
        title='Average Temperature by Country'
    )
    fig.write_html("analysis/choropleth_temperature.html")
    print("✅ Choropleth saved to analysis/choropleth_temperature.html")

def make_heatmap(df):
    print("Creating heatmap...")
    df['month_num'] = pd.to_datetime(df['month']).dt.month
    pivot = df.groupby(['year', 'month_num'])['temperature_celsius'].mean().unstack(fill_value=None)
    fig = px.imshow(
        pivot,
        labels=dict(x="Month", y="Year", color="Temperature (°C)"),
        aspect="auto",
        title="Seasonal Heatmap"
    )
    fig.write_html("analysis/seasonal_heatmap.html")
    print("✅ Heatmap saved to analysis/seasonal_heatmap.html")

def main():
    if not os.path.exists(IN_MONTHLY):
        raise FileNotFoundError("Run aggregate_daily_to_monthly.py first.")
    df = pd.read_parquet(IN_MONTHLY)
    os.makedirs("analysis", exist_ok=True)
    make_choropleth(df)
    make_heatmap(df)

if __name__ == "__main__":
    main()
