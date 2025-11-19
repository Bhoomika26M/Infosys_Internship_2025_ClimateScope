import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io, tempfile

# Optional PDF/chart export libs (handled gracefully)
try:
    import kaleido  # noqa: F401
    HAS_KALEIDO = True
except Exception:
    HAS_KALEIDO = False

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    HAS_REPORTLAB = True
except Exception:
    HAS_REPORTLAB = False

# -----------------------
# Page config + theme
# -----------------------
st.set_page_config(page_title="ClimateScope Dashboard", layout="wide")
px.defaults.template = "plotly_dark"

# -----------------------
# Styling (keeps your theme)
# -----------------------
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid #1E293B; padding-top: 0 !important; }
        .dashboard-title { text-align:center; font-size:36px; font-weight:700; color:#60A5FA; margin-top:-40px; margin-bottom:-10px; }
        .dashboard-subtitle { text-align:center; font-size:18px; color:#CBD5E1; margin-top:5px; margin-bottom:25px; }
        .metric-container { background: rgba(37,99,235,0.12); border: 1px solid rgba(37,99,235,0.25); border-radius: 15px; padding: 14px; margin: 6px; text-align:center; box-shadow: 0 0 10px rgba(59,130,246,0.15); }
        .metric-container h3 { font-size:14px; color:#93C5FD; margin-bottom:6px; }
        .metric-container p { font-size:20px; color:#E2E8F0; margin:0; font-weight:600; }
        footer { text-align:center; color:#94A3B8; padding:10px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# Data loading (cached)
# -----------------------
@st.cache_data
def load_data():
    daily = pd.read_csv("daily_cleaned.csv")
    monthly = pd.read_csv("weather_data_monthly.csv")
    seasonal = pd.read_csv("weather_seasonal_avg.csv")
    yearly = pd.read_csv("weather_yearly_avg.csv")

    # normalize/parse dates
    if "last_updated" in daily.columns:
        daily['date'] = pd.to_datetime(daily['last_updated'], dayfirst=True, errors='coerce')
    elif "date" in daily.columns:
        daily['date'] = pd.to_datetime(daily['date'], errors='coerce')

    # monthly year_month kept as-is (string). We'll parse where needed later.
    if "year_month" in monthly.columns:
        monthly['year_month'] = monthly['year_month'].astype(str)

    # create daily year_month if possible
    if "date" in daily.columns and pd.api.types.is_datetime64_any_dtype(daily['date']):
        daily['year_month'] = daily['date'].dt.strftime("%Y-%m")

    # ensure yearly numeric year
    if "year" in yearly.columns:
        yearly['year'] = pd.to_numeric(yearly['year'], errors='coerce')

    return daily, monthly, seasonal, yearly

daily_df, monthly_df, seasonal_df, yearly_df = load_data()

# build a composite air quality in yearly if not present (safe)
aq_cols = [c for c in yearly_df.columns if "air_quality_" in c and c not in ("air_quality_us-epa-index","air_quality_gb-defra-index")]
if len(aq_cols) >= 1 and "air_quality_score" not in yearly_df.columns:
    yearly_df["air_quality_score"] = yearly_df[aq_cols].mean(axis=1)

# -----------------------
# Small helpers
# -----------------------
def normalize_series_minmax(s):
    """Return min-max normalized series (0..1) safely."""
    if s.isnull().all():
        return s
    mn, mx = s.min(), s.max()
    if mn == mx:
        return s.fillna(0.0) - mn + 0.0
    return (s - mn) / (mx - mn)

def compute_trend_simple(curr, prev):
    """Return arrow and pct change; safe for NaNs and zero previous."""
    if pd.isna(curr) or pd.isna(prev) or prev == 0:
        return "", 0.0
    pct = ((curr - prev) / abs(prev)) * 100
    arrow = "↑" if pct > 0 else "↓" if pct < 0 else ""
    return arrow, round(pct, 2)

# -----------------------
# Sidebar: navigation + filters (unchanged design)
# -----------------------
with st.sidebar:
    st.markdown("<div style='margin-top:-25px;' class='sidebar-title'><span>🌍</span>ClimateScope</div><hr class='sidebar-divider'>", unsafe_allow_html=True)
    page = st.radio("Dashboard Sections", ["Home Overview", "Monthly Trends", "Yearly Analysis", "Extreme Events", "Seasonal Patterns", "Download Reports"])
    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    # Country selector (master filter)
    countries = sorted(yearly_df["country"].dropna().unique().tolist())
    selected_countries = st.multiselect("Select Countries", countries, default=countries[:3], key="country_multi")

    # Date range selector (global) - used for daily-level pages (Home Overview if custom range, and Extreme Events)
    st.markdown("---")
    if 'date' in daily_df.columns:
        daily_df['date'] = pd.to_datetime(daily_df['date'], errors='coerce')
        min_date = daily_df['date'].min()
        max_date = daily_df['date'].max()
        if pd.notnull(min_date) and pd.notnull(max_date):
            date_range = st.date_input(                
                "📅 Select Date Range (applies to Home & Extreme Events):",
                [min_date.date(), max_date.date()],
                min_value=min_date.date(),
                max_value=max_date.date(),
            )
        else:
            date_range = [None, None]
    else:
        date_range = [None, None]

# -----------------------
# Apply country filters across dataframes
# -----------------------
if selected_countries:
    daily_filtered = daily_df[daily_df["country"].isin(selected_countries)].copy()
    monthly_filtered = monthly_df[monthly_df["country"].isin(selected_countries)].copy()
    seasonal_filtered = seasonal_df[seasonal_df["country"].isin(selected_countries)].copy()
    yearly_filtered = yearly_df[yearly_df["country"].isin(selected_countries)].copy()
else:
    daily_filtered = daily_df.copy()
    monthly_filtered = monthly_df.copy()
    seasonal_filtered = seasonal_df.copy()
    yearly_filtered = yearly_df.copy()

# Header
st.markdown("<div class='dashboard-title'>ClimateScope Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='dashboard-subtitle'>Advanced Climate & Air Quality Analytics</div>", unsafe_allow_html=True)

# -----------------------
# Helper: decide whether user chose a custom date range
# -----------------------
def user_selected_custom_range(date_range, full_df):
    """Return True if user changed date_range away from full extent (or if range narrower)."""
    if date_range is None or date_range == [None, None]:
        return False
    # If full_df has no dates -> False
    if 'date' not in full_df.columns:
        return False
    min_all = full_df['date'].min().date()
    max_all = full_df['date'].max().date()
    try:
        start = pd.to_datetime(date_range[0]).date()
        end = pd.to_datetime(date_range[1]).date()
        # If selected equals full extents -> treat as default (not custom)
        if start == min_all and end == max_all:
            return False
        return True
    except Exception:
        return False

# -----------------------
# HOME OVERVIEW
# -----------------------
if page == "Home Overview":
    st.markdown("####  Global Climate Overview")

    # Choose source df for Home Overview KPIs & visuals:
    # - If user selected custom date-range in sidebar -> apply that to daily_filtered
    # - Else keep default KPI behavior: latest year (to match previous behavior)
    apply_custom = user_selected_custom_range(date_range, daily_df)

    # Dynamic AQI detection
    aqi_col = None
    for col in ["air_quality_score", "air_quality_PM2.5", "AirQualityIndex"]:
        if col in daily_filtered.columns:
            aqi_col = col
            break
    if aqi_col is None:
        daily_filtered["air_quality_score"] = np.nan
        aqi_col = "air_quality_score"

    # Dataframes used for charts (global scope)
    if apply_custom:
        # filter by date_range specified in sidebar
        start_dt = pd.to_datetime(date_range[0])
        end_dt = pd.to_datetime(date_range[1])
        home_df = daily_filtered[(daily_filtered["date"] >= start_dt) & (daily_filtered["date"] <= end_dt)].copy()
        # For trend charts that require year aggregation, fall back to available years in the selected range
        latest_year_label = None
    else:
        # default: compute KPIs for latest year (same as prior behavior)
        if "year" not in daily_filtered.columns:
            st.warning("Year column missing in data — Home Overview can't compute year-based KPIs.")
            home_df = daily_filtered.copy()
            latest_year_label = None
        else:
            latest_year = int(daily_filtered["year"].max())
            prev_year = latest_year - 1
            home_df = daily_filtered[daily_filtered["year"] == latest_year].copy()
            latest_year_label = latest_year

    # Compute KPIs using home_df (either custom date range or latest year)
    avg_temp = home_df["temperature_celsius"].mean(skipna=True)
    avg_wind = home_df["wind_kph"].mean(skipna=True)
    avg_aqi = home_df[aqi_col].mean(skipna=True)

    # Prev-year comparisons: only meaningful when default/latest-year mode
    if not apply_custom and latest_year_label is not None:
        prev_df_for_comp = daily_filtered[daily_filtered["year"] == (latest_year_label - 1)]
        p_temp = prev_df_for_comp["temperature_celsius"].mean(skipna=True)
        p_wind = prev_df_for_comp["wind_kph"].mean(skipna=True)
        p_aqi = prev_df_for_comp[aqi_col].mean(skipna=True)
    else:
        p_temp = p_wind = p_aqi = np.nan

    # trend arrows & pct
    a_temp, p_temp_pct = compute_trend_simple(avg_temp, p_temp)
    a_wind, p_wind_pct = compute_trend_simple(avg_wind, p_wind)
    a_aqi, p_aqi_pct = compute_trend_simple(avg_aqi, p_aqi)

    # Climate Index: a normalized composite using min-max (0..100)
    if {"temperature_celsius", "wind_kph", aqi_col}.issubset(home_df.columns):
        ci_df = home_df.dropna(subset=["temperature_celsius", "wind_kph", aqi_col])
        if not ci_df.empty:
            t_norm = normalize_series_minmax(ci_df["temperature_celsius"])
            w_norm = normalize_series_minmax(ci_df["wind_kph"])
            a_norm = normalize_series_minmax(ci_df[aqi_col])
            # Weighted index: note AQ worse when higher -> invert (1 - a_norm)
            climate_index = ((t_norm * 0.3) + ((1 - a_norm) * 0.4) + (w_norm * 0.3)).mean() * 100
        else:
            climate_index = np.nan
    else:
        climate_index = np.nan

    # Display KPIs (keep exact same design)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if pd.notna(avg_temp):
            if not apply_custom and latest_year_label is not None:
                st.markdown(f"<div class='metric-container'><h3>Avg Temp (°C)</h3><p>{avg_temp:.2f} {a_temp}</p><small style='color:#93C5FD'>{p_temp_pct:+.2f}% vs {latest_year_label-1}</small></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='metric-container'><h3>Avg Temp (°C)</h3><p>{avg_temp:.2f} {a_temp}</p></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='metric-container'><h3>Avg Temp (°C)</h3><p>—</p></div>", unsafe_allow_html=True)

    with c2:
        if pd.notna(avg_wind):
            if not apply_custom and latest_year_label is not None:
                st.markdown(f"<div class='metric-container'><h3>Avg Wind (kph)</h3><p>{avg_wind:.2f} {a_wind}</p><small style='color:#93C5FD'>{p_wind_pct:+.2f}% vs {latest_year_label-1}</small></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='metric-container'><h3>Avg Wind (kph)</h3><p>{avg_wind:.2f} {a_wind}</p></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='metric-container'><h3>Avg Wind (kph)</h3><p>—</p></div>", unsafe_allow_html=True)

    with c3:
        if pd.notna(avg_aqi):
            if not apply_custom and latest_year_label is not None:
                st.markdown(f"<div class='metric-container'><h3>Air Quality</h3><p>{avg_aqi:.2f} {a_aqi}</p><small style='color:#93C5FD'>{p_aqi_pct:+.2f}% vs {latest_year_label-1}</small></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='metric-container'><h3>Air Quality</h3><p>{avg_aqi:.2f} {a_aqi}</p></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='metric-container'><h3>Air Quality</h3><p>—</p></div>", unsafe_allow_html=True)

    with c4:
        st.markdown(f"<div class='metric-container'><h3>Climate Index</h3><p>{climate_index:.2f}</p><small style='color:#93C5FD'>climate score (0–100)</small></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Visualizations: use the same data frame used for KPIs (home_df or filtered)
    r1c1, r1c2 = st.columns(2)
    r2c1, r2c2 = st.columns(2)

    # Choropleth — aggregated appropriately
    with r1c1:
        try:
            map_df = home_df.groupby("country", as_index=False).mean(numeric_only=True)
            map_df = map_df.dropna(subset=["country", "temperature_celsius"])
            title_map = "Global Temperature Distribution"
            if not apply_custom and latest_year_label is not None:
                title_map = f"Global Temperature Distribution ({latest_year_label})"
            fig_map = px.choropleth(
                map_df,
                locations="country",
                locationmode="country names",
                color="temperature_celsius",
                color_continuous_scale="thermal",
                title=title_map,
            )
            fig_map.update_layout(paper_bgcolor="#0E1117", plot_bgcolor="#0E1117")
            st.plotly_chart(fig_map, use_container_width=True)
            st.session_state.setdefault("home_figures", {})["map"] = fig_map

        except Exception as e:
            st.info(f"Map unavailable: {e}")

    # Temperature trend — uses global yearly aggregation (not impacted by custom date-range)
    with r1c2:
        try:
            df_temp = daily_filtered.groupby("year")["temperature_celsius"].mean().reset_index().sort_values("year")
            df_temp["rolling3"] = df_temp["temperature_celsius"].rolling(3, min_periods=1).mean()
            fig_temp = px.line(df_temp, x="year", y=["temperature_celsius", "rolling3"],
                               labels={"value": "Temp (°C)"},
                               title="Global Temperature Trend (3-Year Rolling)")
            fig_temp.update_layout(paper_bgcolor="#0E1117", plot_bgcolor="#0E1117")
            st.plotly_chart(fig_temp, use_container_width=True)
            st.session_state.setdefault("home_figures", {})["temp_trend"] = fig_temp

        except Exception as e:
            st.info(f"Temperature trend unavailable: {e}")

    # Air quality trend
    with r2c1:
        try:
            aq_df = daily_filtered.groupby("year")[aqi_col].mean().reset_index().sort_values("year")
            aq_df["rolling3"] = aq_df[aqi_col].rolling(3, min_periods=1).mean()
            fig_aq = px.line(aq_df, x="year", y=[aqi_col, "rolling3"], title="🌫️ Global Air Quality Trend (3-Year Rolling Average)")
            fig_aq.update_layout(legend_title_text="", paper_bgcolor="#0E1117", plot_bgcolor="#0E1117")
            st.plotly_chart(fig_aq, use_container_width=True)
            st.session_state.setdefault("home_figures", {})["aq_trend"] = fig_aq


        except Exception as e:
            st.info(f"Air Quality trend unavailable: {e}")

    # Scatter: temperature vs AQI (country averages)
    with r2c2:
        try:
            numeric_cols = daily_filtered.select_dtypes(include=['number']).columns
            country_avg = daily_filtered.groupby("country")[numeric_cols].mean().reset_index()
            if aqi_col in country_avg.columns:
                fig_sc = px.scatter(country_avg, x="temperature_celsius", y=aqi_col, size="wind_kph",
                                    hover_name="country", title="Temperature vs Air Quality (size = wind)")
                fig_sc.update_layout(paper_bgcolor="#0E1117", plot_bgcolor="#0E1117")
                st.plotly_chart(fig_sc, use_container_width=True)
                st.session_state.setdefault("home_figures", {})["scatter"] = fig_sc

            else:
                st.info("Air Quality column missing for scatter.")
        except Exception as e:
            st.info(f"Scatter plot unavailable: {e}")

    # Save summary for PDF (session_state) — compute summary lines based on the current home_df (so PDF reflects selection)
    home_summary_lines = [
        "🏠 Home Overview Summary",
        f"- Data scope: {'Custom date range' if apply_custom else f'Latest year ({latest_year_label})' if latest_year_label else 'Full dataset'}",
        f"- Avg Temperature: {avg_temp:.2f}°C" if pd.notna(avg_temp) else "- Avg Temperature: —",
        f"- Avg Wind: {avg_wind:.2f} kph" if pd.notna(avg_wind) else "- Avg Wind: —",
        f"- Avg Air Quality: {avg_aqi:.2f}" if pd.notna(avg_aqi) else "- Avg Air Quality: —",
        f"- Climate Index (0–100): {climate_index:.2f}"
    ]
    st.session_state["home_overview_summary"] = "\n".join(home_summary_lines)
# -----------------------
# MONTHLY TRENDS 
# -----------------------
elif page == "Monthly Trends":
    st.markdown("#### Monthly Climate Trends")

    # copy filtered monthly dataframe
    monthly_filtered2 = monthly_filtered.copy()

    # parse year_month to datetime (handle `YYYY-MM` format or other)
    # We'll coerce errors and drop rows with no year_month later
    monthly_filtered2['year_month_raw'] = monthly_filtered2['year_month']
    monthly_filtered2['year_month'] = pd.to_datetime(monthly_filtered2['year_month'], format="%Y-%m", errors='coerce')

    # If parsing failed for all, try generic parse
    if monthly_filtered2['year_month'].isna().all():
        monthly_filtered2['year_month'] = pd.to_datetime(monthly_filtered2['year_month_raw'], errors='coerce')

    # drop rows with NaT in year_month if none can be inferred
    monthly_filtered2 = monthly_filtered2.dropna(subset=['year_month']).sort_values('year_month')

    if monthly_filtered2.empty:
        st.info("No monthly data available for selection.")
    else:
        # create continuous full-month index covering full range (per selected countries)
        full_months = pd.date_range(start=monthly_filtered2["year_month"].min(), end=monthly_filtered2["year_month"].max(), freq='MS')
        full_month_labels = [d.strftime("%b%Y") for d in full_months]

        # Reindex per country so every country has every month (missing months get NaNs)
        all_countries = monthly_filtered2["country"].unique()
        filled_list = []
        for c in all_countries:
            t = monthly_filtered2[monthly_filtered2["country"] == c].copy()
            t = t.drop_duplicates(subset=["year_month"], keep="first")
            t = t.set_index("year_month")
            t = t.reindex(full_months)
            t = t.reset_index().rename(columns={"index": "year_month"})
            t["country"] = c
            filled_list.append(t)
        monthly_filtered2 = pd.concat(filled_list, ignore_index=True)

        # month_label for display
        monthly_filtered2["month_label"] = monthly_filtered2["year_month"].dt.strftime("%b%Y")

        # Month selector (affects KPIs only)
        all_months = monthly_filtered2["month_label"].dropna().unique().tolist()
        sel_month = st.selectbox("Select month for KPI (optional)", ["All"] + sorted(all_months), index=len(all_months))
        # Chart scope radio (shown side-by-side)
        chart_scope = st.radio("Chart scope", ["Full trend (default)", "Selected month only"], horizontal=True, key="month_scope")

        if sel_month != "All":
            kpi_df = monthly_filtered2[monthly_filtered2["month_label"] == sel_month]
        else:
            kpi_df = monthly_filtered2.copy()

        # KPIs
        c1, c2, c3, c4 = st.columns(4)
        avg_temp = kpi_df["temperature_celsius"].mean(skipna=True)
        avg_wind = kpi_df["wind_kph"].mean(skipna=True)
        avg_hum = kpi_df.get("humidity", pd.Series(dtype=float)).mean(skipna=True)
        avg_prec = kpi_df.get("precip_mm", pd.Series(dtype=float)).mean(skipna=True)

        with c1:
            st.markdown(f"<div class='metric-container'><h3>Avg Temperature (°C)</h3><p>{avg_temp:.2f}</p></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-container'><h3>Avg Wind (kph)</h3><p>{avg_wind:.2f}</p></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-container'><h3>Avg Humidity (%)</h3><p>{avg_hum:.2f}</p></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='metric-container'><h3>Avg Precip (mm)</h3><p>{avg_prec:.2f}</p></div>", unsafe_allow_html=True)

        st.markdown("---")

        # Chart type selectors
        chart_type1 = st.selectbox("Chart type - Temp trend", ["Line", "Bar", "Scatter", "Box"], key="m_ct1")
        chart_type2 = st.selectbox("Chart type - Wind trend", ["Line", "Bar", "Scatter", "Box"], key="m_ct2")
        chart_type3 = st.selectbox("Chart type - Combined AQI", ["Bar", "Line", "Scatter"], key="m_ct3")
        chart_type4 = st.selectbox("Chart type - Temp vs AQ", ["Scatter", "Line", "Bar"], key="m_ct4")

        # Prepare plotting DataFrame
        if chart_scope == "Selected month only" and sel_month != "All":
            plot_df = monthly_filtered2[monthly_filtered2["month_label"] == sel_month].copy()
        else:
            plot_df = monthly_filtered2.copy()

        # preserve chronological order before plotting
        plot_df = plot_df.sort_values("year_month")
        

        # Plotting: ensure x-axis contains all month labels (full_month_labels) so every month shows in axis
        st.session_state.setdefault("monthly_figures", {})
        r1c1, r1c2 = st.columns(2)
        r2c1, r2c2 = st.columns(2)

        with r1c1:
            if chart_type1 == "Line":
                fig = px.line(plot_df, x="month_label", y="temperature_celsius", color="country", markers=True, title="Monthly Temperature Trend")
            elif chart_type1 == "Bar":
                fig = px.bar(plot_df, x="month_label", y="temperature_celsius", color="country", barmode="group", title="Monthly Temperature")
            elif chart_type1 == "Scatter":
                fig = px.scatter(plot_df, x="month_label", y="temperature_celsius", color="country", title="Monthly Temperature (scatter)")
            else:
                fig = px.box(plot_df, x="country", y="temperature_celsius", title="Temperature Distribution")
            fig.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117")
            # set explicit ticks = full months so all months are visible
            try:
                fig.update_xaxes(tickangle=-45, tickmode='array', tickvals=full_month_labels, ticktext=full_month_labels)
            except Exception:
                fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            st.session_state["monthly_figures"]["temp_trend"] = fig


        with r1c2:
            if chart_type2 == "Line":
                fig = px.line(plot_df, x="month_label", y="wind_kph", color="country", markers=True, title="Monthly Wind Speed")
            elif chart_type2 == "Bar":
                fig = px.bar(plot_df, x="month_label", y="wind_kph", color="country", barmode="group", title="Wind Speed")
            elif chart_type2 == "Scatter":
                fig = px.scatter(plot_df, x="month_label", y="wind_kph", color="country", title="Wind Scatter")
            else:
                fig = px.box(plot_df, x="country", y="wind_kph", title="Wind Distribution")
            fig.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117")
            try:
                fig.update_xaxes(tickangle=-45, tickmode='array', tickvals=full_month_labels, ticktext=full_month_labels)
            except Exception:
                fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            st.session_state["monthly_figures"]["wind_trend"] = fig


        with r2c1:
            # combined AQI calculation (safe)
            if "air_quality_PM2.5" in plot_df.columns and "air_quality_Ozone" in plot_df.columns:
                plot_df["combined_AQI"] = plot_df["air_quality_PM2.5"] * 0.6 + plot_df["air_quality_Ozone"] * 0.4
            else:
                plot_df["combined_AQI"] = np.nan

            if chart_type3 == "Bar":
                fig = px.bar(plot_df, x="month_label", y="combined_AQI", color="country", barmode="group", title="Combined AQI")
            elif chart_type3 == "Line":
                fig = px.line(plot_df, x="month_label", y="combined_AQI", color="country", title="Combined AQI Trend")
            else:
                fig = px.scatter(plot_df, x="month_label", y="combined_AQI", color="country", title="Combined AQI Scatter")
            fig.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117")
            try:
                fig.update_xaxes(tickangle=-45, tickmode='array', tickvals=full_month_labels, ticktext=full_month_labels)
            except Exception:
                fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            st.session_state["monthly_figures"]["combined_aqi"] = fig


        with r2c2:
            if chart_type4 == "Scatter":
                ycol = "combined_AQI" if "combined_AQI" in plot_df.columns else "air_quality_PM2.5"
                fig = px.scatter(plot_df, x="temperature_celsius", y=ycol, color="country", title="Temp vs AQ")
            elif chart_type4 == "Line":
                fig = px.line(plot_df, x="month_label", y="temperature_celsius", color="country", title="Temp Trend (alt)")
            else:
                fig = px.bar(plot_df, x="month_label", y="temperature_celsius", color="country", title="Temp Bar")
            fig.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117")
            try:
                fig.update_xaxes(tickangle=-45, tickmode='array', tickvals=full_month_labels, ticktext=full_month_labels)
            except Exception:
                fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            st.session_state["monthly_figures"]["temp_vs_aq"] = fig
        # SAVE LAST SHOWN MONTHLY FIGURE FOR PDF
        try:
            st.session_state["monthly_current_fig"] = fig
        except:
            pass




# -----------------------
# YEARLY ANALYSIS 
# -----------------------
elif page == "Yearly Analysis":
    st.markdown("#### Yearly Climate Deep Analysis")
    if "year" in yearly_filtered.columns:
        all_years = sorted(yearly_filtered["year"].dropna().unique().tolist())
    else:
        all_years = []
    sel_year = st.selectbox("Select Year for KPI (optional)", ["All"] + all_years, index=len(all_years))
    if sel_year == "All":
        kpi_df = yearly_filtered.copy()
    else:
        kpi_df = yearly_filtered[yearly_filtered["year"] == sel_year]

    c1, c2, c3 = st.columns(3)
    avg_temp = kpi_df["temperature_celsius"].mean() if len(kpi_df) > 0 else np.nan
    avg_pm25 = kpi_df.get("air_quality_PM2.5", pd.Series(dtype=float)).mean() if len(kpi_df) > 0 else np.nan
    avg_hum = kpi_df.get("humidity", pd.Series(dtype=float)).mean() if len(kpi_df) > 0 else np.nan

    with c1:
        st.markdown(f"<div class='metric-container'><h3>Avg Temperature</h3><p>{avg_temp:.2f} °C</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-container'><h3>Avg PM2.5</h3><p>{avg_pm25:.2f}</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-container'><h3>Avg Humidity</h3><p>{avg_hum:.2f}%</p></div>", unsafe_allow_html=True)

    st.markdown("---")
    scope = st.radio("Chart scope", ["Full trend (default)", "Selected year only"], horizontal=True, key="year_scope")
    
    if scope == "Selected year only" and sel_year != "All":
        plot_df = yearly_filtered[yearly_filtered["year"] == sel_year]
    else:
        plot_df = yearly_filtered

    ct1 = st.selectbox("Chart type - Yearly Temp", ["Line", "Bar", "Scatter"], key="yct1")
    ct2 = st.selectbox("Chart type - Yearly AQ", ["Line", "Bar", "Scatter"], key="yct2")
    st.session_state.setdefault("yearly_figures", {})

    r1c1, r1c2 = st.columns(2)
    r2c1, r2c2 = st.columns(2)

    with r1c1:
        if ct1 == "Line":
            fig = px.line(plot_df, x="year", y="temperature_celsius", color="country", title="Yearly Temperature Trend", markers=True)
        elif ct1 == "Bar":
            fig = px.bar(plot_df, x="year", y="temperature_celsius", color="country", barmode="group", title="Yearly Temp")
        else:
            fig = px.scatter(plot_df, x="year", y="temperature_celsius", color="country", title="Yearly Temp Scatter")
        fig.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117")
        st.plotly_chart(fig, use_container_width=True)
        st.session_state["yearly_figures"]["yearly_temp_trend"] = fig


    with r1c2:
        if ct2 == "Line":
            fig = px.line(plot_df, x="year", y="air_quality_PM2.5", color="country", title="Yearly PM2.5 Trend", markers=True)
        elif ct2 == "Bar":
            fig = px.bar(plot_df, x="year", y="air_quality_PM2.5", color="country", barmode="group", title="Yearly PM2.5")
        else:
            fig = px.scatter(plot_df, x="year", y="air_quality_PM2.5", color="country", title="Yearly PM2.5 Scatter")
        fig.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117")
        st.plotly_chart(fig, use_container_width=True)
        st.session_state["yearly_figures"]["yearly_pm25_trend"] = fig


    with r2c1:
        fig = px.scatter(plot_df, x="temperature_celsius", y="humidity", color="country", title="Temp vs Humidity (Yearly)")
        fig.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117")
        st.plotly_chart(fig, use_container_width=True)

    with r2c2:
        fig = px.box(plot_df, x="country", y="air_quality_PM2.5", title="PM2.5 Distribution by Country")
        fig.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117")
        st.plotly_chart(fig, use_container_width=True)
        st.session_state["yearly_figures"]["temp_vs_humidity"] = fig
        st.session_state["yearly_figures"]["pm25_boxplot"] = fig
    # SAVE LAST SHOWN YEARLY FIGURE FOR PDF
    try:
        st.session_state["yearly_current_fig"] = fig
    except:
        pass

# -----------------------
# EXTREME EVENTS
# -----------------------
elif page == "Extreme Events":
    st.markdown("#### 🚨 Global & Daily Extreme Events Overview")

    # If date_range exists and is custom -> use that, else default to latest year (if available)
    apply_custom = user_selected_custom_range(date_range, daily_df)

    if apply_custom:
        start_dt = pd.to_datetime(date_range[0])
        end_dt = pd.to_datetime(date_range[1])
        df_range = daily_filtered[(daily_filtered["date"] >= start_dt) & (daily_filtered["date"] <= end_dt)].copy()
        header_scope = f"{start_dt.date()} → {end_dt.date()}"
    else:
        # if no custom range, try latest year
        if "year" in daily_filtered.columns:
            latest_year = int(daily_filtered["year"].max())
            df_range = daily_filtered[daily_filtered["year"] == latest_year].copy()
            header_scope = f"Latest year: {latest_year}"
        else:
            df_range = daily_filtered.copy()
            header_scope = "Full dataset"

    if df_range.empty:
        st.info("No daily data for this selection.")
    else:
        st.markdown(f"###### Scope: {header_scope}")

        # ensure numeric
        for col in ["temperature_celsius", "air_quality_PM2.5", "air_quality_PM10"]:
            if col in df_range.columns:
                df_range[col] = pd.to_numeric(df_range[col], errors="coerce")

        # compute per-country means for alerts
        extreme_df = df_range.groupby("country", as_index=False).agg({
            "temperature_celsius": "mean",
            "air_quality_PM2.5": "mean",
            "air_quality_PM10": "mean"
        })

        hottest = extreme_df.nlargest(5, "temperature_celsius")
        coldest = extreme_df.nsmallest(5, "temperature_celsius")
        polluted = extreme_df.dropna(subset=["air_quality_PM2.5"]).nlargest(5, "air_quality_PM2.5")

        alerts = []
        if not hottest.empty:
            alerts.append(f"🔥 Heat Alert: {hottest.iloc[0]['country']} averaged {hottest.iloc[0]['temperature_celsius']:.2f}°C.")
        if not coldest.empty:
            alerts.append(f"❄️ Cold Alert: {coldest.iloc[0]['country']} averaged {coldest.iloc[0]['temperature_celsius']:.2f}°C.")
        if not polluted.empty:
            alerts.append(f"☣️ Pollution Alert: {polluted.iloc[0]['country']} had PM2.5 {polluted.iloc[0]['air_quality_PM2.5']:.2f} µg/m³.")

        if alerts:
            for a in alerts:
                st.warning(a)
        else:
            st.success("No extreme alerts detected for this scope.")

        st.markdown("---")
        st.markdown("### 🌡️ Temperature Timeline with Extreme Days Highlighted")

        # detect extremes based on df_range percentiles
        def detect_extremes_local(df):
            out = {}
            for col in ["temperature_celsius", "precip_mm", "wind_kph", "air_quality_PM2.5"]:
                if col in df.columns:
                    colnum = pd.to_numeric(df[col], errors="coerce")
                    if colnum.dropna().empty:
                        continue
                    q95 = colnum.quantile(0.95)
                    q99 = colnum.quantile(0.99)
                    top = df[colnum >= q95].sort_values(col, ascending=False).head(10)
                    out[col] = {"95th": q95, "99th": q99, "top_example": top.head(3).to_dict(orient="records")}
            return out

        extremes = detect_extremes_local(df_range)

        fig = px.line(df_range.sort_values("date"), x="date", y="temperature_celsius", color="country", title="Daily Temperature Trend")
        if "temperature_celsius" in extremes:
            t95 = extremes["temperature_celsius"]["95th"]
            topdays = df_range[df_range["temperature_celsius"] >= t95]
            fig.add_trace(go.Scatter(x=topdays["date"], y=topdays["temperature_celsius"], mode="markers",
                                     marker=dict(color="red", size=8), name="Extreme Days"))
        fig.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 🌡️ Top Country Comparisons")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h3 style='font-size:18px; color:white;'> Hottest Countries</h3>", unsafe_allow_html=True)
            if not hottest.empty:
                st.bar_chart(hottest.set_index("country")["temperature_celsius"])
            else:
                st.info("No hot countries detected.")

        with col2:
            st.markdown("<h3 style='font-size:18px; color:white;'> Coldest Countries</h3>", unsafe_allow_html=True)
            if not coldest.empty:
                st.bar_chart(coldest.set_index("country")["temperature_celsius"])
            else:
                st.info("No cold countries detected.")

        st.markdown("---")
        st.markdown("#### ☣️ Most Polluted Countries (PM2.5)")
        if not polluted.empty:
            fig_polluted = px.bar(polluted.sort_values("air_quality_PM2.5"), x="air_quality_PM2.5", y="country",
                                  orientation="h", color="air_quality_PM2.5", color_continuous_scale="YlOrRd",
                                  title="Top Most Polluted Countries (PM2.5 µg/m³)")
            fig_polluted.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117", showlegend=False)
            st.plotly_chart(fig_polluted, use_container_width=True)
        else:
            st.info("No PM2.5 pollution data available for this scope.")

    # -----------------------------
    # Save summary for PDF export
    # -----------------------------
    st.session_state["extreme_summary"] = (
        f"Extreme Events Overview — Scope: {header_scope}\n"
        f"- Hottest Country: {hottest.iloc[0]['country']} ({hottest.iloc[0]['temperature_celsius']:.2f}°C)" if not hottest.empty else "- No heat data.\n"
    )

    # -----------------------------
    # Save ALL visuals for PDF
    # -----------------------------
    st.session_state["extreme_figures"] = {
        # Temperature timeline with extreme days
        "temp_timeline": locals().get("fig", None),

        # Hottest countries bar chart (streamlit native → converted to data)
        "hottest_data": hottest.set_index("country")["temperature_celsius"].to_dict(),

        # Coldest countries bar chart (streamlit native → converted to data)
        "coldest_data": coldest.set_index("country")["temperature_celsius"].to_dict(),

        # Polluted countries plotly figure
        "polluted": locals().get("fig_polluted", None)
    }


# -----------------------
# SEASONAL PATTERNS
# -----------------------
elif page == "Seasonal Patterns":
    st.markdown("#### Seasonal Patterns Comparison")
    years_avail = sorted(seasonal_filtered["year"].dropna().unique().tolist()) if "year" in seasonal_filtered.columns else []
    if years_avail:
        selected_year = st.selectbox("Select Year to compare seasons", years_avail, index=len(years_avail)-1)
        sdata = seasonal_filtered[seasonal_filtered["year"] == selected_year].copy()
    else:
        st.info("Seasonal data not available.")
        sdata = seasonal_filtered.copy()

    ct1 = st.selectbox("Chart type - Seasonal Temp", ["Box", "Bar", "Line"], key="sct1")
    ct2 = st.selectbox("Chart type - Seasonal AQ", ["Bar", "Box", "Line"], key="sct2")

    c1, c2 = st.columns(2)
    with c1:
        if ct1 == "Box":
            fig = px.box(sdata, x="season", y="temperature_celsius", color="country", title=f"Seasonal Temperature ({selected_year})")
        elif ct1 == "Bar":
            sf = sdata.groupby(["season", "country"])["temperature_celsius"].mean().reset_index()
            fig = px.bar(sf, x="season", y="temperature_celsius", color="country", barmode="group", title=f"Seasonal Avg Temp ({selected_year})")
        else:
            sf = sdata.groupby(["season", "country"])["temperature_celsius"].mean().reset_index()
            fig = px.line(sf, x="season", y="temperature_celsius", color="country", title=f"Seasonal Trend Temp ({selected_year})", markers=True)
        fig.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        if "air_quality_PM2.5" in sdata.columns:
            if ct2 == "Bar":
                sf = sdata.groupby(["season", "country"])["air_quality_PM2.5"].mean().reset_index()
                fig = px.bar(sf, x="season", y="air_quality_PM2.5", color="country", barmode="group", title=f"Seasonal PM2.5 ({selected_year})")
            elif ct2 == "Box":
                fig = px.box(sdata, x="season", y="air_quality_PM2.5", color="country", title=f"Seasonal PM2.5 ({selected_year})")
            else:
                sf = sdata.groupby(["season", "country"])["air_quality_PM2.5"].mean().reset_index()
                fig = px.line(sf, x="season", y="air_quality_PM2.5", color="country", title=f"Seasonal PM2.5 Trend ({selected_year})", markers=True)
            fig.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("PM2.5 not present in seasonal dataset.")
    # -----------------------------
    # Save Seasonal Summary for PDF
    # -----------------------------
    if "year" in seasonal_filtered.columns and not sdata.empty:
        avg_temp_season = sdata["temperature_celsius"].mean(skipna=True)
        avg_pm25_season = sdata["air_quality_PM2.5"].mean(skipna=True) if "air_quality_PM2.5" in sdata.columns else None

        seasonal_summary = [
            f"🌤 Seasonal Pattern Summary ({selected_year})",
            f"- Avg Temperature: {avg_temp_season:.2f}°C" if avg_temp_season is not None else "- Temperature not available",
            f"- Avg PM2.5: {avg_pm25_season:.2f}" if avg_pm25_season is not None else "- PM2.5 not available",
            f"- Seasons included: {', '.join(sorted(sdata['season'].dropna().unique()))}"
        ]
    else:
        seasonal_summary = ["Seasonal Pattern Summary — No valid data available."]

    st.session_state["seasonal_summary"] = "\n".join(seasonal_summary)

    # -----------------------------
    # Save Seasonal Figures for PDF
    # -----------------------------
    st.session_state["seasonal_figures"] = {
        "temp_season_chart": locals().get("fig", None),  # first seasonal fig (temperature)
        "aqi_season_chart": locals().get("fig", None)     # last assigned fig (AQ chart)
    }


# -----------------------
# Download Reports (PDF)
# -----------------------
elif page == "Download Reports":
    st.markdown("### 📘 Generate Custom Climate Report")
    st.info("Select dashboard pages to include in your PDF report. Each page will include the exact KPIs and charts currently displayed on those pages.")

    selected_pages = st.multiselect(
        "Select Dashboard Pages to Include:",
        ["🏠 Home Overview", "📅 Monthly Trends", "📆 Yearly Analysis", "⚠️ Extreme Events", "🍃 Seasonal Patterns"],
        default=["🏠 Home Overview"]
    )

    st.divider()
    figures_for_pdf = []
    summary_lines = []

    # Helper: Get fig from session_state safely
    def get_fig(key):
        try:
            return st.session_state.get(key, None)
        except:
            return None

    # -------------------------
    # 1) HOME OVERVIEW
    # -------------------------
    if "🏠 Home Overview" in selected_pages:
        summary_lines.append("🏠 Home Overview")
        home_summary = st.session_state.get("home_overview_summary", None)

        if home_summary:
            summary_lines.append(home_summary)
        else:
            summary_lines.append("- Home overview summary unavailable.")

        home_figs = st.session_state.get("home_figures", {})
        if home_figs.get("map"): figures_for_pdf.append(("Global Climate Map", home_figs["map"]))
        if home_figs.get("temp_trend"): figures_for_pdf.append(("Temperature Trend", home_figs["temp_trend"]))
        if home_figs.get("aq_trend"): figures_for_pdf.append(("Air Quality Trend", home_figs["aq_trend"]))
        if home_figs.get("scatter"): figures_for_pdf.append(("Temp vs AQ Scatter", home_figs["scatter"]))

    # -------------------------
    # 2) MONTHLY TRENDS
    # -------------------------
    if "📅 Monthly Trends" in selected_pages:
        summary_lines.append("\n📅 Monthly Trends")

        month_fig = get_fig("monthly_current_fig")
        if month_fig:
            figures_for_pdf.append(("Monthly Chart (as displayed)", month_fig))

        try:
            mdf = monthly_filtered.copy()
            mdf["year_month"] = pd.to_datetime(mdf["year_month"], errors='coerce')
            mdf = mdf.dropna(subset=["year_month"])
            summary_lines.append(f"- Months covered: {mdf['year_month'].nunique()}")
            summary_lines.append(f"- Avg Temp: {mdf['temperature_celsius'].mean():.2f}°C")
        except:
            summary_lines.append("- Monthly summary unavailable.")

    # -------------------------
    # 3) YEARLY ANALYSIS
    # -------------------------
    if "📆 Yearly Analysis" in selected_pages:
        summary_lines.append("\n📆 Yearly Analysis")

        year_fig = get_fig("yearly_current_fig")
        if year_fig:
            figures_for_pdf.append(("Yearly Chart (as displayed)", year_fig))

        try:
            yf = yearly_filtered.copy()
            summary_lines.append(f"- Years covered: {yf['year'].nunique()}")
            summary_lines.append(f"- Avg Temperature: {yf['temperature_celsius'].mean():.2f}°C")
        except:
            summary_lines.append("- Yearly summary unavailable.")

    # -------------------------
    # 4) EXTREME EVENTS
    # -------------------------
    if "⚠️ Extreme Events" in selected_pages:
        summary_lines.append("\n⚠️ Extreme Events")

        ext_figs = st.session_state.get("extreme_figures", {})
        if ext_figs.get("temp_timeline"):
            figures_for_pdf.append(("Daily Temperature Timeline", ext_figs["temp_timeline"]))
        if ext_figs.get("polluted"):
            figures_for_pdf.append(("Top Polluted Countries", ext_figs["polluted"]))

        ext_summary = st.session_state.get("extreme_summary", None)
        if ext_summary:
            summary_lines.append(ext_summary)

    # -------------------------
    # 5) SEASONAL PATTERNS
    # -------------------------
    if "🍃 Seasonal Patterns" in selected_pages:
        summary_lines.append("\n🍃 Seasonal Patterns")

        season_fig = get_fig("seasonal_current_fig")
        if season_fig:
            figures_for_pdf.append(("Seasonal Chart (as displayed)", season_fig))

        try:
            sdf = seasonal_filtered.copy()
            if "season" in sdf.columns:
                summary_lines.append(f"- Seasons available: {sdf['season'].nunique()}")
        except:
            summary_lines.append("- Seasonal summary unavailable.")

    # -------------------------
    # Build Summary Text
    # -------------------------
    summary_text = "\n".join(summary_lines)

    # -------------------------
    # PDF BUILDER (Always Use Local)
    # -------------------------
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, PageBreak
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    import tempfile

    def create_pdf_with_figures_local(figures, summary_text):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = getSampleStyleSheet()

        story = []
        story.append(Paragraph("🌍 <b>ClimateScope Report</b>", styles["Title"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(summary_text.replace("\n", "<br/>"), styles["Normal"]))
        story.append(PageBreak())

        for title, fig in figures:
            try:
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    fig.write_image(tmp.name, format="png", engine="kaleido")
                    story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
                    story.append(Image(tmp.name, width=6*inch, height=3.5*inch))
                    story.append(Spacer(1, 12))
            except Exception as e:
                story.append(Paragraph(f"⚠️ Failed to render {title}: {e}", styles["Normal"]))
                story.append(Spacer(1, 12))

        doc.build(story)
        buf.seek(0)
        return buf

    pdf_creator = create_pdf_with_figures_local

    # -------------------------
    # Download Button
    # -------------------------
    st.subheader("📥 Generate Report")
    if st.button("Generate PDF Report"):
        if not HAS_REPORTLAB or not HAS_KALEIDO:
            st.error("⚠️ Please install `reportlab` and `kaleido` to generate PDF with charts.")
        else:
            if len(figures_for_pdf) == 0:
                st.warning("No figures to include in PDF. Select at least one page.")
            else:
                buf = pdf_creator(figures_for_pdf, summary_text)
                st.download_button(
                    "⬇️ Download ClimateScope_Report.pdf",
                    data=buf.getvalue(),
                    file_name="ClimateScope_Report.pdf",
                    mime="application/pdf"
                )

# Footer
st.markdown("<hr style='border-color:#1E293B'/>", unsafe_allow_html=True)
st.markdown("<footer>Developed by Bhagyalaxmi Kali • ClimateScope • Global Weather Repository dataset</footer>", unsafe_allow_html=True)
