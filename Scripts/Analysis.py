# analyse.py  (in-memory, returns results; no disk writes)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

DATA_PATH_DEFAULT = "../data/GlobalWeatherRepository_cleaned.csv"

KEY_NUMERIC_COLUMNS = [
    "temperature_celsius", "feels_like_celsius", "temperature_fahrenheit", "feels_like_fahrenheit",
    "wind_mph", "wind_kph", "gust_mph", "gust_kph",
    "humidity", "cloud", "visibility_km", "visibility_miles",
    "precip_mm", "precip_in", "pressure_mb", "pressure_in",
    "uv_index",
    "air_quality_Carbon_Monoxide", "air_quality_Ozone", "air_quality_Nitrogen_dioxide",
    "air_quality_Sulphur_dioxide", "air_quality_PM2.5", "air_quality_PM10",
    "air_quality_us-epa-index", "air_quality_gb-defra-index",
    "last_updated_epoch", "latitude", "longitude", "moon_illumination"
]


def load_data(path=DATA_PATH_DEFAULT):
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    if "last_updated" in df.columns:
        try:
            df["last_updated"] = pd.to_datetime(df["last_updated"]).dt.tz_localize(None)
        except Exception:
            pass
    return df


def descriptive_stats(df):
    num = df.select_dtypes(include=[np.number])
    desc = num.describe().T
    desc["skew"] = num.skew()
    desc["kurtosis"] = num.kurtosis()
    return desc


def country_aggregates(df, cols=None):
    cols = cols or KEY_NUMERIC_COLUMNS
    cols = [c for c in cols if c in df.columns]
    if "country" not in df.columns:
        return pd.DataFrame()
    agg = df.groupby("country")[cols].agg(["mean", "median", "std", "min", "max", "count"])
    return agg


def correlation_matrix(df):
    num = df.select_dtypes(include=[np.number])
    corr = num.corr(method="pearson")
    # simple heatmap figure
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr, interpolation="nearest")
    ax.set_xticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=90, fontsize=8)
    ax.set_yticks(range(len(corr.index)))
    ax.set_yticklabels(corr.index, fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.03)
    fig.suptitle("Correlation matrix (Pearson)")
    fig.tight_layout()
    return corr, fig


def monthly_trends(df, cols=None):
    if "date" not in df.columns:
        return pd.DataFrame(), None
    cols = cols or KEY_NUMERIC_COLUMNS
    cols = [c for c in cols if c in df.columns]
    tmp = df.copy()
    tmp["month"] = tmp["date"].dt.to_period("M")
    monthly = tmp.groupby("month")[cols].mean()
    # plot sample temperature trend when present
    fig = None
    if "temperature_celsius" in monthly.columns:
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot(monthly.index.to_timestamp(), monthly["temperature_celsius"])
        ax.set_xlabel("Month")
        ax.set_ylabel("Temperature (C)")
        ax.set_title("Monthly Average Temperature (C)")
        fig.tight_layout()
    return monthly, fig


def detect_extreme_events(df, temp_pct=0.95, wind_pct=0.95, precip_pct=0.95, vis_pct=0.05):
    num = df.select_dtypes(include=[np.number])
    thresholds = {}
    if "temperature_celsius" in num.columns:
        thresholds["high_temp"] = float(num["temperature_celsius"].quantile(temp_pct))
    if "wind_kph" in num.columns:
        thresholds["high_wind"] = float(num["wind_kph"].quantile(wind_pct))
    if "precip_mm" in num.columns:
        thresholds["heavy_precip"] = float(num["precip_mm"].quantile(precip_pct))
    if "visibility_km" in num.columns:
        thresholds["low_visibility"] = float(num["visibility_km"].quantile(vis_pct))

    df_ext = df.copy()
    conds = []
    extreme_type_list = []

    if "high_temp" in thresholds:
        df_ext["extreme_high_temp"] = df_ext["temperature_celsius"] >= thresholds["high_temp"]
        conds.append("extreme_high_temp")
    if "high_wind" in thresholds:
        df_ext["extreme_high_wind"] = df_ext["wind_kph"] >= thresholds["high_wind"]
        conds.append("extreme_high_wind")
    if "heavy_precip" in thresholds:
        df_ext["extreme_heavy_precip"] = df_ext["precip_mm"] >= thresholds["heavy_precip"]
        conds.append("extreme_heavy_precip")
    if "low_visibility" in thresholds:
        df_ext["extreme_low_visibility"] = df_ext["visibility_km"] <= thresholds["low_visibility"]
        conds.append("extreme_low_visibility")

    # Add a column listing the types of extremes per row
    def list_extremes(row):
        types = [c.replace("extreme_", "").replace("_", " ").title() for c in conds if row[c]]
        return ", ".join(types) if types else None

    df_ext["extreme_types"] = df_ext.apply(list_extremes, axis=1)

    # Flag overall extreme
    if conds:
        df_ext["is_extreme_event"] = df_ext[conds].any(axis=1)
    else:
        df_ext["is_extreme_event"] = False

    ext_events = df_ext[df_ext["is_extreme_event"]].copy()

    # Summary per country and type
    summary = {}
    for c in conds:
        if "country" in ext_events.columns:
            summary[c] = ext_events.groupby("country").size().sort_values(ascending=False)
        else:
            summary[c] = ext_events[c].sum()

    return thresholds, ext_events, summary

def region_comparisons(df, metric="temperature_celsius"):
    if metric not in df.columns:
        return pd.DataFrame(), None
    comp = df.groupby("country")[metric].agg(["mean", "median", "std", "min", "max", "count"]).sort_values("mean", ascending=False)
    # create a bar figure for top 20
    fig = None
    top = comp.head(20)
    if not top.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(range(len(top)), top["mean"])
        ax.set_xticks(range(len(top)))
        ax.set_xticklabels(top.index, rotation=90, fontsize=8)
        ax.set_title(f"Top 20 countries by mean {metric}")
        fig.tight_layout()
    return comp, fig