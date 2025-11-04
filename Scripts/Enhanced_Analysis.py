<<<<<<< HEAD
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from typing import Tuple, Dict, List, Optional
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.interpolate import griddata
import warnings
warnings.filterwarnings('ignore')

# Default data path
DATA_PATH_DEFAULT = "../data/GlobalWeatherRepository_cleaned.csv"

# Key numeric columns for analysis
=======
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


<<<<<<< HEAD
def load_data(path: str = DATA_PATH_DEFAULT) -> pd.DataFrame:
    """
    Load and preprocess the global weather dataset.

    Args:
        path: Path to the CSV file

    Returns:
        Preprocessed DataFrame with parsed dates and cleaned data
    """
    df = pd.read_csv(path)

    # Parse date columns
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors='coerce').dt.tz_localize(None)

    if "last_updated" in df.columns:
        try:
            df["last_updated"] = pd.to_datetime(df["last_updated"], errors='coerce').dt.tz_localize(None)
        except Exception:
            pass

    # Handle missing values for key numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            df[col].fillna(df[col].median(), inplace=True)

    return df


def descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate comprehensive descriptive statistics for all numeric columns.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with statistical summaries including mean, median, std, skew, kurtosis
    """

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

    desc["missing"] = num.isnull().sum()
    desc["missing_pct"] = (desc["missing"] / len(df) * 100).round(2)
    return desc


def country_aggregates(df: pd.DataFrame, cols: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Aggregate weather metrics by country with comprehensive statistics.

    Args:
        df: Input DataFrame
        cols: List of columns to aggregate (defaults to KEY_NUMERIC_COLUMNS)

    Returns:
        Multi-index DataFrame with aggregated statistics per country
    """
    if "country" not in df.columns:
        return pd.DataFrame()

    cols = cols or KEY_NUMERIC_COLUMNS
    cols = [c for c in cols if c in df.columns]


    return desc


def country_aggregates(df, cols=None):
    cols = cols or KEY_NUMERIC_COLUMNS
    cols = [c for c in cols if c in df.columns]
    if "country" not in df.columns:
        return pd.DataFrame()

    agg = df.groupby("country")[cols].agg(["mean", "median", "std", "min", "max", "count"])
    return agg


<<<<<<< HEAD
def correlation_matrix(df: pd.DataFrame) -> Tuple[pd.DataFrame, go.Figure]:
    """
    Compute correlation matrix and generate interactive heatmap.

    Args:
        df: Input DataFrame

    Returns:
        Tuple of (correlation DataFrame, Plotly figure)
    """
    num = df.select_dtypes(include=[np.number])
    corr = num.corr(method="pearson")

    # Create interactive Plotly heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale='RdBu_r',
        zmid=0,
        text=corr.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 8},
        colorbar=dict(title="Correlation")
    ))

    fig.update_layout(
        title="Weather Metrics Correlation Matrix",
        xaxis_title="",
        yaxis_title="",
        height=700,
        width=700,
        font=dict(size=10)
    )

    return corr, fig


