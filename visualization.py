import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import pycountry
# Load default dataset safely
try:
    default_df = pd.read_csv("Cleaned_GlobalWeatherRepository.csv", parse_dates=['last_updated'])
except Exception:
    default_df = pd.DataFrame()

# Sidebar
st.sidebar.header("Filters")

# CSV Upload
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])
st.sidebar.markdown("""
**Upload Format Requirements**  
- Must include: `date`, `country`, `temperature_celsius`, `humidity`, `precip_mm`, `wind_kph`    
- Missing columns will disable related visuals.
""")

# Use uploaded file if valid, else fallback to default
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, parse_dates=['date'])

    except Exception:
        df = pd.DataFrame()
else:
    df = default_df.copy()
    if not df.empty:
        df.rename(columns={'last_updated': 'date'}, inplace=True)

# Preprocess
if not df.empty and 'date' in df.columns:
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    if 'country' in df.columns:
        df['country'] = df['country'].apply(lambda x: str(x).encode('ascii', 'ignore').decode())

# Sidebar filters
if 'country' in df.columns:
    selected_country = st.sidebar.selectbox("Primary Country", df['country'].unique())
    compare_countries = st.sidebar.multiselect("Compare Countries", df['country'].unique())
else:
    selected_country = None
    compare_countries = []

if 'date' in df.columns:
    date_range = st.sidebar.date_input("Select Date Range", [df['date'].min(), df['date'].max()])

else:
    date_range = []

# Determine comparison mode
is_comparing = len(compare_countries) > 0
selected_countries = list(set(compare_countries + [selected_country])) if is_comparing else df['country'].unique()

# Filtered data
if selected_country and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = df[
        (df['country'].isin(selected_countries)) &
        (df['date'] >= start_date) &
        (df['date'] <= end_date)
    ]
else:
    filtered_df = pd.DataFrame()

# Key Insights Function
def generate_key_insights(df, primary_country, is_comparing, selected_countries):
    if df.empty or 'temperature_celsius' not in df.columns:
        return "Temperature data missing. Summary insights unavailable."

    if is_comparing:
        subset = df[df['country'].isin(selected_countries)]
        avg_temp = subset.groupby("country")["temperature_celsius"].mean()
        primary_avg = avg_temp.get(primary_country, np.nan)
        insights = f"- **{primary_country} Average Temperature:** {primary_avg:.2f} °C\n"
        insights += f"- **Selected Countries Average:** {avg_temp.mean():.2f} °C\n"
        insights += f"- **Hottest Among Selected:** {avg_temp.idxmax()} ({avg_temp.max():.2f} °C)\n"
        insights += f"- **Coldest Among Selected:** {avg_temp.idxmin()} ({avg_temp.min():.2f} °C)"
    else:
        global_avg = df["temperature_celsius"].mean()
        primary_avg = df[df["country"] == primary_country]["temperature_celsius"].mean()
        insights = f"- **{primary_country} Average Temperature:** {primary_avg:.2f} °C\n"
        insights += f"- **Global Average Temperature:** {global_avg:.2f} °C\n"
        insights += f"- **Difference from Global Average:** {primary_avg - global_avg:+.2f} °C"
    return insights

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Summary",
    "📈 Visualizations",
    "⚠️ Extreme Weather Trends",
    "🗺️ Global Temperature Map"
])

# Tab 1: Summary
with tab1:
    st.subheader("Key Insights")
    st.markdown(generate_key_insights(filtered_df, selected_country, is_comparing, selected_countries))

    st.subheader("Summary Statistics Table")
    summary_cols = ['temperature_celsius', 'precip_mm', 'wind_kph']
    available_summary = [col for col in summary_cols if col in filtered_df.columns]
    if available_summary:
        summary_data = {
            "Count": filtered_df[available_summary].count(),
            "Mean": filtered_df[available_summary].mean(),
            "Min": filtered_df[available_summary].min(),
            "Max": filtered_df[available_summary].max()
        }
        summary_df = pd.DataFrame(summary_data).T.round(2)
        st.dataframe(summary_df)
    else:
        st.info("Summary statistics unavailable due to missing temperature, precipitation, or wind data.")

