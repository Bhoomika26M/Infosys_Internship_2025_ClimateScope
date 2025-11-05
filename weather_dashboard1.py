"""
weather_dashboard1.py
ClimateScope Project — Dark Tech Theme (Pure Black + Neon Cyan Accents)
Final: multi-country rolling average, improved correlation heatmap,
natural-earth choropleth (pure black + white borders), attractive z-score KDE.
"""

import os
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

# Optional ISO mapping
try:
    import pycountry
except Exception:
    pycountry = None

# ------------------------
# CONFIG
# ------------------------
DATA_PATH = "cleaned_dataset.csv"
ALT_PATH = "C:/Users/jsrv7/.vscode/cleaned_dataset.csv"
if not os.path.exists(DATA_PATH) and os.path.exists(ALT_PATH):
    DATA_PATH = ALT_PATH

DEFAULT_Z = 3.0
ACCENT_COLOR = "#00E5FF"  # neon techy cyan
PX_TEMPLATE = "plotly_dark"  # Plotly dark template

# ------------------------
# PAGE + CSS (pure black)
# ------------------------
st.set_page_config(page_title="🌌 ClimateScope ", layout="wide", page_icon="🌍")

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: #000000; color: #ffffff; }}
    .header-card {{
        background: linear-gradient(90deg, rgba(0,230,255,0.06), rgba(0,150,255,0.04));
        padding: 16px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.03);
    }}
    /* Slightly larger heading + soft neon glow */
    .header-title {{ 
        font-size:50px; 
        font-weight:800; 
        color: #e6ffff; 
        margin:0; 
        text-shadow: 0 0 6px rgba(0,229,255,0.55), 0 0 12px rgba(0,229,255,0.35), 0 0 24px rgba(0,150,255,0.18);
        letter-spacing: 0.6px;
    }}
    .card {{ background: rgba(255,255,255,0.01); padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.03); }}
    .stSidebar .sidebar-content {{ background-color: #000000; color: #ffffff; }}
    .stButton>button {{ background: linear-gradient(90deg, {ACCENT_COLOR}, #0077b6); color: black; font-weight:600; border-radius:8px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="header-card">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div class="header-title">🌌 ClimateScope  Dashboard</div>
          <div style="font-size:15px;color:rgba(255,255,255,0.8)">Manual country input • Choropleth (natural earth) • Enhanced visuals</div>
        </div>
        <div style="text-align:right;color:rgba(255,255,255,0.6);font-size:11px">Streamlit • Plotly • Matplotlib • 2025</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
 
st.write("")

# ------------------------
# HELPERS
# ------------------------
@st.cache_data(ttl=3600)
def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data not found: {path}")
    df = pd.read_csv(path, low_memory=False)
    df.columns = [c.strip() for c in df.columns]

    # prefer last_updated
    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
        if df["last_updated"].notna().sum() > 0:
            df.rename(columns={"last_updated": "date"}, inplace=True)
            return df

    date_col = None
    for c in df.columns:
        if any(x in c.lower() for x in ["date", "time", "timestamp", "datetime", "recorded", "observation"]):
            try:
                df[c] = pd.to_datetime(df[c], errors="coerce")
            except Exception:
                pass
            if df[c].notna().sum() > 0:
                date_col = c
                break

    if not date_col:
        st.warning("⚠️ No valid date/time column detected — creating synthetic daily sequence.")
        df["date"] = pd.date_range(start="2000-01-01", periods=len(df), freq="D")
    elif date_col != "date":
        df.rename(columns={date_col: "date"}, inplace=True)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isna().all():
        st.warning("⚠️ All date values invalid — using synthetic range.")
        df["date"] = pd.date_range(start="2000-01-01", periods=len(df), freq="D")

    return df


def detect_country_col(df):
    for n in ["country", "region", "location", "country_name"]:
        for c in df.columns:
            if n == c.lower():
                return c
    for c in df.columns:
        if df[c].dtype == object and 1 < df[c].nunique() < 500:
            return c
    return None


def ensure_iso_alpha3(df, country_col):
    unmapped = []
    if "iso_alpha" in df.columns and df["iso_alpha"].notna().any():
        return df, unmapped
    if not country_col or pycountry is None:
        df["iso_alpha"] = None
        return df, unmapped
    mapping = {}
    for name in df[country_col].dropna().unique():
        try:
            mapping[name] = pycountry.countries.lookup(name).alpha_3
        except Exception:
            mapping[name] = None
            unmapped.append(name)
    df["iso_alpha"] = df[country_col].map(mapping)
    return df, unmapped


def numeric_parameters(df, exclude):
    nums = [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]
    return [c for c in nums if df[c].nunique() > 1]


def detect_extremes(df, param, z_thresh, group_col=None):
    if param not in df.columns:
        return pd.DataFrame()
    if group_col and group_col in df.columns:
        rows = []
        for g, sub in df.groupby(group_col):
            s = sub[param].dropna()
            if len(s) < 3:
                continue
            z = (s - s.mean()) / (s.std() if s.std() != 0 else 1)
            mask = z.abs() > z_thresh
            if mask.any():
                tmp = sub.loc[mask.index[mask]].copy()
                tmp["z_score"] = z.loc[mask].abs()
                rows.append(tmp)
        if not rows:
            return pd.DataFrame()
        return pd.concat(rows).sort_values("z_score", ascending=False)
    else:
        s = df[param].dropna()
        if s.empty:
            return pd.DataFrame()
        z = (s - s.mean()) / (s.std() if s.std() != 0 else 1)
        mask = z.abs() > z_thresh
        if not mask.any():
            return pd.DataFrame()
        out = df.loc[z[mask].index].copy()
        out["z_score"] = z.loc[z[mask].index].abs()
        return out.sort_values("z_score", ascending=False)


# ------------------------
# LOAD DATA
# ------------------------
try:
    df = load_data(DATA_PATH)
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

if df.empty:
    st.error("The dataset is empty!")
    st.stop()

# The user confirmed the dataset has column named 'country' — prefer that if present
country_col = detect_country_col(df)
if "country" in df.columns:
    country_col = "country"

df, unmapped_countries = ensure_iso_alpha3(df, country_col)

exclude = ["date", "iso_alpha"]
if country_col:
    exclude.append(country_col)
numeric_cols = numeric_parameters(df, exclude)

# ------------------------
# SIDEBAR: filters + manual country input
# ------------------------
with st.sidebar:
    st.markdown("<div class='card'><strong style='color:white'>🧭 Filters — ClimateScope </strong></div>", unsafe_allow_html=True)
    st.write("")

    # Manual country input
    st.markdown("**📍 Your Country (manual)**")
    user_country_manual = st.text_input("Enter your country name (optional)", value="").strip()

    # Date range
    min_ts = df["date"].dropna().min()
    max_ts = df["date"].dropna().max()
    min_dt = min_ts.date() if pd.notna(min_ts) else datetime.date(2000, 1, 1)
    max_dt = max_ts.date() if pd.notna(max_ts) else datetime.date(2000, 12, 31)
    date_range = st.date_input("📅 Date Range", (min_dt, max_dt), min_value=min_dt, max_value=max_dt)

    # Country selector with default from manual input + Select All
    if country_col:
        countries = sorted(df[country_col].dropna().astype(str).unique())

        sort_method = st.radio("🔢 Sort countries by", ["Alphabetical", "Average parameter value"], horizontal=True)
        if sort_method == "Average parameter value" and numeric_cols:
            temp_param_sort = st.selectbox("Sort by parameter (for ordering)", sorted(numeric_cols))
            avg_values = df.groupby(country_col)[temp_param_sort].mean().sort_values(ascending=False)
            countries_ordered = [c for c in list(avg_values.index) if c in countries]
            remaining = [c for c in countries if c not in countries_ordered]
            countries = countries_ordered + remaining

        default_selection = []
        if user_country_manual:
            matches = [c for c in countries if user_country_manual.lower() in c.lower()]
            if matches:
                default_selection = matches[:3]
        if not default_selection:
            default_selection = countries[:5]

        with st.expander("🌍 Country Filter", expanded=True):
            st.caption(f"{len(countries)} countries available")

            # New: Select all checkbox (when checked, multiselect default becomes all countries)
            select_all = st.checkbox("Select all countries", value=False, help="Check to select every country in the dataset")
            if select_all:
                multiselect_default = countries
            else:
                multiselect_default = default_selection

            selected_countries = st.multiselect("Select countries", countries, default=multiselect_default)
    else:
        selected_countries = []

    # Parameter & chart options
    param = st.selectbox("📊 Parameter", sorted(numeric_cols)) if numeric_cols else None
    agg_choice = st.selectbox("⏱ Aggregation", ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"])
    chart_type = st.selectbox("📈 Chart type", ["Line", "Area", "Scatter"])

    # Value range
    if param and df[param].notna().any():
        min_val, max_val = float(df[param].min()), float(df[param].max())
        value_range = st.slider(f"🔍 {param} range", min_val, max_val, (min_val, max_val))
    else:
        value_range = (None, None)

    # Rolling average options (window + allow multiple countries) - we'll show controls in Trends tab too
    rolling_window = st.slider("🔁 Rolling window (days)", min_value=3, max_value=365, value=30, step=1)

    # Extremes options
    z_thresh = st.slider("⚠️ Z-score threshold", 2.0, 6.0, DEFAULT_Z, 0.5)
    group_z = st.checkbox("Compute extremes within each country", value=True)

    # Reset filters
    if st.button("🔄 Reset filters"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.experimental_rerun()

st.write("")

# ------------------------
# APPLY FILTERS
# ------------------------
df_filtered = df.copy()
start_dt = pd.to_datetime(date_range[0])
end_dt = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
df_filtered = df_filtered[(df_filtered["date"] >= start_dt) & (df_filtered["date"] <= end_dt)]

if param and value_range[0] is not None:
    df_filtered = df_filtered[(df_filtered[param] >= value_range[0]) & (df_filtered[param] <= value_range[1])]

if country_col and selected_countries:
    df_filtered = df_filtered[df_filtered[country_col].astype(str).isin(selected_countries)]

# ------------------------
# TOP METRICS
# ------------------------
col1, col2, col3, col4 = st.columns([1.6, 1, 1, 1])
with col1:
    st.markdown("<div class='card'><strong style='color:white'>📌 Summary</strong></div>", unsafe_allow_html=True)
    st.caption("Overview of the filtered dataset")
    st.metric("Records", f"{len(df_filtered):,}")
with col2:
    st.markdown("<div class='card'><strong style='color:white'>📅 Range</strong></div>", unsafe_allow_html=True)
    dmin = df_filtered["date"].min().date() if not df_filtered["date"].isna().all() else "—"
    dmax = df_filtered["date"].max().date() if not df_filtered["date"].isna().all() else "—"
    st.metric("From → To", f"{dmin} → {dmax}")
with col3:
    st.markdown("<div class='card'><strong style='color:white'>🌍 Countries</strong></div>", unsafe_allow_html=True)
    n_countries = df_filtered[country_col].nunique() if country_col else 0
    st.metric("Countries Shown", f"{n_countries}")
with col4:
    st.markdown("<div class='card'><strong style='color:white'>🔢 Parameters</strong></div>", unsafe_allow_html=True)
    st.metric("Numerical Params", f"{len(numeric_cols)}")

st.write("")

# ------------------------
# TABS
# ------------------------
tab1, tab2, tab3 = st.tabs(["📈 Trends", "🗺 Regional Comparison", "⚠️ Extreme Events"])

# ------------------------
# TAB 1 — Trends (Plotly + multi-country rolling average + Plotly heatmap correlation)
# ------------------------
with tab1:
    st.markdown("<div class='card'><strong style='color:white'>📈 Trends Over Time</strong></div>", unsafe_allow_html=True)
    if not param:
        st.info("Select a numeric parameter to display trends.")
    else:
        freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "M", "Quarterly": "Q", "Yearly": "Y"}
        freq = freq_map.get(agg_choice, "D")

        # aggregated time series per country
        if country_col:
            df_ts = (
                df_filtered.groupby([country_col, pd.Grouper(key="date", freq=freq)])[param]
                .mean()
                .reset_index()
            )
            if chart_type == "Line":
                fig_main = px.line(df_ts, x="date", y=param, color=country_col, template=PX_TEMPLATE,
                                   title=f"{param} — {agg_choice} Trends by Country")
            elif chart_type == "Area":
                fig_main = px.area(df_ts, x="date", y=param, color=country_col, template=PX_TEMPLATE,
                                   title=f"{param} — {agg_choice} Area by Country")
            else:
                fig_main = px.scatter(df_ts, x="date", y=param, color=country_col, template=PX_TEMPLATE,
                                      title=f"{param} — {agg_choice} Scatter by Country", opacity=0.85)
        else:
            df_ts = df_filtered[["date", param]].dropna().sort_values("date")
            fig_main = px.line(df_ts, x="date", y=param, template=PX_TEMPLATE, title=f"{param} Trend ({agg_choice})")

        fig_main.update_layout(title_x=0.5, paper_bgcolor="#000000", plot_bgcolor="#000000", font=dict(color="white"))
        # accent first trace
        try:
            if fig_main.data:
                fig_main.data[0].line.color = ACCENT_COLOR
        except Exception:
            pass

        st.plotly_chart(fig_main, use_container_width=True)

        # ---- Multi-country rolling average ----
        st.markdown("<div class='card'><strong style='color:white'>🔁 Rolling Average — Multi-country</strong></div>", unsafe_allow_html=True)
        if country_col:
            # IMPORTANT: source rolling country options from the CURRENTLY filtered dataframe so it updates correctly
            country_options = sorted(df_filtered[country_col].dropna().astype(str).unique())
            # If no countries are available in the filtered dataset, fallback to full list
            if not country_options:
                country_options = sorted(df[country_col].dropna().astype(str).unique())

            # Determine sensible default: prefer sidebar selected_countries (if any), else top 3 of available options
            if selected_countries:
                default_for_roll = [c for c in selected_countries if c in country_options]
                if not default_for_roll:
                    default_for_roll = country_options[:3]
            else:
                default_for_roll = country_options[:3]

            # Use a stable key to avoid unexpected re-initialization; defaults are provided above
            selected_for_roll = st.multiselect(
                "Select countries for rolling average (multiple allowed)",
                country_options,
                default=default_for_roll,
                key="rolling_countries"
            )

            if selected_for_roll:
                roll_df_list = []
                for country in selected_for_roll:
                    sub = df_filtered[df_filtered[country_col].astype(str) == str(country)].sort_values("date")
                    if param in sub.columns and not sub.empty:
                        # compute rolling on the param series for that country's filtered data
                        s = sub.set_index("date")[param].rolling(window=rolling_window, min_periods=1).mean().reset_index()
                        s[country_col] = country
                        roll_df_list.append(s.rename(columns={param: param}))
                if roll_df_list:
                    roll_df = pd.concat(roll_df_list, ignore_index=True)
                    # make sure we use the same column name for color: rename to "country" for plotting consistency
                    roll_df = roll_df.rename(columns={country_col: "country"})
                    fig_roll = px.line(roll_df, x="date", y=param, color="country", template=PX_TEMPLATE,
                                       title=f"Rolling mean ({rolling_window}d) — selected countries")
                    fig_roll.update_layout(paper_bgcolor="#000000", plot_bgcolor="#000000", font=dict(color="white"))
                    st.plotly_chart(fig_roll, use_container_width=True)
                else:
                    st.info("No rolling data available for the selected countries and parameter.")
            else:
                st.info("Select one or more countries to compare rolling averages.")
        else:
            st.info("No country column detected; rolling average shown globally (use filters).")

        # ---- Improved correlation heatmap (Plotly) ----
        st.markdown("<div class='card'><strong style='color:white'>🔬 Parameter Correlation (interactive)</strong></div>", unsafe_allow_html=True)
        numeric_all = df_filtered.select_dtypes(include=[np.number]).copy()
        if numeric_all.shape[1] >= 2:
            corr = numeric_all.corr().fillna(0)
            # Use Plotly heatmap with annotations for better interactivity
            fig_corr = go.Figure(data=go.Heatmap(
                z=np.round(corr.values, 3),
                x=corr.columns,
                y=corr.index,
                colorscale="Blues",
                zmin=-1, zmax=1,
                colorbar=dict(title="corr")
            ))
            # add annotations
            annotations = []
            for i, row in enumerate(corr.values):
                for j, val in enumerate(row):
                    annotations.append(
                        dict(x=corr.columns[j], y=corr.index[i], text=str(round(val, 2)),
                             showarrow=False, font=dict(color="white", size=10))
                    )
            fig_corr.update_layout(template=PX_TEMPLATE, paper_bgcolor="#000000", plot_bgcolor="#000000",
                                   title="Correlation matrix (interactive)", annotations=annotations, font=dict(color="white"))
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Not enough numeric parameters for a correlation heatmap.")

# ------------------------
# TAB 2 — Regional Comparison (improved choropleth, natural earth + extras)
# ------------------------
with tab2:
    st.markdown("<div class='card'><strong style='color:white'>🗺 Regional Comparison</strong></div>", unsafe_allow_html=True)

    # Build aggregated mapping df
    if param and country_col:
        df_map = df_filtered.groupby([country_col]).agg(mean_val=(param, "mean"), count=("date", "count")).reset_index()
    else:
        df_map = pd.DataFrame()

    # Use iso_alpha if present & non-empty, else fallback to country names
    use_iso = "iso_alpha" in df_filtered.columns and df_filtered["iso_alpha"].notna().any()
    if not df_map.empty and param:
        if use_iso:
            # prefer ISO-3 mapping for accuracy
            df_map_iso = df_filtered.groupby(["iso_alpha", country_col]).agg(mean_val=(param, "mean"), count=("date", "count")).reset_index()
            locations = df_map_iso["iso_alpha"]
            locationmode = "ISO-3"
            hover_text = df_map_iso[country_col] + "<br>Mean: " + df_map_iso["mean_val"].round(3).astype(str) + "<br>Records: " + df_map_iso["count"].astype(str)
            z_vals = df_map_iso["mean_val"]
        else:
            # fallback to country names
            df_map_cn = df_filtered.groupby([country_col]).agg(mean_val=(param, "mean"), count=("date", "count")).reset_index()
            locations = df_map_cn[country_col]
            locationmode = "country names"
            hover_text = df_map_cn[country_col] + "<br>Mean: " + df_map_cn["mean_val"].round(3).astype(str) + "<br>Records: " + df_map_cn["count"].astype(str)
            z_vals = df_map_cn["mean_val"]

        # Improved choropleth using go.Choropleth for control
        chor = go.Choropleth(
            locations=locations,
            z=z_vals,
            text=hover_text,
            locationmode=locationmode,
            colorscale=[[0, "#001f3f"], [0.5, "#0066cc"], [1, ACCENT_COLOR]],
            zmin=float(z_vals.min()) if not z_vals.empty else 0.0,
            zmax=float(z_vals.max()) if not z_vals.empty else 1.0,
            marker_line_color="white",
            marker_line_width=0.9,
            colorbar=dict(title=f"Mean {param}", tickfont=dict(color="white")),
            showscale=True,
            autocolorscale=False,
            hoverinfo="text",
        )

        fig_map = go.Figure(data=[chor])
        fig_map.update_geos(
            projection_type="natural earth",
            showcountries=True,
            countrycolor="white",
            showland=True,
            landcolor="#000000",
            showocean=True,
            oceancolor="#000000",
            fitbounds="locations"
        )
        fig_map.update_layout(
            title=f"{param} — Choropleth (natural earth)",
            template=PX_TEMPLATE,
            paper_bgcolor="#000000",
            plot_bgcolor="#000000",
            font=dict(color="white"),
            margin=dict(l=0, r=0, t=50, b=0),
        )

        # extra polishing: stronger contrast for colorbar ticks
        if fig_map.layout.coloraxis:
            fig_map.layout.coloraxis.colorbar.tickfont.color = "white"

        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Choropleth requires a selected parameter and data for the selected filters. Provide iso_alpha or choose a parameter and adjust filters.")

    # Boxplot (top N countries)
    if country_col and param:
        st.markdown("<div class='card'><strong style='color:white'>📦 Distribution by Country (Top N)</strong></div>", unsafe_allow_html=True)
        df_box = df_filtered[[country_col, param]].dropna()
        if not df_box.empty:
            top_n = st.slider("Top N countries to display (by record count)", min_value=5, max_value=30, value=12, step=1)
            counts = df_box[country_col].value_counts().nlargest(top_n).index
            df_box_small = df_box[df_box[country_col].isin(counts)]
            fig_box = px.box(df_box_small, x=country_col, y=param, points="outliers", template=PX_TEMPLATE,
                             title=f"{param} distribution — top {top_n} countries")
            fig_box.update_layout(title_x=0.5)
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("No data for boxplot with current filters.")

    # Top / Bottom bar comparison (top 10 + bottom 10)
    if param and country_col:
        st.markdown("<div class='card'><strong style='color:white'>🏆 Top / Bottom Countries (mean)</strong></div>", unsafe_allow_html=True)
        agg = df_filtered.groupby(country_col)[param].mean().sort_values(ascending=False)
        if not agg.empty:
            topn = agg.head(10)
            botn = agg.tail(10)
            c1, c2 = st.columns(2)
            with c1:
                st.write("Top 10")
                fig_top = px.bar(topn.reset_index(), x=country_col, y=param, template=PX_TEMPLATE, color=param,
                                 color_continuous_scale=[[0, ACCENT_COLOR], [1, "#0077b6"]])
                fig_top.update_layout(paper_bgcolor="#000000", plot_bgcolor="#000000", showlegend=False)
                st.plotly_chart(fig_top, use_container_width=True)
            with c2:
                st.write("Bottom 10")
                fig_bot = px.bar(botn.reset_index(), x=country_col, y=param, template=PX_TEMPLATE, color=param,
                                 color_continuous_scale=px.colors.sequential.Plasma_r)
                fig_bot.update_layout(paper_bgcolor="#000000", plot_bgcolor="#000000", showlegend=False)
                st.plotly_chart(fig_bot, use_container_width=True)
        else:
            st.info("Not enough aggregated data to compute Top/Bottom.")

    # unmapped countries
    if unmapped_countries:
        with st.expander("Unmapped country names (not resolved to ISO-3)"):
            st.write(sorted(unmapped_countries))

# ------------------------
# TAB 3 — Extreme Events (improved z-score KDE + interactive scatter + heatmap)
# ------------------------
with tab3:
    st.markdown("<div class='card'><strong style='color:white'>⚠️ Extreme Events Detection</strong></div>", unsafe_allow_html=True)
    if not param:
        st.info("Select a numeric parameter to detect extremes.")
    else:
        extremes = detect_extremes(df_filtered, param, z_thresh, country_col if group_z else None)
        if extremes.empty:
            st.info("No extreme events detected for the selected filters.")
        else:
            st.success(f"Detected {len(extremes):,} extreme points (|z| > {z_thresh}).")

            # Interactive scatter of extremes (Plotly)
            st.markdown("<div class='card'><strong style='color:white'>📍 Extreme Points (interactive)</strong></div>", unsafe_allow_html=True)
            if country_col and country_col in extremes.columns:
                fig_sc = px.scatter(extremes, x="date", y=param, color="z_score", size="z_score", hover_name=country_col,
                                    hover_data=["date", param, "z_score"], template=PX_TEMPLATE, title="Extreme points over time")
            else:
                fig_sc = px.scatter(extremes, x="date", y=param, color="z_score", size="z_score",
                                    hover_data=["date", param, "z_score"], template=PX_TEMPLATE, title="Extreme points")
            fig_sc.update_layout(paper_bgcolor="#000000", plot_bgcolor="#000000", font=dict(color="white"))
            st.plotly_chart(fig_sc, use_container_width=True)

            # Attractive KDE plot for z_score (Matplotlib)
            if "z_score" in extremes.columns:
                st.markdown("<div class='card'><strong style='color:white'>📊 Z-score Density (KDE) — Attractive</strong></div>", unsafe_allow_html=True)
                zvals = extremes["z_score"].dropna().values
                if len(zvals) > 1:
                    kde = gaussian_kde(zvals)
                    xs = np.linspace(0, max(zvals.max(), z_thresh * 2), 500)
                    ys = kde(xs)

                    plt.style.use("dark_background")
                    fig, ax = plt.subplots(figsize=(7, 3), facecolor="black")
                    ax.fill_between(xs, ys, color=ACCENT_COLOR, alpha=0.35)
                    ax.plot(xs, ys, color=ACCENT_COLOR, linewidth=2.0)
                    ax.axvline(x=z_thresh, color="white", linestyle="--", linewidth=1.2, label=f"Threshold = {z_thresh}")
                    ax.axvline(x=-z_thresh, color="white", linestyle="--", linewidth=1.2)  # symmetric visual
                    ax.set_xlabel("Absolute z-score", color="white")
                    ax.set_ylabel("Density", color="white")
                    ax.set_title("Density of absolute z-scores (extreme points)", color="white")
                    ax.tick_params(colors="white")
                    ax.legend(facecolor="black", edgecolor="white", labelcolor="white")
                    st.pyplot(fig)
                    plt.style.use("default")
                else:
                    st.info("Not enough extreme z-score points to build KDE.")
            else:
                st.info("z_score not available in extremes.")

            # Heatmap of extremes by country-month (Matplotlib)
            st.markdown("<div class='card'><strong style='color:white'>🗺 Z-score Heatmap (country × month)</strong></div>", unsafe_allow_html=True)
            if country_col and "z_score" in extremes.columns:
                ex = extremes.copy()
                ex["month_year"] = ex["date"].dt.to_period("M").astype(str)
                pivot = ex.pivot_table(values="z_score", index=country_col, columns="month_year", aggfunc="max").fillna(0)
                pivot_small = pivot.iloc[:40, -12:]
                if not pivot_small.empty:
                    plt.style.use("dark_background")
                    fig, ax = plt.subplots(figsize=(10, max(3, 0.25 * pivot_small.shape[0])), facecolor="black")
                    im = ax.imshow(pivot_small.values, aspect='auto', cmap="magma")
                    ax.set_yticks(range(len(pivot_small.index)))
                    ax.set_yticklabels(pivot_small.index, color="white")
                    ax.set_xticks(range(len(pivot_small.columns)))
                    ax.set_xticklabels(pivot_small.columns, rotation=45, ha="right", color="white")
                    ax.set_title("Heatmap of max absolute z-score (sample)", color="white")
                    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
                    cbar.ax.yaxis.set_tick_params(color="white")
                    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
                    st.pyplot(fig)
                    plt.style.use("default")
                else:
                    st.info("Insufficient data for z-score heatmap.")
            else:
                st.info("Insufficient data to build z-score heatmap.")

            # Table of top extreme events
            with st.expander("View top extreme events (table)"):
                st.dataframe(extremes.sort_values("z_score", ascending=False).head(200))

# ------------------------
# FOOTER
# ------------------------
st.markdown("---")
st.markdown("<div style='color:rgba(255,255,255,0.7)'>✅ ClimateScope | Dark Tech Theme | Neon Cyan Accents | 2025</div>", unsafe_allow_html=True)
