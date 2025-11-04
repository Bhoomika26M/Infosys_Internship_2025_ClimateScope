import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import io

def add_cohesive_climate_style():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(rgba(15, 32, 39, 0.8), rgba(15, 32, 39, 0.8)),
                        url('https://images.unsplash.com/photo-1435224654926-ecc9f7fa028c?auto=format&fit=crop&w=1470&q=80');
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
            color: #f0f6f8;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        [data-testid="stSidebar"] {
            background: rgba(20, 40, 50, 0.85) !important;
            border-radius: 0 20px 20px 0;
            font-size: 16px;
            color: #d1d9e6 !important;
        }
        .css-1v3fvcr {margin-bottom: 14px;}
        .css-1a4t5cm {color: #e0e6f2 !important;}
        .css-18e3th9 {
            background-color: rgba(0, 0, 0, 0.6);
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        }
        h1, h2, h3, h4 {
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.15);
        }
        .stDataFrame div[data-testid="stDataFrame"] {
            border-radius: 12px !important;
            box-shadow: 0 4px 8px rgba(255,255,255,0.1);
            background-color: rgba(255, 255, 255, 0.1);
        }
        .stButton > button {
            background-color: #3e6fc1;
            color: white;
            border-radius: 8px;
            border: none;
            box-shadow: 0 2px 6px rgba(62,111,193,0.6);
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #2c4a8f;
            box-shadow: 0 4px 12px rgba(44,74,143,0.8);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

add_cohesive_climate_style()

st.set_page_config(layout="wide", page_title="ClimateScope Prototype")
st.title("🌍 Global Weather Monitor")

DATA_PATH = "data/processed/monthly_agg.parquet"
REQUIRED_COLS = ["country", "year", "month", "temperature_celsius", "precip_mm", "humidity", "wind_mps"]

if not os.path.exists(DATA_PATH):
    st.warning("Run scripts/aggregate_daily_to_monthly.py first to generate data.")
else:
    df = pd.read_parquet(DATA_PATH)
    np.random.seed(42)
    demo_cols = [
        ("pressure_hPa", 980, 1040),
        ("solar_radiation", 80, 390),
        ("cloud_cover", 0, 100),
        ("dew_point", 0, 28),
        ("visibility_km", 1, 20),
        ("heat_index", 15, 55),
        ("snow_mm", 0, 500),
        ("thunderstorm_days", 0, 12),
        ("min_temperature_celsius", -10, 30),
        ("max_temperature_celsius", 10, 48),
    ]
    for col, mn, mx in demo_cols:
        if col not in df.columns:
            df[col] = np.random.uniform(mn, mx, len(df))

    st.markdown(
        "<b>Columns present in DataFrame:</b> "
        + " ".join(
            f'<span style="display:inline-block;background:#3e6fc1;color:white;padding:4px 14px 4px 14px;border-radius:14px;margin:2px 3px;font-size:15px;">{col}</span>'
            for col in df.columns
        ),
        unsafe_allow_html=True,
    )

    missing = [col for col in REQUIRED_COLS if col not in df.columns]
    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

    st.sidebar.header("Filters")
    countries = sorted(df["country"].dropna().unique())
    sel_countries = st.sidebar.multiselect("Countries (compare multiple!)", countries, default=countries[:1])

    additional_vars = [
        "temperature_celsius",
        "min_temperature_celsius",
        "max_temperature_celsius",
        "precip_mm",
        "humidity",
        "wind_mps",
        "pressure_hPa",
        "solar_radiation",
        "cloud_cover",
        "dew_point",
        "visibility_km",
        "heat_index",
        "snow_mm",
        "thunderstorm_days",
    ]
    variable_options = [v for v in additional_vars if v in df.columns]
    variable = st.sidebar.selectbox("Variable", variable_options)

    # --- YEAR RANGE SLIDER ---
    yr_range = st.sidebar.slider("Year range", 2000, 2025, (int(df["year"].min()), int(df["year"].max())))

    # --- BUILD DATE COLUMN ON FULL DF (for filtering) ---
    df["month_num"] = pd.to_datetime(df["month"], errors="coerce").dt.month
    df["date"] = pd.to_datetime(
        df["year"].astype(str) + "-" + df["month_num"].astype(str) + "-01"
    )

    # --- FILTER YEAR RANGE FIRST ---
    filtered = df[(df["year"] >= yr_range[0]) & (df["year"] <= yr_range[1])]
    if sel_countries:
        filtered = filtered[filtered["country"].isin(sel_countries)]

    # --- DATE RANGE SIDEBAR (AFTER YEAR RANGE) ---
    if not filtered.empty:
        min_date = filtered["date"].min()
        max_date = filtered["date"].max()
        range_defaults = [min_date, max_date]
        date_range = st.sidebar.date_input(
            "Date range (calendar)", value=range_defaults, min_value=min_date, max_value=max_date
        )
        # For single date pick (not range) just set both to the same day:
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            filtered = filtered[(filtered["date"] >= pd.to_datetime(date_range[0])) & (filtered["date"] <= pd.to_datetime(date_range[1]))]
        else:  # fallback single date
            filtered = filtered[filtered["date"] == pd.to_datetime(date_range)]

    # --- Drill Down Controls ---
    st.sidebar.markdown("### Drill Down Controls")
    enable_year_drill = st.sidebar.checkbox("Drill down by year")
    if enable_year_drill:
        all_years = sorted(df["year"].unique())
        drill_year = st.sidebar.selectbox("Drill Year", all_years, index=all_years.index(yr_range[1]))
        filtered = filtered[filtered["year"] == drill_year]
    else:
        drill_year = None

    enable_country_drill = st.sidebar.checkbox("Drill down by country")
    if enable_country_drill:
        all_ctrs = sorted(df["country"].dropna().unique())
        drill_country = st.sidebar.selectbox("Drill Country", all_ctrs, index=0)
        filtered = filtered[filtered["country"] == drill_country]
    else:
        drill_country = None

    chart_type = st.sidebar.radio("Trend Chart Type", ["Line", "Bar", "Heatmap"])

    extremes = None
    extremes_table = None
    if os.path.exists("analysis/extremes.csv"):
        ex = pd.read_csv("analysis/extremes.csv")
        extremes = ex
        extremes_table = ex.copy()
        extremes_table = extremes_table[
            (extremes_table["year"] >= yr_range[0]) & (extremes_table["year"] <= yr_range[1])
        ]
        if sel_countries:
            extremes_table = extremes_table[extremes_table["country"].isin(sel_countries)]
        if drill_year is not None:
            extremes_table = extremes_table[extremes_table["year"] == drill_year]
        if drill_country is not None:
            extremes_table = extremes_table[extremes_table["country"] == drill_country]

    st.markdown("## Average Climate Measures by Country")
    st.markdown(
        "This choropleth map visualizes the average value of the selected variable across the chosen countries and time period."
    )
    if not filtered.empty:
        country_avg = filtered.groupby("country")[variable].mean().reset_index()
        fig = px.choropleth(
            country_avg,
            locations="country",
            locationmode="country names",
            color=variable,
            title=f"{variable} Average by Country",
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar=dict(title=variable.replace("_", " ").title()),
            height=600,
            width=1100,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for choropleth.")

    st.markdown("## Climate Trends Over Time")
    st.markdown(
        "Interactive trend charts allow you to compare how the selected variable changes over months and years among selected countries. "
        "Switch between line, bar, and heatmap views."
    )

    if not filtered.empty:
        if chart_type == "Heatmap":
            pivot = filtered.pivot_table(
                index="country", columns="month", values=variable, aggfunc="mean", fill_value=None
            )
            fig2 = px.imshow(
                pivot,
                labels=dict(x="Month", y="Country", color=variable),
                aspect="auto",
                title=f"{variable} Heatmap (Country vs Month)",
                template="plotly_dark",
            )
        else:
            if chart_type == "Line":
                fig2 = px.line(
                    filtered,
                    x="month",
                    y=variable,
                    color="country",
                    title=f"{variable} Trend Comparison ({yr_range[0]}-{yr_range[1]})",
                    template="plotly_dark",
                )
            elif chart_type == "Bar":
                fig2 = px.bar(
                    filtered,
                    x="month",
                    y=variable,
                    color="country",
                    title=f"{variable} Bar Comparison ({yr_range[0]}-{yr_range[1]})",
                    template="plotly_dark",
                )

            if extremes_table is not None and not extremes_table.empty and chart_type in ("Line", "Bar"):
                for country in sel_countries:
                    df_ext = extremes_table[extremes_table["country"] == country]
                    if not df_ext.empty and variable in df_ext.columns:
                        fig2.add_trace(
                            go.Scatter(
                                x=df_ext["month"],
                                y=df_ext[variable],
                                mode="markers",
                                name=f"Extreme ({country})",
                                marker=dict(color="red", size=12, symbol="x"),
                                showlegend=True,
                            )
                        )

        st.plotly_chart(fig2, use_container_width=True)
        buf = io.BytesIO()
        fig2.write_image(buf, format="png")
        st.download_button(label="Download Chart as PNG", data=buf, file_name="chart.png", mime="image/png")
    else:
        st.info("No data for selected chart.")

    # Time series section (with unique key)
    st.markdown("## Interactive Time Series for Selected Variable")
    if not filtered.empty:
        fig_ts = px.line(
            filtered,
            x="date",
            y=variable,
            color="country",
            title=f"Time Series of {variable.replace('_', ' ').title()}",
            template="plotly_dark",
            markers=True,
        )
        st.plotly_chart(fig_ts, use_container_width=True, key="timeseries")

    if not filtered.empty:
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(label="Download Filtered Data as CSV", data=csv, file_name="filtered_data.csv", mime="text/csv")

    st.markdown("## Detected Extreme Weather Events and Outliers")
    st.markdown(
        "The following table displays detected extreme temperature and precipitation events within your current filter settings."
    )
    if extremes_table is not None and not extremes_table.empty:
        st.subheader("Detected Extremes")
        st.dataframe(extremes_table)
    else:
        st.info("No extremes for current selection.")

    st.markdown("## Scatter Plot — Relationship Explorer")
    if filtered.empty:
        st.info("No data available for scatter plot.")
    else:
        var_list = [col for col in variable_options if col in filtered.columns]
        scatter_x = st.sidebar.selectbox("Scatter Plot X-Axis Variable", var_list, index=0)
        scatter_y = st.sidebar.selectbox("Scatter Plot Y-Axis Variable", var_list, index=min(1, len(var_list) - 1))
        scatter_fig = px.scatter(
            filtered,
            x=scatter_x,
            y=scatter_y,
            color="country",
            hover_data=["country", "year", "month"],
            title=f"Scatter Plot: {scatter_y} vs {scatter_x}",
            template="plotly_dark",
        )
        st.plotly_chart(scatter_fig, use_container_width=True)

    with st.sidebar.expander("Help & FAQ", expanded=False):
        st.markdown(
            """
        **How do I filter by country or time period?**  
        Use the checkboxes and sliders in the sidebar to select which countries and years you want displayed.

        **What do the chart types mean?**  
        - **Line**: Shows trends across time for each country.
        - **Bar**: Compares values across countries for each time interval.
        - **Heatmap**: Visualizes average values per country and month.

        **How do I see extreme weather events?**  
        When detected, extremes are highlighted with red '×' points on trend charts. The detected extremes/outliers table lists all such events for your selected filters.

        **Can I download the current chart or filtered data?**  
        Yes! Use the "Download Chart as PNG" or "Download Filtered Data as CSV" buttons below each chart.

        **What does each variable mean?**  
        - `temperature_celsius`: Monthly average temperature (°C)
        - `precip_mm`: Total monthly precipitation (mm)
        - `humidity`: Monthly average relative humidity (%)
        - `wind_mps`: Monthly average wind speed (meters/sec)
        - ...plus any others present in your data!
        
        **No data or empty plots?**  
        Try expanding your time range or selecting more countries; some combinations may have missing data.

        ---

        
        """
        )