# Tab 2: Visualizations
with tab2:
    st.subheader("Temperature Trend")
    if 'date' in filtered_df.columns and 'temperature_celsius' in filtered_df.columns:
        fig, ax = plt.subplots(figsize=(12, 6))
        if is_comparing:
            for country in selected_countries:
                country_df = filtered_df[filtered_df['country'] == country]
                daily_avg = country_df.groupby('date')['temperature_celsius'].mean()
                ax.plot(daily_avg.index, daily_avg.values, label=country,
                        linewidth=2 if country == selected_country else 1,
                        linestyle='-' if country == selected_country else '--')
            ax.set_title('Temperature Trends Among Selected Countries')
            ax.legend()
        else:
            daily_avg = filtered_df.groupby('date')['temperature_celsius'].mean()
            ax.plot(daily_avg.index, daily_avg.values, color='tomato')
            ax.set_title(f'Temperature Trend for {selected_country}')
        ax.set_xlabel('Date')
        ax.set_ylabel('Temperature (°C)')
        ax.grid(True)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Temperature trend unavailable due to missing data.")

    st.subheader("Temperature vs Humidity")
    if 'temperature_celsius' in filtered_df.columns and 'humidity' in filtered_df.columns:
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.scatter(filtered_df['temperature_celsius'], filtered_df['humidity'], alpha=0.5, c='royalblue')
        ax2.set_title('Temperature vs Humidity')
        ax2.set_xlabel('Temperature (°C)')
        ax2.set_ylabel('Humidity (%)')
        ax2.grid(True)
        st.pyplot(fig2)
        plt.close(fig2)

    else:
        st.info("Scatterplot unavailable due to missing data.")

    st.subheader("Monthly Temperature Trends Across Years")
    if 'year' in filtered_df.columns and 'month' in filtered_df.columns and 'temperature_celsius' in filtered_df.columns:
       monthly_trend = filtered_df.groupby(['year', 'month'])['temperature_celsius'].mean().unstack()
       if monthly_trend.empty:
        st.info("ℹ️ No data available to plot the monthly temperature trends across years.")
       else:
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        sns.heatmap(monthly_trend, cmap='YlOrRd', annot=True, fmt=".1f", ax=ax3)
        ax3.set_title('Monthly Temperature Trends Across Years')
        st.pyplot(fig3)
        plt.close(fig3)
    else:
        st.info("ℹ️ Monthly trends unavailable due to missing or invalid columns in dataset.")

    st.subheader("Average Monthly Temperature")
    if 'month' in filtered_df.columns and 'temperature_celsius' in filtered_df.columns:
        monthly_avg_temp = filtered_df.groupby('month')['temperature_celsius'].mean()
        fig4, ax4 = plt.subplots(figsize=(10, 5))
        ax4.plot(monthly_avg_temp.index, monthly_avg_temp.values, marker='o', color='teal')
        ax4.set_title('Average Monthly Temperature' + (" (Selected Countries)" if is_comparing else " (Global)"))
        ax4.set_xlabel("Month")
        ax4.set_ylabel("Temperature (°C)")
        st.pyplot(fig4)
        plt.close(fig4)
    else:
        st.info("Monthly average temperature unavailable.")

    st.subheader("Monthly Temperature Heatmap by Country")
    if 'country' in filtered_df.columns and 'month' in filtered_df.columns and 'temperature_celsius' in filtered_df.columns:
        monthly_avg = filtered_df.groupby(['country', 'month'])['temperature_celsius'].mean().unstack()
        fig5, ax5 = plt.subplots(figsize=(14, 8))
        sns.heatmap(monthly_avg, cmap='coolwarm', annot=False, ax=ax5)
        ax5.set_title('Monthly Temperature Heatmap by Country')
        st.pyplot(fig5)
        plt.close(fig5)
    else:
        st.info("Country-wise heatmap unavailable.")

    st.subheader("Custom Scatterplot")
    numeric_cols = ['temperature_celsius', 'humidity', 'precip_mm', 'wind_kph']
    available_cols = [col for col in numeric_cols if col in filtered_df.columns]
    if len(available_cols) >= 2:
        x_var = st.selectbox("X-axis Variable", available_cols, index=0)
        y_var = st.selectbox("Y-axis Variable", available_cols, index=1)
        fig6, ax6 = plt.subplots(figsize=(8, 5))
        ax6.scatter(filtered_df[x_var], filtered_df[y_var], alpha=0.6, c='darkgreen')
        ax6.set_title(f"{x_var} vs {y_var}")
        ax6.set_xlabel(x_var)
        ax6.set_ylabel(y_var)
        st.pyplot(fig6)
        plt.close(fig6)
    else:
        st.info("Custom scatterplot unavailable due to missing variables.")

    st.subheader("Histogram")
    if available_cols:
        hist_var = st.selectbox("Histogram Variable", available_cols)
        bins = st.slider("Number of Bins", min_value=10, max_value=100, value=30)
        fig7, ax7 = plt.subplots(figsize=(8, 5))
        sns.histplot(filtered_df[hist_var], bins=bins, kde=True, ax=ax7, color='orange')
        ax7.set_title(f"Distribution of {hist_var}")
        ax7.set_xlabel(hist_var)
        st.pyplot(fig7)
        plt.close(fig7)
    else:
        st.info("Histogram unavailable due to missing data.")

    st.subheader("Boxplot of Weather Variables")
    if available_cols:
        fig8, ax8 = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=filtered_df[available_cols], ax=ax8)
        ax8.set_title("Boxplot of Weather Variables")
        st.pyplot(fig8)
        plt.close(fig8)
    else:
        st.info("Boxplot unavailable due to missing data.")