def monthly_trends(df: pd.DataFrame, cols: Optional[List[str]] = None) -> Tuple[pd.DataFrame, Optional[go.Figure]]:
    """
    Calculate monthly aggregated trends for weather metrics.

    Args:
        df: Input DataFrame
        cols: Columns to analyze (defaults to KEY_NUMERIC_COLUMNS)

    Returns:
        Tuple of (monthly aggregated DataFrame, Plotly figure)
    """
    if "date" not in df.columns:
        return pd.DataFrame(), None

    cols = cols or KEY_NUMERIC_COLUMNS
    cols = [c for c in cols if c in df.columns]

    tmp = df.copy()
    tmp["month"] = tmp["date"].dt.to_period("M")
    monthly = tmp.groupby("month")[cols].mean()

    # Create interactive multi-line plot
    fig = None
    if "temperature_celsius" in monthly.columns:
        fig = go.Figure()

        # Add temperature trace
        fig.add_trace(go.Scatter(
            x=monthly.index.to_timestamp(),
            y=monthly["temperature_celsius"],
            mode='lines+markers',
            name='Temperature (°C)',
            line=dict(color='red', width=2),
            marker=dict(size=6)
        ))

        # Add humidity if available
        if "humidity" in monthly.columns:
            fig.add_trace(go.Scatter(
                x=monthly.index.to_timestamp(),
                y=monthly["humidity"],
                mode='lines+markers',
                name='Humidity (%)',
                line=dict(color='blue', width=2),
                marker=dict(size=6),
                yaxis='y2'
            ))

        fig.update_layout(
            title="Monthly Weather Trends",
            xaxis_title="Month",
            yaxis_title="Temperature (°C)",
            yaxis2=dict(
                title="Humidity (%)",
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            height=500,
            showlegend=True
        )

    return monthly, fig


def detect_extreme_events(
    df: pd.DataFrame,
    temp_pct: float = 0.95,
    wind_pct: float = 0.95,
    precip_pct: float = 0.95,
    vis_pct: float = 0.05
) -> Tuple[Dict, pd.DataFrame, Dict]:
    """
    Detect and flag extreme weather events based on percentile thresholds.

    Args:
        df: Input DataFrame
        temp_pct: Percentile threshold for high temperature
        wind_pct: Percentile threshold for high wind
        precip_pct: Percentile threshold for heavy precipitation
        vis_pct: Percentile threshold for low visibility

    Returns:
        Tuple of (thresholds dict, extreme events DataFrame, summary dict)
    """
    num = df.select_dtypes(include=[np.number])
    thresholds = {}

=======
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

    event_type_mapping = {}

    extreme_type_list = []


    if "high_temp" in thresholds:
        df_ext["extreme_high_temp"] = df_ext["temperature_celsius"] >= thresholds["high_temp"]
        conds.append("extreme_high_temp")
<<<<<<< HEAD
        event_type_mapping["extreme_high_temp"] = "Heatwave"

    if "high_wind" in thresholds:
        df_ext["extreme_high_wind"] = df_ext["wind_kph"] >= thresholds["high_wind"]
        conds.append("extreme_high_wind")
        event_type_mapping["extreme_high_wind"] = "Storm"

    if "heavy_precip" in thresholds:
        df_ext["extreme_heavy_precip"] = df_ext["precip_mm"] >= thresholds["heavy_precip"]
        conds.append("extreme_heavy_precip")
        event_type_mapping["extreme_heavy_precip"] = "Flood"

    if "low_visibility" in thresholds:
        df_ext["extreme_low_visibility"] = df_ext["visibility_km"] <= thresholds["low_visibility"]
        conds.append("extreme_low_visibility")
        event_type_mapping["extreme_low_visibility"] = "Drought"

    # Create extreme types list
    def list_extremes(row):
        types = [event_type_mapping[c] for c in conds if row[c]]

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


    # Add event color mapping
    def get_event_color(row):
        if pd.isna(row["extreme_types"]):
            return None
        if "Heatwave" in row["extreme_types"]:
            return "#FF0000"
        elif "Flood" in row["extreme_types"]:
            return "#0000FF"
        elif "Storm" in row["extreme_types"]:
            return "#9B59B6"
        elif "Drought" in row["extreme_types"]:
            return "#FFD700"
        return "#808080"

    df_ext["event_color"] = df_ext.apply(get_event_color, axis=1)


    # Flag overall extreme

    if conds:
        df_ext["is_extreme_event"] = df_ext[conds].any(axis=1)
    else:
        df_ext["is_extreme_event"] = False

    ext_events = df_ext[df_ext["is_extreme_event"]].copy()


    # Summary statistics
    summary = {}
    for c in conds:
        if "country" in ext_events.columns:
            summary[c] = ext_events.groupby("country")[c].sum().sort_values(ascending=False)

    # Summary per country and type
    summary = {}
    for c in conds:
        if "country" in ext_events.columns:
            summary[c] = ext_events.groupby("country").size().sort_values(ascending=False)

        else:
            summary[c] = ext_events[c].sum()

    return thresholds, ext_events, summary



def region_comparisons(df: pd.DataFrame, metric: str = "temperature_celsius") -> Tuple[pd.DataFrame, Optional[go.Figure]]:
    """
    Generate region-based comparisons for specified metric.

    Args:
        df: Input DataFrame
        metric: Metric to compare across regions

    Returns:
        Tuple of (comparison DataFrame, Plotly figure)
    """
    if metric not in df.columns or "country" not in df.columns:
        return pd.DataFrame(), None

    comp = df.groupby("country")[metric].agg(["mean", "median", "std", "min", "max", "count"]).sort_values("mean", ascending=False)

    # Create interactive bar chart for top 20 countries
    top = comp.head(20)
    fig = None

    if not top.empty:
        fig = go.Figure(data=[
            go.Bar(
                x=top.index,
                y=top["mean"],
                text=top["mean"].round(2),
                textposition='auto',
                marker=dict(
                    color=top["mean"],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title=metric)
                )
            )
        ])

        fig.update_layout(
            title=f"Top 20 Countries by Mean {metric.replace('_', ' ').title()}",
            xaxis_title="Country",
            yaxis_title=metric.replace('_', ' ').title(),
            height=500,
            xaxis_tickangle=-45
        )

    return comp, fig


