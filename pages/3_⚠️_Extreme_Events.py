import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_generator import generate_climate_data
from sidebar_filters import render_sidebar_filters

st.set_page_config(page_title="Extreme Events", page_icon="⚠️", layout="wide")

@st.cache_data
def load_data():
    return generate_climate_data()

df = load_data()
filtered_df = render_sidebar_filters(df)

st.session_state['filtered_df'] = filtered_df
st.session_state['full_df'] = df

st.title("⚠️ Extreme Events Analysis")
st.markdown("### Climate Extremes and Frequency")

filtered_df = filtered_df.copy()
full_df = df.copy()

st.markdown("---")
st.subheader("Extreme Records: Global vs Regional")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🔥 Hottest Days (Global Top 5)")
    global_hot = full_df.nlargest(5, 'Temperature')[['Date', 'Country', 'Temperature', 'Region']]
    global_hot['Temperature'] = global_hot['Temperature'].apply(lambda x: f"{x:.2f}°C")
    st.dataframe(global_hot.reset_index(drop=True), use_container_width=True)

with col2:
    st.markdown("#### 🔥 Hottest Days (Regional Top 5)")
    regional_hot = filtered_df.nlargest(5, 'Temperature')[['Date', 'Country', 'Temperature', 'Region']]
    regional_hot['Temperature'] = regional_hot['Temperature'].apply(lambda x: f"{x:.2f}°C")
    st.dataframe(regional_hot.reset_index(drop=True), use_container_width=True)

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    st.markdown("#### ❄️ Coldest Days (Global Top 5)")
    global_cold = full_df.nsmallest(5, 'Temperature')[['Date', 'Country', 'Temperature', 'Region']]
    global_cold['Temperature'] = global_cold['Temperature'].apply(lambda x: f"{x:.2f}°C")
    st.dataframe(global_cold.reset_index(drop=True), use_container_width=True)

with col4:
    st.markdown("#### ❄️ Coldest Days (Regional Top 5)")
    regional_cold = filtered_df.nsmallest(5, 'Temperature')[['Date', 'Country', 'Temperature', 'Region']]
    regional_cold['Temperature'] = regional_cold['Temperature'].apply(lambda x: f"{x:.2f}°C")
    st.dataframe(regional_cold.reset_index(drop=True), use_container_width=True)

st.markdown("---")

col5, col6 = st.columns(2)

with col5:
    st.markdown("#### 💨 Windiest Days (Global Top 5)")
    global_wind = full_df.nlargest(5, 'Wind Speed')[['Date', 'Country', 'Wind Speed', 'Region']]
    global_wind['Wind Speed'] = global_wind['Wind Speed'].apply(lambda x: f"{x:.2f} m/s")
    st.dataframe(global_wind.reset_index(drop=True), use_container_width=True)

with col6:
    st.markdown("#### 💨 Windiest Days (Regional Top 5)")
    regional_wind = filtered_df.nlargest(5, 'Wind Speed')[['Date', 'Country', 'Wind Speed', 'Region']]
    regional_wind['Wind Speed'] = regional_wind['Wind Speed'].apply(lambda x: f"{x:.2f} m/s")
    st.dataframe(regional_wind.reset_index(drop=True), use_container_width=True)

st.markdown("---")

col7, col8 = st.columns(2)

with col7:
    st.markdown("#### 🌧️ Heaviest Precipitation (Global Top 5)")
    global_prec = full_df.nlargest(5, 'Precipitation')[['Date', 'Country', 'Precipitation', 'Region']]
    global_prec['Precipitation'] = global_prec['Precipitation'].apply(lambda x: f"{x:.2f} mm")
    st.dataframe(global_prec.reset_index(drop=True), use_container_width=True)

with col8:
    st.markdown("#### 🌧️ Heaviest Precipitation (Regional Top 5)")
    regional_prec = filtered_df.nlargest(5, 'Precipitation')[['Date', 'Country', 'Precipitation', 'Region']]
    regional_prec['Precipitation'] = regional_prec['Precipitation'].apply(lambda x: f"{x:.2f} mm")
    st.dataframe(regional_prec.reset_index(drop=True), use_container_width=True)

st.markdown("---")
st.subheader("Extreme Frequency Analysis")
st.markdown("Track hazardous climate conditions by defining custom thresholds")

metrics = ['Temperature', 'Humidity', 'Wind Speed', 'Precipitation']

col_a, col_b, col_c = st.columns([2, 1, 1])

with col_a:
    selected_metric = st.selectbox("Select Metric", metrics)

with col_b:
    operator = st.selectbox("Condition", ['≥ (Greater than or equal)', '≤ (Less than or equal)'])

with col_c:
    if selected_metric == 'Temperature':
        threshold = st.number_input("Threshold", value=30.0, step=1.0)
    elif selected_metric == 'Humidity':
        threshold = st.number_input("Threshold", value=70.0, step=5.0)
    elif selected_metric == 'Wind Speed':
        threshold = st.number_input("Threshold", value=10.0, step=1.0)
    else:
        threshold = st.number_input("Threshold", value=10.0, step=1.0)

filtered_df['Month'] = filtered_df['Date'].dt.month_name()
filtered_df['Month_Num'] = filtered_df['Date'].dt.month

if '≥' in operator:
    extreme_events = filtered_df[filtered_df[selected_metric] >= threshold]
else:
    extreme_events = filtered_df[filtered_df[selected_metric] <= threshold]

month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

extreme_counts = extreme_events.groupby('Month').size().reset_index(name='Event Count')
extreme_counts['Month'] = pd.Categorical(extreme_counts['Month'], categories=month_order, ordered=True)
extreme_counts = extreme_counts.sort_values('Month')

fig_extreme = px.bar(
    extreme_counts,
    x='Month',
    y='Event Count',
    title=f"Number of Days per Month where {selected_metric} {operator.split()[0]} {threshold}",
    color='Event Count',
    color_continuous_scale='Reds'
)

fig_extreme.update_layout(height=500)
st.plotly_chart(fig_extreme, use_container_width=True)

total_events = extreme_counts['Event Count'].sum()
st.info(f"**Total Extreme Events:** {total_events} days ({total_events/len(filtered_df)*100:.2f}% of filtered data)")

st.markdown("---")
st.subheader("Event Distribution by Country")

country_extreme = extreme_events.groupby('Country').size().reset_index(name='Event Count')
country_extreme = country_extreme.sort_values('Event Count', ascending=False).head(15)

fig_country = px.bar(
    country_extreme,
    x='Country',
    y='Event Count',
    title=f"Top 15 Countries with Most Extreme Events ({selected_metric} {operator.split()[0]} {threshold})",
    color='Event Count',
    color_continuous_scale='Oranges'
)

fig_country.update_layout(height=400, xaxis_tickangle=-45)
st.plotly_chart(fig_country, use_container_width=True)
