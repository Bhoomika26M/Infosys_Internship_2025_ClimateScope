import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path

# Safety: allow large images if needed (use cautiously)
Image.MAX_IMAGE_PIXELS = None

# --- Page Config ---
st.set_page_config(page_title="🌍 Global Weather Dashboard", layout="wide")

# --- Custom Theme ---
# --- Custom Theme ---
st.markdown("""
    <style>
        /* 🌤 Main App Background */
        .stApp {
            background: linear-gradient(to bottom right, #f0f9ff, #cbebff);
            font-family: 'Segoe UI', sans-serif;
            color: #1a1a1a;
        }

        /* 🧭 Sidebar Styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #74ebd5, #ACB6E5);
            color: white;
        }

        /* 🏷️ Headings */
        h1, h2, h3 {
            color: #003366;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }

        /* 🔘 Button Styling */
        .stButton>button {
            background: linear-gradient(to right, #4facfe, #00f2fe);
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.6em 1.2em;
            font-weight: bold;
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            background: linear-gradient(to right, #43e97b, #38f9d7);
            transform: scale(1.05);
        }

        /* 📊 Metric Cards (used in Weather Overview tab) */

        /* 💠 Metric Cards Styling */
        .metric-card {
            background: #CCF3E1;
            border-radius: 18px;
            padding: 22px;
            text-align: center;
            margin: 12px;
            color: #4B93D2;
            font-family: 'Segoe UI', sans-serif;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-6px);
            box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.25);
        }

        .metric-card h3 {
            font-size: 1.1em;
            margin-bottom: 6px;
            opacity: 0.9;
        }

        .metric-card h2 {
            font-size: 2em;
            font-weight: bold;
        }



        /* 📦 Tabs Styling */
        div[data-baseweb="tab-list"] {
            background-color: #e6f2ff;
            border-radius: 10px;
            padding: 5px;
        }

        button[data-baseweb="tab"] {
            color: #003366;
            font-weight: bold;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(to right, #4facfe, #00f2fe);
            color: white;
            border-radius: 10px;
        }

        /* 🧮 Dataframe Styling */
        .dataframe {
            border-radius: 10px;
            overflow: hidden;
        }

        /* 🔹 Tooltips & Info Boxes */
        .stAlert {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)


# --- Load Data ---
@st.cache_data(show_spinner=True)
def load_data(path):
    df = pd.read_csv(path)
    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
    return df

# ✅ Use relative path
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "Cleaned data set" / "GlobalWeatherRepository_cleaned.csv"

df = load_data(DATA_PATH)
# --- Sidebar Filters (global) ---
st.sidebar.header("🔍 Filter Data")

# Country filter
if "country" in df.columns:
    selected_countries = st.sidebar.multiselect(
        "Select Country/Countries",
        options=sorted(df["country"].dropna().unique()),
        default=None
    )
else:
    selected_countries = []

# Date Range Filter
if "last_updated" in df.columns:
    min_date = df["last_updated"].min().date()
    max_date = df["last_updated"].max().date()
    st.sidebar.info(f"📅 Available Data Range: **{min_date} → {max_date}**")

    start_date, end_date = st.sidebar.date_input(
        "Select Date Range:",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    # validate range
    if start_date < min_date or end_date > max_date:
        st.sidebar.error("⚠️ Selected date range is out of dataset bounds.")
    else:
        df = df[
            (df["last_updated"].dt.date >= start_date) &
            (df["last_updated"].dt.date <= end_date)
        ]

# Apply countries filter
if selected_countries:
    if "country" in df.columns:
        df = df[df["country"].isin(selected_countries)]

# --- Navigation Tabs ---
tab0,tab1, tab2, tab3, tab4 = st.tabs([
    "🌤Weather Overview",
    "📈 Weather Analysis",
    "🗺 Visualizations",
    "📊 Trends & Regional Comparison",
    "✈️ Travel Planner"
])
with tab0:
    st.title("🔥Weather Overview Dashboard")

    if df.empty:
        st.warning("⚠️ No data available for selected filters.")
    else:
        # Compute key metrics
        avg_temp = df["temperature_celsius"].mean() if "temperature_celsius" in df.columns else np.nan
        avg_humidity = df["humidity"].mean() if "humidity" in df.columns else np.nan
        avg_uv = df["uv_index"].mean() if "uv_index" in df.columns else np.nan
        avg_wind = df["wind_kph"].mean() if "wind_kph" in df.columns else np.nan
        avg_pressure = df["pressure_mb"].mean() if "pressure_mb" in df.columns else np.nan

        # Display cards in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>🌡 Temperature (°C)</h3>
                <h2>{avg_temp:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>💧 Humidity (%)</h3>
                <h2>{avg_humidity:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>☀️ UV Index</h3>
                <h2>{avg_uv:.0f}</h2>
            </div>
            """, unsafe_allow_html=True)

        col4, col5 = st.columns(2)
        with col4:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>🌬 Wind Speed (kph)</h3>
                <h2>{avg_wind:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col5:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>⚙️ Pressure (mb)</h3>
                <h2>{avg_pressure:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)

# =============================
# 📈 TAB 1: Weather Analysis
# =============================
with tab1:
    st.title("📊 Weather Analysis with Statistical Insights")

    if df.empty:
        st.warning("⚠️ No data available for the selected filters.")
    else:
        # Numeric columns
        numeric_data = df.select_dtypes(include=np.number)
        numeric_cols = numeric_data.columns.tolist()

        # Descriptive summary
        st.subheader("📈 Descriptive Statistics")
        desc = numeric_data.describe().T
        st.dataframe(desc)

        # Advanced statistics (variance, skewness, kurtosis, range added)
        st.subheader("📊 Advanced Statistics")
        adv = {}
        for c in numeric_cols:
            s = numeric_data[c].dropna()
            adv[c] = {
                "mean": s.mean(),
                "median": s.median(),
                "std": s.std(),
                "var": s.var(),
                "skew": s.skew(),
                "kurtosis": s.kurtosis(),
                "min": s.min() if not s.empty else np.nan,
                "max": s.max() if not s.empty else np.nan,
                "range": (s.max() - s.min()) if not s.empty else np.nan
            }
        adv_df = pd.DataFrame(adv).T
        st.dataframe(adv_df)

        # Interactive highlighting for both tables
        st.markdown("---")
        st.subheader("✨ Interactive Highlighting for Statistics")
        if not numeric_cols:
            st.info("No numeric columns available for highlighting.")
        else:
            highlight_vars = st.multiselect("Select variable(s) to highlight:", numeric_cols)
            highlight_stats_options = ["Maximum", "Minimum", "Above Average", "Below Average", "Std Dev High"]
            highlight_choice = st.selectbox("Highlight Type:", highlight_stats_options)
            highlight_color = st.color_picker("Choose highlight color:", "#fffa65")

            if highlight_vars:
                # Style descriptive (desc) table
                def style_desc_row(row):
                    styles = []
                    var = row.name
                    for stat in row.index:
                        styles.append("")  # default no style
                    # If chosen var, apply rule
                    if var in highlight_vars:
                        if highlight_choice == "Maximum":
                            # highlight max cell in desc -> stat 'max'
                            styles = [""] * len(row.index)
                            if "max" in row.index:
                                idx = list(row.index).index("max")
                                styles[idx] = f"background-color: {highlight_color}"
                        elif highlight_choice == "Minimum":
                            styles = [""] * len(row.index)
                            if "min" in row.index:
                                idx = list(row.index).index("min")
                                styles[idx] = f"background-color: {highlight_color}"
                        elif highlight_choice == "Above Average":
                            # highlight mean if above mean-of-selected-vars
                            mean_of_means = desc.loc[highlight_vars, "mean"].mean()
                            if row["mean"] > mean_of_means:
                                styles = [""] * len(row.index)
                                if "mean" in row.index:
                                    idx = list(row.index).index("mean")
                                    styles[idx] = f"background-color: {highlight_color}"
                        elif highlight_choice == "Below Average":
                            mean_of_means = desc.loc[highlight_vars, "mean"].mean()
                            if row["mean"] < mean_of_means:
                                styles = [""] * len(row.index)
                                if "mean" in row.index:
                                    idx = list(row.index).index("mean")
                                    styles[idx] = f"background-color: {highlight_color}"
                        elif highlight_choice == "Std Dev High":
                            std_of_stds = desc.loc[highlight_vars, "std"].mean()
                            if row["std"] > std_of_stds:
                                styles = [""] * len(row.index)
                                if "std" in row.index:
                                    idx = list(row.index).index("std")
                                    styles[idx] = f"background-color: {highlight_color}"
                    return styles

                st.markdown("**Descriptive Stats (highlighted)**")
                st.dataframe(desc.style.apply(style_desc_row, axis=1), use_container_width=True)

                # Style advanced table
                def style_adv_row(row):
                    styles = [""] * len(row.index)
                    var = row.name
                    if var in highlight_vars:
                        if highlight_choice == "Maximum":
                            if "max" in row.index:
                                i = list(row.index).index("max")
                                styles[i] = f"background-color: {highlight_color}"
                        elif highlight_choice == "Minimum":
                            if "min" in row.index:
                                i = list(row.index).index("min")
                                styles[i] = f"background-color: {highlight_color}"
                        elif highlight_choice == "Above Average":
                            mean_of_means = adv_df.loc[highlight_vars, "mean"].mean()
                            if row["mean"] > mean_of_means:
                                if "mean" in row.index:
                                    i = list(row.index).index("mean")
                                    styles[i] = f"background-color: {highlight_color}"
                        elif highlight_choice == "Below Average":
                            mean_of_means = adv_df.loc[highlight_vars, "mean"].mean()
                            if row["mean"] < mean_of_means:
                                if "mean" in row.index:
                                    i = list(row.index).index("mean")
                                    styles[i] = f"background-color: {highlight_color}"
                        elif highlight_choice == "Std Dev High":
                            std_of_stds = adv_df.loc[highlight_vars, "std"].mean()
                            if row["std"] > std_of_stds:
                                if "std" in row.index:
                                    i = list(row.index).index("std")
                                    styles[i] = f"background-color: {highlight_color}"
                    return styles

                st.markdown("**Advanced Stats (highlighted)**")
                st.dataframe(adv_df.style.apply(style_adv_row, axis=1).format(precision=3), use_container_width=True)
            else:
                st.info("Pick variable(s) above to enable highlighting.")

        # Distribution Analysis - improved labels and parameters
        st.markdown("---")
        st.subheader("📉 Distribution Analysis (Enhanced)")
        if numeric_cols:
            dist_var = st.selectbox("Select variable for distribution:", numeric_cols, index=0)
            bins = st.slider("Number of bins (histogram):", 10, 100, 30)
            kde_toggle = st.checkbox("Show KDE (smoothed density)", value=True)
            color_choice = st.color_picker("Pick a color for plots:", "#1f77b4")

            col1, col2 = st.columns(2)
            with col1:
                fig = px.histogram(df, x=dist_var, nbins=bins, title=f"Histogram of {dist_var}", color_discrete_sequence=[color_choice])
                if not kde_toggle:
                    fig.update_traces(histnorm=None)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.box(df, y=dist_var, title=f"Box plot of {dist_var}", color_discrete_sequence=[color_choice])
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No numeric columns available for distribution analysis.")

# =============================
# 🗺 TAB 2: Visualizations
# =============================
with tab2:
    st.title("🌦 Enhanced Visualizations")

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    plot_type = st.selectbox(
        "Choose Visualization Type",
        ["Line Chart", "Scatter Plot", "Choropleth Map", "Heatmap", "Bubble Chart", "Histogram Grid", "Box Comparison"]
    )

    if plot_type == "Line Chart":
        if "last_updated" in df.columns:
            y_cols = st.multiselect("Select Variables to Plot", numeric_cols, default=[c for c in ["temperature_celsius", "humidity"] if c in numeric_cols])
            if y_cols:
                fig = px.line(df, x="last_updated", y=y_cols, color="country" if "country" in df.columns else None, title="Weather Variables Over Time")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Select at least one numeric variable.")
        else:
            st.warning("last_updated column required for line chart.")

    elif plot_type == "Scatter Plot":
        if numeric_cols:
            x_col = st.selectbox("X-axis", numeric_cols)
            y_col = st.selectbox("Y-axis", numeric_cols)
            size_col = None
            if "wind_kph" in numeric_cols:
                size_col = st.selectbox("Size (optional):", ["None"] + numeric_cols, index=0)
                if size_col == "None":
                    size_col = None
            fig = px.scatter(df, x=x_col, y=y_col, color="country" if "country" in df.columns else None, size=size_col, title=f"{y_col} vs {x_col}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numeric columns to plot.")

    elif plot_type == "Choropleth Map":
        if "country" in df.columns and numeric_cols:
            y_col = st.selectbox("Select Metric", numeric_cols)
            fig = px.choropleth(df, locations="country", locationmode="country names", color=y_col, title=f"World Map of {y_col}", color_continuous_scale="Viridis")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Need country and a numeric metric for choropleth.")

    elif plot_type == "Heatmap":
        # limit to key variables to avoid huge images
        key_vars = ["temperature_celsius", "humidity", "wind_kph", "pressure_mb", "visibility_km", "precip_mm"]
        present = [c for c in key_vars if c in numeric_cols]
        if len(present) < 2:
            st.warning("Not enough key numeric variables available for heatmap.")
        else:
            fig, ax = plt.subplots(figsize=(8, 5), dpi=80)
            sns.heatmap(df[present].corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
            st.pyplot(fig)

    elif plot_type == "Bubble Chart":
        if {"temperature_celsius", "humidity", "wind_kph"}.issubset(df.columns):
            fig = px.scatter(df, x="temperature_celsius", y="humidity", size="wind_kph", color="country" if "country" in df.columns else None, title="Temperature vs Humidity (bubble=wind)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Required columns missing for bubble chart.")

    elif plot_type == "Histogram Grid":
        numeric_data = df.select_dtypes(include=np.number)
        sampled = numeric_data.sample(min(500, len(numeric_data))) if len(numeric_data) > 500 else numeric_data
        selected_vars = st.multiselect("Select Variables for Pairplot", sampled.columns.tolist(), default=sampled.columns[:4].tolist() if len(sampled.columns) >= 4 else sampled.columns.tolist())
        if len(selected_vars) > 1:
            fig = sns.pairplot(sampled[selected_vars], corner=True)
            st.pyplot(fig)
        else:
            st.info("Choose 2 or more variables to show pairplot.")

    elif plot_type == "Box Comparison":
        if "country" in df.columns and numeric_cols:
            var = st.selectbox("Select Variable for Box Comparison", numeric_cols)
            fig = px.box(df, x="country", y=var, color="country", title=f"{var} Distribution by Country")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Need country and numeric variable for box comparison.")

# =============================
# 📊 TAB 3: Trends & Regional Comparison (with Extreme sections)
# =============================
with tab3:
    st.title("📊 Trends & Regional Comparison")

    if df.empty:
        st.warning("No data available for selected filters.")
    else:
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        # Trend variables selectable
        st.subheader("📉 Trend Analysis (Custom Variables)")
        trend_vars = st.multiselect("Select variables to show over time:", numeric_cols, default=[v for v in ["temperature_celsius", "humidity"] if v in numeric_cols])
        if trend_vars and "last_updated" in df.columns:
            fig_trend = px.line(df, x="last_updated", y=trend_vars, color="country" if "country" in df.columns else None, title="Customizable Weather Trends")
            st.plotly_chart(fig_trend, use_container_width=True)
        elif not trend_vars:
            st.info("Select at least one variable for trends.")
        else:
            st.warning("last_updated column required for trend plots.")

        # Regional comparison
        st.subheader("🌍 Regional Comparison")
        if numeric_cols:
            metric = st.selectbox("Select Metric for Regional Comparison", numeric_cols, index=0)
            region_agg = st.radio("Aggregation:", ["Average", "Maximum", "Minimum"], horizontal=True)
            if region_agg == "Average":
                comp = df.groupby("country")[metric].mean().reset_index()
            elif region_agg == "Maximum":
                comp = df.groupby("country")[metric].max().reset_index()
            else:
                comp = df.groupby("country")[metric].min().reset_index()
            fig_comp = px.bar(comp.sort_values(by=metric, ascending=False), x="country", y=metric, color=metric, title=f"{region_agg} {metric} by Country", text_auto=True)
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("No numeric columns available for regional comparison.")

        # ---------- EXTREME SECTIONS (ONLY IN THIS TAB) ----------
        st.markdown("---")
        st.subheader("🔥 Extreme Temperature & Wind Events (Interactive)")

        # Temperature extremes
        if "temperature_celsius" in df.columns:
            st.markdown("**Extreme Temperature Events**")
            temp_thresh = st.slider("Set extreme temperature threshold (°C):", int(np.floor(df["temperature_celsius"].min())) if not df["temperature_celsius"].isna().all() else -50,
                                     int(np.ceil(df["temperature_celsius"].max())) if not df["temperature_celsius"].isna().all() else 90,
                                     value=int(np.ceil(df["temperature_celsius"].max())) if not df["temperature_celsius"].isna().all() else 30)
            extreme_temp_df = df[df["temperature_celsius"] >= temp_thresh].sort_values("temperature_celsius", ascending=False)
            st.info(f"Found {len(extreme_temp_df)} events with temperature ≥ {temp_thresh}°C.")
            if not extreme_temp_df.empty:
                # Show top 10 in table
                st.dataframe(extreme_temp_df.head(20)[["country", "last_updated", "temperature_celsius", "humidity"]].reset_index(drop=True))
                # Plot interactive bar (top 20)
                top_plot = extreme_temp_df.head(20).copy()
                if "country" in top_plot.columns:
                    fig_et = px.bar(top_plot, x="country", y="temperature_celsius", hover_data=["last_updated", "humidity"],
                                    title=f"Top {min(20, len(top_plot))} Extreme Temperature Events (≥ {temp_thresh}°C)")
                else:
                    fig_et = px.bar(top_plot.reset_index().rename(columns={"index": "row"}), x="row", y="temperature_celsius",
                                    title=f"Top {min(20, len(top_plot))} Extreme Temperature Events (≥ {temp_thresh}°C)")
                st.plotly_chart(fig_et, use_container_width=True)
            else:
                st.info("No events meet the temperature threshold.")

        else:
            st.info("temperature_celsius column not available for extreme temperature analysis.")

        st.markdown("---")

        # Wind extremes
        if "wind_kph" in df.columns:
            st.markdown("**Extreme Wind Events**")
            wind_min = int(np.floor(df["wind_kph"].min())) if not df["wind_kph"].isna().all() else 0
            wind_max = int(np.ceil(df["wind_kph"].max())) if not df["wind_kph"].isna().all() else 200
            wind_thresh = st.slider("Set extreme wind threshold (kph):", wind_min, wind_max, value=min(120, wind_max))
            extreme_wind_df = df[df["wind_kph"] >= wind_thresh].sort_values("wind_kph", ascending=False)
            st.info(f"Found {len(extreme_wind_df)} events with wind_kph ≥ {wind_thresh} kph.")
            if not extreme_wind_df.empty:
                st.dataframe(extreme_wind_df.head(20)[["country", "last_updated", "wind_kph", "temperature_celsius"]].reset_index(drop=True))
                topw = extreme_wind_df.head(20).copy()
                if "country" in topw.columns:
                    fig_w = px.bar(topw, x="country", y="wind_kph", hover_data=["last_updated", "temperature_celsius"],
                                   title=f"Top {min(20, len(topw))} Extreme Wind Events (≥ {wind_thresh} kph)")
                else:
                    fig_w = px.bar(topw.reset_index().rename(columns={"index": "row"}), x="row", y="wind_kph",
                                   title=f"Top {min(20, len(topw))} Extreme Wind Events (≥ {wind_thresh} kph)")
                st.plotly_chart(fig_w, use_container_width=True)
            else:
                st.info("No events meet the wind threshold.")
        else:
            st.info("wind_kph column not available for extreme wind analysis.")

# ====================================================
# ✈️ TAB 4: Travel Planner (with Benchmarks)
# ====================================================
with tab4:
    # 🌍✈️ Travel Planner – Ideal Travel Suitability
    st.title("✈️ Travel Planner – Ideal Travel Suitability")

    if "country" not in df.columns:
        st.warning("Country data not available.")
        st.stop()

    selected_country = st.selectbox("🌍 Select a Country", sorted(df["country"].dropna().unique()))
    country_df = df[df["country"] == selected_country].copy()

# 🗓 Ensure month column exists
    if "last_updated" in df.columns and "month" not in df.columns:
        df["month"] = df["last_updated"].dt.month

    if not country_df.empty and {"temperature_celsius", "humidity"}.issubset(country_df.columns):
    # ✅ Benchmarks for comparison
        benchmark_temp = country_df["temperature_celsius"].min()
        benchmark_humidity = country_df["humidity"].min()

        st.info(f"🌡 Benchmark Minimum Temperature: **{benchmark_temp:.2f}°C**")
        st.info(f"💧 Benchmark Minimum Humidity: **{benchmark_humidity:.2f}%**")

        mode = st.radio("Choose Mode", ["By Season", "By Month"], horizontal=True)

    # 🌤 Define season-to-month and comfort ranges
        season_months = {
            "Winter": [12, 1, 2],
            "Summer": [5, 6, 7, 8],
            "Monsoon": [7, 8, 9],
            "Spring": [3, 4],
            "Autumn": [9, 10, 11]
        }

        season_conditions = {
        "Winter": {"temp_min": 10, "temp_max": 25, "hum_min": 20, "hum_max": 70},
        "Summer": {"temp_min": 20, "temp_max": 35, "hum_min": 30, "hum_max": 65},
        "Monsoon": {"temp_min": 18, "temp_max": 30, "hum_min": 70, "hum_max": 90},
        "Spring": {"temp_min": 15, "temp_max": 28, "hum_min": 40, "hum_max": 70},
        "Autumn": {"temp_min": 10, "temp_max": 25, "hum_min": 40, "hum_max": 75},
        }

        if mode == "By Season":
            season = st.selectbox("Select a Season", list(season_months.keys()))
            cond = season_conditions[season]
            months = season_months[season]

        # Filter by season months
            season_df = country_df[country_df["last_updated"].dt.month.isin(months)]

            if not season_df.empty:
                avg_temp = season_df["temperature_celsius"].mean()
                avg_humidity = season_df["humidity"].mean()

                st.write(f"🌡 Average Temperature ({season}): **{avg_temp:.2f}°C**")
                st.write(f"💧 Average Humidity ({season}): **{avg_humidity:.2f}%**")

            # ✅ Slightly relaxed condition to be realistic
                if (
                    cond["temp_min"] - 3 <= avg_temp <= cond["temp_max"] + 3
                    and cond["hum_min"] - 5 <= avg_humidity <= cond["hum_max"] + 5
                ):
                    st.success(f"✅ {selected_country} is suitable for travel during {season}.")
                else:
                    st.error(f"❌ {selected_country} is not suitable for travel during {season}.")
            else:
                st.warning("No data available for this season.")

        elif mode == "By Month":
            month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            selected_month = st.selectbox("Select a Month", month_names)
            month_num = month_names.index(selected_month) + 1
            month_df = country_df[country_df["last_updated"].dt.month == month_num]

        # 🔗 Link month to season
            related_season = None
            for s, months in season_months.items():
                if month_num in months:
                    related_season = s
                    break

            cond = season_conditions[related_season] if related_season else {"temp_min": 15, "temp_max": 30, "hum_min": 40, "hum_max": 75}

            if not month_df.empty:
                avg_temp = month_df["temperature_celsius"].mean()
                avg_humidity = month_df["humidity"].mean()

                st.write(f"🌡 Average Temperature in {selected_month}: **{avg_temp:.2f}°C**")
                st.write(f"💧 Average Humidity in {selected_month}: **{avg_humidity:.2f}%**")

            # ✅ Compare with related season comfort and relaxed margins
                if (
                    cond["temp_min"] - 3 <= avg_temp <= cond["temp_max"] + 3
                    and cond["hum_min"] - 5 <= avg_humidity <= cond["hum_max"] + 5
                ):
                    st.success(f"✅ {selected_country} is suitable for travel in {selected_month} ({related_season}).")
                else:
                    st.error(f"❌ {selected_country} is not suitable for travel in {selected_month} ({related_season}).")
            else:
                st.warning("No data found for this country in the selected month.")

# End of dashboard             