def forecast_weather(df: pd.DataFrame, metric: str = "temperature_celsius", periods: int = 30) -> Tuple[pd.DataFrame, Optional[Dict]]:
    """
    Perform time-series forecasting using simple moving average and trend analysis.

    Args:
        df: Input DataFrame
        metric: Metric to forecast
        periods: Number of periods to forecast

    Returns:
        Tuple of (forecast DataFrame with insights, insights dict)
    """
    if "date" not in df.columns or metric not in df.columns:
        return pd.DataFrame(), None

    # Aggregate by date
    daily = df.groupby("date")[metric].mean().sort_index()

    # Simple moving average forecast
    window = min(7, len(daily) // 4)
    if window < 2:
        window = 2

    rolling_mean = daily.rolling(window=window).mean()

    # Calculate trend
    x = np.arange(len(daily))
    y = daily.values

    # Remove NaN values for trend calculation
    valid_idx = ~np.isnan(y)
    if valid_idx.sum() > 1:
        z = np.polyfit(x[valid_idx], y[valid_idx], 1)
        trend = np.poly1d(z)

        # Forecast future values
        future_x = np.arange(len(daily), len(daily) + periods)
        forecast_values = trend(future_x)

        # Create forecast dates
        last_date = daily.index[-1]
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=periods, freq='D')

        forecast_df = pd.DataFrame({
            'Date': forecast_dates,
            'Predicted Value': forecast_values.round(2)
        })

        # Generate insights
        insights = {
            'forecast_mean': float(forecast_values.mean()),
            'forecast_max': float(forecast_values.max()),
            'forecast_min': float(forecast_values.min()),
            'forecast_std': float(forecast_values.std()),
            'trend_direction': 'increasing' if z[0] > 0 else 'decreasing',
            'trend_rate': float(abs(z[0])),
            'historical_mean': float(daily.mean()),
            'historical_std': float(daily.std())
        }

        return forecast_df, insights

    return pd.DataFrame(), None


def forecast_multiple_metrics(df: pd.DataFrame, periods: int = 30) -> pd.DataFrame:
    """
    Forecast multiple weather metrics simultaneously.

    Args:
        df: Input DataFrame
        periods: Number of periods to forecast

    Returns:
        DataFrame with forecasts for temperature, humidity, and pressure
    """
    metrics = ['temperature_celsius', 'humidity', 'pressure_mb']
    available_metrics = [m for m in metrics if m in df.columns and 'date' in df.columns]

    if not available_metrics:
        return pd.DataFrame()

    forecast_results = {}

    for metric in available_metrics:
        forecast_df, _ = forecast_weather(df, metric=metric, periods=periods)
        if not forecast_df.empty:
            forecast_results[metric] = forecast_df['Predicted Value'].values

    if forecast_results:
        # Use the date from the first forecast
        first_forecast, _ = forecast_weather(df, metric=available_metrics[0], periods=periods)
        result_df = pd.DataFrame({
            'Date': first_forecast['Date']
        })

        for metric, values in forecast_results.items():
            column_name = metric.replace('_', ' ').title()
            result_df[column_name] = values

        return result_df

    return pd.DataFrame()