# Tab 3: Extreme Weather Trends
with tab3:
    st.subheader("Extreme Weather Events")
    if not filtered_df.empty:
        extreme_temp = filtered_df[filtered_df['temperature_celsius'] > filtered_df['temperature_celsius'].quantile(0.99)] if 'temperature_celsius' in filtered_df.columns else pd.DataFrame()
        extreme_precip = filtered_df[filtered_df['precip_mm'] > filtered_df['precip_mm'].quantile(0.99)] if 'precip_mm' in filtered_df.columns else pd.DataFrame()
        extreme_wind = filtered_df[filtered_df['wind_kph'] > filtered_df['wind_kph'].quantile(0.99)] if 'wind_kph' in filtered_df.columns else pd.DataFrame()
        extreme_events = pd.concat([extreme_temp, extreme_precip, extreme_wind]).drop_duplicates()

        if extreme_events.empty:
            st.info("No extreme weather events found for the selected filters.")
        else:
            st.dataframe(extreme_events[['date', 'country', 'temperature_celsius', 'precip_mm', 'wind_kph']])

            st.subheader("Extreme Event Counts by Country")
            if 'country' in extreme_events.columns:
                event_counts = extreme_events['country'].value_counts()
                fig9, ax9 = plt.subplots(figsize=(10, 5))
                event_counts.plot(kind='bar', color='crimson', ax=ax9)
                ax9.set_title("Extreme Event Counts by Country")
                ax9.set_xlabel("Country")
                ax9.set_ylabel("Event Count")
                st.pyplot(fig9)
                plt.close(fig9)
    else:
        st.info("Extreme weather trends unavailable due to missing or filtered data.")

# Tab 4: Global Temperature Map
with tab4:
    st.subheader("Global Temperature Map")
    if not df.empty and 'country' in df.columns and 'temperature_celsius' in df.columns:
        map_source = filtered_df if not filtered_df.empty else df
        if 'country' not in map_source.columns or 'temperature_celsius' not in map_source.columns:
            st.info("ℹ️ Map cannot be displayed — missing 'country' or 'temperature_celsius' data.")
        else:
            try:
                map_data = map_source.groupby('country')['temperature_celsius'].mean().reset_index()

                def get_iso3(country_name):
                    try:
                        return pycountry.countries.lookup(country_name).alpha_3
                    except LookupError:
                        return None

                map_data["iso_alpha"] = map_data["country"].apply(get_iso3)
                map_data = map_data.dropna(subset=["iso_alpha"])

                if not map_data.empty:
                    fig10 = px.choropleth(
                        map_data,
                        locations="iso_alpha",
                        locationmode="ISO-3",
                        color="temperature_celsius",
                        color_continuous_scale="RdYlBu_r",
                        title="Average Temperature by Country" if not is_comparing else "Average Temperature Among Selected Countries"
                    )
                    st.plotly_chart(fig10, use_container_width=True)
                else:
                    st.info("ℹ️ Map data unavailable after filtering.")
            except Exception as e:
                st.info(f"⚠️ Map could not be generated due to an error: {e}")
    else:
        st.info("ℹ️ Choropleth map cannot be rendered due to missing or invalid data.")

# Download Section
st.header("📥 Download Data")
if not filtered_df.empty:
        st.download_button(
        label="Download Filtered Data",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_weather.csv",
        mime="text/csv"
    )
else:
    st.info("No filtered data available to download.")