def generate_heatmap(df: pd.DataFrame, metric: str = "temperature_celsius") -> Optional[go.Figure]:
    """
    Generate geographic heatmap of specified metric using latitude/longitude.

    Args:
        df: Input DataFrame
        metric: Metric to visualize

    Returns:
        Plotly figure with geographic heatmap
    """
    required_cols = ["latitude", "longitude", metric]
    if not all(col in df.columns for col in required_cols):
        return None

    # Remove rows with missing coordinates
    df_map = df.dropna(subset=["latitude", "longitude", metric])

    if df_map.empty:
        return None

    fig = go.Figure(data=go.Scattergeo(
        lon=df_map["longitude"],
        lat=df_map["latitude"],
        mode='markers',
        marker=dict(
            size=5,
            color=df_map[metric],
            colorscale='RdYlBu_r',
            showscale=True,
            colorbar=dict(title=metric.replace('_', ' ').title()),
            opacity=0.7
        ),
        text=df_map["country"] if "country" in df_map.columns else None,
        hovertemplate='<b>%{text}</b><br>' +
                      f'{metric}: %{{marker.color:.2f}}<br>' +
                      'Lat: %{lat:.2f}<br>' +
                      'Lon: %{lon:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title=f"Global {metric.replace('_', ' ').title()} Distribution",
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
        ),
        height=600
    )

    return fig


def generate_3d_surface(df: pd.DataFrame, x_metric: str = "humidity", y_metric: str = "temperature_celsius", z_metric: str = "pressure_mb") -> Optional[go.Figure]:
    """
    Generate 3D surface plot showing relationships between three metrics.

    Args:
        df: Input DataFrame
        x_metric: Metric for X-axis
        y_metric: Metric for Y-axis
        z_metric: Metric for Z-axis (height)

    Returns:
        Plotly 3D figure
    """
    required_cols = [x_metric, y_metric, z_metric]
    if not all(col in df.columns for col in required_cols):
        return None

    # Remove rows with missing values
    df_3d = df[required_cols].dropna()

    if df_3d.empty or len(df_3d) < 10:
        return None

    # Create 3D scatter plot
    fig = go.Figure(data=[go.Scatter3d(
        x=df_3d[x_metric],
        y=df_3d[y_metric],
        z=df_3d[z_metric],
        mode='markers',
        marker=dict(
            size=3,
            color=df_3d[z_metric],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title=z_metric.replace('_', ' ').title()),
            opacity=0.6
        ),
        text=[f'{x_metric}: {x:.2f}<br>{y_metric}: {y:.2f}<br>{z_metric}: {z:.2f}'
              for x, y, z in zip(df_3d[x_metric], df_3d[y_metric], df_3d[z_metric])],
        hovertemplate='%{text}<extra></extra>'
    )])

    fig.update_layout(
        title=f"3D Visualization: {x_metric.replace('_', ' ').title()} vs {y_metric.replace('_', ' ').title()} vs {z_metric.replace('_', ' ').title()}",
        scene=dict(
            xaxis_title=x_metric.replace('_', ' ').title(),
            yaxis_title=y_metric.replace('_', ' ').title(),
            zaxis_title=z_metric.replace('_', ' ').title(),
        ),
        height=700
    )

    return fig


def perform_pca_analysis(df: pd.DataFrame) -> Tuple[pd.DataFrame, go.Figure, Dict]:
    """
    Perform Principal Component Analysis on weather data.

    Args:
        df: Input DataFrame

    Returns:
        Tuple of (PCA results DataFrame, visualization figure, insights dict)
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    # Select key weather metrics
    key_cols = [col for col in ['temperature_celsius', 'humidity', 'pressure_mb', 'wind_kph',
                                 'precip_mm', 'visibility_km'] if col in numeric_cols]

    if len(key_cols) < 2:
        return pd.DataFrame(), None, {}

    df_clean = df[key_cols].dropna()

    if len(df_clean) < 10:
        return pd.DataFrame(), None, {}

    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df_clean)

    # Perform PCA
    pca = PCA()
    pca_result = pca.fit_transform(scaled_data)

    # Create results DataFrame
    pca_df = pd.DataFrame(
        data=pca_result[:, :3],
        columns=['PC1', 'PC2', 'PC3']
    )

    # Create visualization
    fig = go.Figure(data=[go.Scatter(
        x=pca_df['PC1'],
        y=pca_df['PC2'],
        mode='markers',
        marker=dict(
            size=5,
            color=pca_df['PC3'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="PC3")
        ),
        text=[f'PC1: {x:.2f}<br>PC2: {y:.2f}<br>PC3: {z:.2f}'
              for x, y, z in zip(pca_df['PC1'], pca_df['PC2'], pca_df['PC3'])],
        hovertemplate='%{text}<extra></extra>'
    )])

    fig.update_layout(
        title="PCA Analysis - Principal Components",
        xaxis_title="First Principal Component",
        yaxis_title="Second Principal Component",
        height=600
    )

    # Generate insights
    explained_var = pca.explained_variance_ratio_
    insights = {
        'pc1_variance': float(explained_var[0] * 100),
        'pc2_variance': float(explained_var[1] * 100),
        'total_variance_2pc': float(sum(explained_var[:2]) * 100),
        'components': len(key_cols)
    }

    return pca_df, fig, insights


def perform_clustering(df: pd.DataFrame, n_clusters: int = 5) -> Tuple[pd.DataFrame, go.Figure, Dict]:
    """
    Perform K-Means clustering to identify similar climate zones.

    Args:
        df: Input DataFrame
        n_clusters: Number of clusters

    Returns:
        Tuple of (clustered data, visualization, insights)
    """
    key_cols = [col for col in ['temperature_celsius', 'humidity', 'pressure_mb', 'wind_kph']
                if col in df.columns]

    if len(key_cols) < 2:
        return pd.DataFrame(), None, {}

    df_clean = df[key_cols + ['country']].dropna() if 'country' in df.columns else df[key_cols].dropna()

    if len(df_clean) < n_clusters * 2:
        return pd.DataFrame(), None, {}

    # Standardize
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df_clean[key_cols])

    # Cluster
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(scaled_data)

    df_clean['Cluster'] = clusters

    # Create visualization using first two features
    fig = px.scatter(df_clean, x=key_cols[0], y=key_cols[1], color='Cluster',
                     title=f"Climate Zone Clustering ({n_clusters} clusters)",
                     labels={key_cols[0]: key_cols[0].replace('_', ' ').title(),
                            key_cols[1]: key_cols[1].replace('_', ' ').title()},
                     color_continuous_scale='viridis')
    fig.update_layout(height=600)

    # Generate insights
    cluster_sizes = pd.Series(clusters).value_counts().sort_index()
    insights = {
        'n_clusters': n_clusters,
        'largest_cluster': int(cluster_sizes.max()),
        'smallest_cluster': int(cluster_sizes.min()),
        'cluster_distribution': cluster_sizes.to_dict()
    }

    return df_clean, fig, insights


def detect_anomalies(df: pd.DataFrame, metric: str = 'temperature_celsius', threshold: float = 3.0) -> Tuple[pd.DataFrame, Dict]:
    """
    Detect anomalies using Z-score method.

    Args:
        df: Input DataFrame
        metric: Metric to analyze
        threshold: Z-score threshold for anomaly detection

    Returns:
        Tuple of (anomalies DataFrame, summary dict)
    """
    if metric not in df.columns:
        return pd.DataFrame(), {}

    df_clean = df[[metric, 'date', 'country']].dropna() if all(col in df.columns for col in [metric, 'date', 'country']) else df[[metric]].dropna()

    if len(df_clean) < 10:
        return pd.DataFrame(), {}

    # Calculate Z-scores
    mean = df_clean[metric].mean()
    std = df_clean[metric].std()
    df_clean['z_score'] = (df_clean[metric] - mean) / std

    # Identify anomalies
    anomalies = df_clean[abs(df_clean['z_score']) > threshold].copy()

    insights = {
        'total_anomalies': len(anomalies),
        'anomaly_percentage': float(len(anomalies) / len(df_clean) * 100),
        'mean': float(mean),
        'std': float(std),
        'threshold': threshold
    }

    return anomalies, insights


def generate_insights(df: pd.DataFrame) -> Dict[str, str]:
    """
    Generate AI-style text insights from the data.

    Args:
        df: Input DataFrame

    Returns:
        Dictionary of insight categories and their descriptions
    """
    insights = {}

    # Temperature insights
    if "temperature_celsius" in df.columns:
        temp_mean = df["temperature_celsius"].mean()
        temp_std = df["temperature_celsius"].std()
        temp_max = df["temperature_celsius"].max()
        temp_min = df["temperature_celsius"].min()

        insights["Temperature"] = (
            f"The average global temperature across all observations is {temp_mean:.2f}°C "
            f"with a standard deviation of {temp_std:.2f}°C. "
            f"Temperature ranges from {temp_min:.2f}°C to {temp_max:.2f}°C, "
            f"indicating {'high' if temp_std > 15 else 'moderate' if temp_std > 8 else 'low'} variability."
        )

    # Humidity insights
    if "humidity" in df.columns:
        humid_mean = df["humidity"].mean()
        insights["Humidity"] = (
            f"Average humidity levels are {humid_mean:.1f}%. "
            f"{'High humidity conditions dominate the dataset' if humid_mean > 70 else 'Moderate humidity levels are typical' if humid_mean > 50 else 'Generally dry conditions prevail'}."
        )

    # Wind insights
    if "wind_kph" in df.columns:
        wind_mean = df["wind_kph"].mean()
        wind_max = df["wind_kph"].max()
        insights["Wind"] = (
            f"Average wind speed is {wind_mean:.2f} km/h with maximum gusts reaching {wind_max:.2f} km/h. "
            f"{'Strong wind conditions are common' if wind_mean > 20 else 'Moderate wind patterns dominate' if wind_mean > 10 else 'Generally calm wind conditions'}."
        )

    # Precipitation insights
    if "precip_mm" in df.columns:
        precip_mean = df["precip_mm"].mean()
        precip_max = df["precip_mm"].max()
        rainy_days = (df["precip_mm"] > 0).sum()
        total_days = len(df)

        insights["Precipitation"] = (
            f"Average precipitation is {precip_mean:.2f} mm with maximum recorded at {precip_max:.2f} mm. "
            f"Precipitation occurred in {rainy_days/total_days*100:.1f}% of observations."
        )

    # Air quality insights
    if "air_quality_us-epa-index" in df.columns:
        aqi_mean = df["air_quality_us-epa-index"].mean()
        aqi_categories = {1: "Good", 2: "Moderate", 3: "Unhealthy for Sensitive Groups",
                         4: "Unhealthy", 5: "Very Unhealthy", 6: "Hazardous"}
        aqi_category = aqi_categories.get(round(aqi_mean), "Unknown")

        insights["Air Quality"] = (
            f"The average air quality index is {aqi_mean:.1f}, classified as '{aqi_category}'. "
            f"{'Air quality concerns should be monitored' if aqi_mean > 3 else 'Air quality is generally acceptable'}."
        )

    return insights


def analyze_correlation_insights(df: pd.DataFrame) -> Dict[str, str]:
    """
    Analyze correlations between metrics and generate interpretations.

    Args:
        df: Input DataFrame

    Returns:
        Dictionary of correlation insights
    """
    insights = {}

    # Temperature vs AQI
    if 'temperature_celsius' in df.columns and 'air_quality_us-epa-index' in df.columns:
        corr = df[['temperature_celsius', 'air_quality_us-epa-index']].corr().iloc[0, 1]
        if abs(corr) > 0.3:
            direction = "positive" if corr > 0 else "negative"
            insights['temp_aqi'] = f"There is a {direction} correlation ({corr:.2f}) between temperature and air quality index. {'Higher temperatures tend to worsen air quality' if corr > 0 else 'Higher temperatures tend to improve air quality'}."

    # Humidity vs Visibility
    if 'humidity' in df.columns and 'visibility_km' in df.columns:
        corr = df[['humidity', 'visibility_km']].corr().iloc[0, 1]
        if abs(corr) > 0.3:
            insights['humidity_visibility'] = f"Humidity and visibility show a correlation of {corr:.2f}. High humidity may {'reduce' if corr < 0 else 'increase'} visibility by {'trapping moisture in the air' if corr < 0 else 'clearing particulates'}."

    # Pressure vs Precipitation
    if 'pressure_mb' in df.columns and 'precip_mm' in df.columns:
        corr = df[['pressure_mb', 'precip_mm']].corr().iloc[0, 1]
        if abs(corr) > 0.2:
            insights['pressure_precip'] = f"Atmospheric pressure and precipitation are correlated at {corr:.2f}. {'Low pressure systems often bring rainfall' if corr < 0 else 'High pressure systems tend to bring clear skies'}."

    return insights


def generate_3d_chart(df: pd.DataFrame, x_metric: str = "humidity", y_metric: str = "temperature_celsius", z_metric: str = "pressure_mb", chart_type: str = "Scatter 3D") -> Optional[go.Figure]:
    """
    Generate various types of 3D charts showing relationships between three metrics.

    Args:
        df: Input DataFrame
        x_metric: Metric for X-axis
        y_metric: Metric for Y-axis
        z_metric: Metric for Z-axis (height)
        chart_type: Type of 3D chart (Scatter 3D, Surface, Line 3D, Mesh 3D, Bubble 3D)

    Returns:
        Plotly 3D figure
    """
    required_cols = [x_metric, y_metric, z_metric]
    if not all(col in df.columns for col in required_cols):
        return None

    df_3d = df[required_cols].dropna()

    if df_3d.empty or len(df_3d) < 10:
        return None

    fig = go.Figure()

    if chart_type == "Scatter 3D":
        fig.add_trace(go.Scatter3d(
            x=df_3d[x_metric],
            y=df_3d[y_metric],
            z=df_3d[z_metric],
            mode='markers',
            marker=dict(
                size=4,
                color=df_3d[z_metric],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title=z_metric.replace('_', ' ').title()),
                opacity=0.7
            ),
            text=[f'{x_metric}: {x:.2f}<br>{y_metric}: {y:.2f}<br>{z_metric}: {z:.2f}'
                  for x, y, z in zip(df_3d[x_metric], df_3d[y_metric], df_3d[z_metric])],
            hovertemplate='%{text}<extra></extra>'
        ))

    elif chart_type == "Surface":
        x_unique = np.linspace(df_3d[x_metric].min(), df_3d[x_metric].max(), 30)
        y_unique = np.linspace(df_3d[y_metric].min(), df_3d[y_metric].max(), 30)
        x_grid, y_grid = np.meshgrid(x_unique, y_unique)

        z_grid = griddata(
            (df_3d[x_metric], df_3d[y_metric]),
            df_3d[z_metric],
            (x_grid, y_grid),
            method='linear'
        )

        fig.add_trace(go.Surface(
            x=x_grid,
            y=y_grid,
            z=z_grid,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title=z_metric.replace('_', ' ').title()),
            opacity=0.9
        ))

    elif chart_type == "Line 3D":
        df_sorted = df_3d.sort_values(by=[x_metric, y_metric])

        fig.add_trace(go.Scatter3d(
            x=df_sorted[x_metric],
            y=df_sorted[y_metric],
            z=df_sorted[z_metric],
            mode='lines+markers',
            line=dict(
                color=df_sorted[z_metric],
                colorscale='Viridis',
                width=3
            ),
            marker=dict(
                size=3,
                color=df_sorted[z_metric],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title=z_metric.replace('_', ' ').title())
            ),
            text=[f'{x_metric}: {x:.2f}<br>{y_metric}: {y:.2f}<br>{z_metric}: {z:.2f}'
                  for x, y, z in zip(df_sorted[x_metric], df_sorted[y_metric], df_sorted[z_metric])],
            hovertemplate='%{text}<extra></extra>'
        ))

    elif chart_type == "Mesh 3D":
        sample_size = min(500, len(df_3d))
        df_sample = df_3d.sample(n=sample_size, random_state=42)

        fig.add_trace(go.Mesh3d(
            x=df_sample[x_metric],
            y=df_sample[y_metric],
            z=df_sample[z_metric],
            intensity=df_sample[z_metric],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title=z_metric.replace('_', ' ').title()),
            opacity=0.6,
            alphahull=5
        ))

    elif chart_type == "Bubble 3D":
        marker_sizes = (df_3d[z_metric] - df_3d[z_metric].min()) / (df_3d[z_metric].max() - df_3d[z_metric].min()) * 20 + 5

        fig.add_trace(go.Scatter3d(
            x=df_3d[x_metric],
            y=df_3d[y_metric],
            z=df_3d[z_metric],
            mode='markers',
            marker=dict(
                size=marker_sizes,
                color=df_3d[z_metric],
                colorscale='Plasma',
                showscale=True,
                colorbar=dict(title=z_metric.replace('_', ' ').title()),
                opacity=0.6,
                line=dict(width=0.5, color='white')
            ),
            text=[f'{x_metric}: {x:.2f}<br>{y_metric}: {y:.2f}<br>{z_metric}: {z:.2f}'
                  for x, y, z in zip(df_3d[x_metric], df_3d[y_metric], df_3d[z_metric])],
            hovertemplate='%{text}<extra></extra>'
        ))

    fig.update_layout(
        title=f"{chart_type}: {x_metric.replace('', ' ').title()} vs {y_metric.replace('', ' ').title()} vs {z_metric.replace('_', ' ').title()}",
        scene=dict(
            xaxis_title=x_metric.replace('_', ' ').title(),
            yaxis_title=y_metric.replace('_', ' ').title(),
            zaxis_title=z_metric.replace('_', ' ').title(),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        height=700
    )

    return fig

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

