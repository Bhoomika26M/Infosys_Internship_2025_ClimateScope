"""
ClimateScope - Weather Analytics Platform
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from scipy import stats
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# PAGE CONFIGURATION

st.set_page_config(
    page_title="ClimateScope",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PREMIUM CSS STYLING

st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        padding: 0rem 1rem;
        background: linear-gradient(to bottom, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Top Navigation Bar */
    .top-nav {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin: -1rem -1rem 2rem -1rem;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .logo-text {
        font-size: 2rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .logo-tagline {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.9);
        margin: 5px 0 0 0;
    }
    
    /* Enhanced Tab Styling with More Space */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 10px 15px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        overflow-x: auto;
        overflow-y: hidden;
        white-space: nowrap;
        display: flex;
        flex-wrap: wrap;
    }

    .stTabs [data-baseweb="tab"] {
        height: 60px;
        min-width: 150px;
        white-space: pre-wrap;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        gap: 8px;
        padding: 12px 20px;
        font-weight: 600;
        color: #2c3e50;
        border: 2px solid transparent;
        transition: all 0.3s ease;
        flex-shrink: 0;
    }

    /* Scrollbar for tabs on mobile */
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        height: 6px;
    }

    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    /* Responsive tabs */
    @media screen and (max-width: 1400px) {
        .stTabs [data-baseweb="tab"] {
            min-width: 130px;
            padding: 10px 16px;
            font-size: 0.9rem;
        }
    }

    @media screen and (max-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            min-width: 120px;
            padding: 8px 12px;
            font-size: 0.85rem;
            height: 50px;
        }
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: #667eea !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* Section Headers */
    h1, h2, h3, h4 {
        color: #2c3e50;
        font-weight: 700;
    }
    
    h2 {
        font-size: 1.8rem;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    /* Metrics Cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .stMetric label {
        color: #6c757d !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #2c3e50 !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
    }
    
    /* Insight Cards */
    .insight-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border-left: 5px solid #3498db;
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateX(5px);
    }
    
    .insight-card h3 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-size: 1.3rem;
    }
    
    .insight-card p {
        color: #495057;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Alert Boxes */
    .alert-info {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 5px solid #17a2b8;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #0c5460;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 5px solid #28a745;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #155724;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
        border-left: 5px solid #ffc107;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #856404;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    
    /* Sidebar - Enhanced visibility */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: white !important;
        font-weight: 500;
    }
    
    /* Sidebar inputs styling */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] textarea {
        background: rgba(255, 255, 255, 0.95) !important;
        color: #000000 !important;
        border: 2px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    /* Specific styling for text input placeholder */
    [data-testid="stSidebar"] input::placeholder {
        color: #6c757d !important;
        opacity: 0.8 !important;
    }
    
    /* Ensure text input text is visible */
    [data-testid="stSidebar"] [data-baseweb="input"] input {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar multiselect */
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background: rgba(255, 215, 0, 0.95) !important;
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar slider */
    [data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {
        background: white !important;
    }
    
    [data-testid="stSidebar"] .stSlider [data-testid="stTickBar"] {
        background: rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Sidebar date input */
    [data-testid="stSidebar"] [data-baseweb="input"] {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #2c3e50 !important;
    }
    
    /* SIDEBAR BUTTONS - Purple/Pink Gradient to Match Sidebar */
    [data-testid="stSidebar"] .stButton button,
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] .row-widget.stButton button,
    [data-testid="stSidebar"] button[kind="primary"],
    [data-testid="stSidebar"] button[kind="secondary"],
    [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] button,
    [data-testid="stSidebar"] div[data-testid="column"] button {
        background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%) !important;
        color: #FFFFFF !important;
        border: 3px solid rgba(255, 255, 255, 0.3) !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4) !important;
        padding: 0.75rem 1rem !important;
        border-radius: 10px !important;
        letter-spacing: 0.3px !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stSidebar"] .stButton button:hover,
    [data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #A78BFA 0%, #F472B6 100%) !important;
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.6) !important;
        color: #FFFFFF !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
    }
    
    [data-testid="stSidebar"] .stButton button:active,
    [data-testid="stSidebar"] button:active,
    [data-testid="stSidebar"] .stButton button:focus,
    [data-testid="stSidebar"] button:focus {
        background: linear-gradient(135deg, #7C3AED 0%, #DB2777 100%) !important;
        color: #FFFFFF !important;
        border-color: rgba(255, 255, 255, 0.6) !important;
    }
    
    /* Sidebar metrics */
    [data-testid="stSidebar"] .stMetric {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stSidebar"] .stMetric label,
    [data-testid="stSidebar"] .stMetric [data-testid="stMetricValue"],
    [data-testid="stSidebar"] .stMetric [data-testid="stMetricDelta"] {
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Sidebar expander */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 0 0 10px 10px !important;
    }
    
    /* Sidebar info box */
    [data-testid="stSidebar"] .stAlert {
        background: rgba(255, 255, 255, 0.2) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        color: white !important;
    }
    
    /* Sidebar markdown */
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Sidebar success/warning messages */
    [data-testid="stSidebar"] .element-container [data-testid="stNotification"] {
        background: rgba(255, 255, 255, 0.2) !important;
        border-left: 4px solid white !important;
        color: white !important;
    }
    
    /* Dataframes */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    /* Plotly Charts */
    .js-plotly-plot {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        border-radius: 10px;
        font-weight: 600;
        color: #2c3e50;
        padding: 1rem;
    }
    
    /* Loading State */
    .stSpinner > div {
        border-top-color: #667eea;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Selected Countries - Dark Text */
    .stMultiSelect [data-baseweb="select"] .selected-item {
        background: #FFD700 !important;
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* Make sure the multiselect dropdown text is also dark */
    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] div {
        color: #2c3e50 !important;  /* Dark text for dropdown */
    }

    /* Selected tags in sidebar */
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background: rgba(255, 215, 0, 0.95) !important;  /* Gold */
        color: #000000 !important;  /* Black text */
        font-weight: 600 !important;
    }
            
    /* Navbar Responsiveness - Enhanced */
    @media screen and (max-width: 1200px) {
        .top-nav {
            padding: 1rem 1rem;
        }
        .logo-text {
            font-size: 1.5rem;
        }
        .logo-tagline {
            font-size: 0.75rem;
        }
    }

    @media screen and (max-width: 768px) {
        .top-nav {
            padding: 0.75rem 0.5rem;
        }
        .logo-text {
            font-size: 1.2rem;
        }
        .logo-tagline {
            font-size: 0.65rem;
            display: none;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px;
            font-size: 0.85rem;
            height: auto;
        }
    }

    @media screen and (max-width: 480px) {
        .logo-text {
            font-size: 1rem;
        }
    }

    </style>
""", unsafe_allow_html=True)

# DATA LOADING FUNCTIONS

@st.cache_data(show_spinner=False)
def load_data():
    """Load and preprocess dataset"""
    try:
        df = pd.read_csv('global_weather_cleaned.csv')
        
        # Convert last_updated to datetime (not epoch)
        if 'last_updated' in df.columns:
            df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')
        
        # Convert other date columns
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        for col in date_cols:
            if col != 'last_updated' and col != 'last_updated_epoch':
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    except FileNotFoundError:
        st.error("❌ **Error:** 'global_weather_cleaned.csv' not found!")
        st.stop()
        return None

@st.cache_data
def identify_columns(df):
    """Identify key columns intelligently"""
    # Date column - prioritize last_updated
    date_col = None
    if 'last_updated' in df.columns:
        date_col = 'last_updated'
    else:
        date_candidates = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
        if date_candidates:
            date_col = max(date_candidates, key=lambda x: df[x].notna().sum())
    
    # Location columns
    location_col = None
    for col in ['location_name', 'name', 'location', 'city', 'country']:
        if col in df.columns:
            location_col = col
            break
    
    country_col = 'country' if 'country' in df.columns else None
    
    # Temperature column
    temp_col = None
    for col in ['temperature_celsius', 'temp_c', 'temperature']:
        if col in df.columns:
            temp_col = col
            break
    
    # Wind column
    wind_col = None
    for col in ['wind_kph', 'wind_speed_kph', 'wind_speed']:
        if col in df.columns:
            wind_col = col
            break
    
    # Pressure column
    pressure_col = None
    for col in ['pressure_mb', 'pressure']:
        if col in df.columns:
            pressure_col = col
            break
    
    # Humidity column
    humidity_col = None
    for col in ['humidity', 'humidity_percent']:
        if col in df.columns:
            humidity_col = col
            break
    
    return date_col, location_col, country_col, temp_col, wind_col, pressure_col, humidity_col

def detect_extreme_events(df, col, sigma=3):
    """Detect extreme events using z-score method"""
    if col not in df.columns or df[col].isna().all():
        return pd.DataFrame(), pd.DataFrame(), 0, 0
    
    valid_data = df[col].dropna()
    if len(valid_data) == 0:
        return pd.DataFrame(), pd.DataFrame(), 0, 0
    
    mean = valid_data.mean()
    std = valid_data.std()
    
    if std == 0 or np.isnan(std):
        return pd.DataFrame(), pd.DataFrame(), mean, mean
    
    upper = mean + sigma * std
    lower = mean - sigma * std
    
    extreme_high = df[df[col] > upper]
    extreme_low = df[df[col] < lower]
    
    return extreme_high, extreme_low, upper, lower

# LOAD DATA

with st.spinner('🚀 Loading ClimateScope...'):
    df = load_data()
    date_col, location_col, country_col, temp_col, wind_col, pressure_col, humidity_col = identify_columns(df)

# TOP NAVIGATION BAR

st.markdown("""
    <div class='top-nav'>
        <div class='logo-section'>
            <div>
                <div class='logo-text'>🌍 ClimateScope</div>
                <div class='logo-tagline'>Weather Intelligence Platform</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# SIDEBAR CONTROLS

with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 1rem; background: rgba(255,255,255,0.15); 
                    border-radius: 15px; margin-bottom: 1.5rem; border: 2px solid rgba(255,255,255,0.3);'>
            <h2 style='color: white; margin: 0; font-size: 1.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>
                🎯 Control Center
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'df_original' not in st.session_state:
        st.session_state.df_original = df.copy()
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    
    df_filtered = st.session_state.df_original.copy()
    
    # Advanced Filters
    st.markdown("""
        <h3 style='color: white; margin-top: 1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);'>
            🔍 Advanced Filters
        </h3>
    """, unsafe_allow_html=True)
    
    # Date Filter
    if date_col:
        with st.expander("📅 Date Range", expanded=True):
            min_date = pd.Timestamp(df_filtered[date_col].min())
            max_date = pd.Timestamp(df_filtered[date_col].max())
            
            if pd.notna(min_date) and pd.notna(max_date):
                st.markdown("<p style='color: white; font-weight: 600;'>Select Time Period:</p>", unsafe_allow_html=True)
                date_range = st.date_input(
                    "Date Range",
                    value=(min_date.date(), max_date.date()),
                    min_value=min_date.date(),
                    max_value=max_date.date(),
                    key='date_range',
                    label_visibility="collapsed"
                )
                
                if len(date_range) == 2:
                    start_date = pd.Timestamp(date_range[0])
                    end_date = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
                    df_filtered = df_filtered[(df_filtered[date_col] >= start_date) & (df_filtered[date_col] < end_date)]
                    days = (end_date - start_date).days
                    st.markdown(f"""
                        <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px; 
                                    text-align: center; margin-top: 0.5rem; border: 1px solid rgba(255,255,255,0.3);'>
                            <p style='color: white; margin: 0; font-weight: 600;'>✅ {days} days selected</p>
                        </div>
                    """, unsafe_allow_html=True)

    # Country Filter
    if country_col:
        with st.expander("🌐 Geographic Filter", expanded=True):
            all_countries = sorted([str(c) for c in df_filtered[country_col].dropna().unique()])
            
            st.markdown("<p style='color: white; font-weight: 600;'>Search & Select Countries:</p>", unsafe_allow_html=True)
            search = st.text_input("Search", "", key='country_search', label_visibility="collapsed", 
                                  placeholder="🔍 | 🇹 🇾 🇵 🇪   🇹 🇴   🇸 🇪 🇦 🇷 🇨 🇭   🇨 🇴 🇺 🇳 🇹 🇷 🇮 🇪 🇸 🌍")
            filtered_countries = [c for c in all_countries if search.lower() in c.lower()] if search else all_countries
            
            selected_countries = st.multiselect(
                "Countries",
                options=filtered_countries,
                default=filtered_countries[:5] if len(filtered_countries) <= 10 else [],
                key='countries',
                label_visibility="collapsed"
            )
            
            if selected_countries:
                df_filtered = df_filtered[df_filtered[country_col].isin(selected_countries)]
                st.markdown(f"""
                    <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px; 
                                text-align: center; margin-top: 0.5rem; border: 1px solid rgba(255,255,255,0.3);'>
                        <p style='color: white; margin: 0; font-weight: 600;'>✅ {len(selected_countries)} countries</p>
                    </div>
                """, unsafe_allow_html=True)
    
    # Temperature Filter
    if temp_col:
        with st.expander("🌡️ Temperature Range"):
            temp_min = float(df_filtered[temp_col].min())
            temp_max = float(df_filtered[temp_col].max())
            
            st.markdown("<p style='color: white; font-weight: 600;'>Temperature (°C):</p>", unsafe_allow_html=True)
            temp_range = st.slider(
                "Temp Range",
                temp_min, temp_max,
                (temp_min, temp_max),
                key='temp_range',
                label_visibility="collapsed"
            )
            df_filtered = df_filtered[(df_filtered[temp_col] >= temp_range[0]) & (df_filtered[temp_col] <= temp_range[1])]
            
            st.markdown(f"""
                <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px; 
                            text-align: center; margin-top: 0.5rem; border: 1px solid rgba(255,255,255,0.3);'>
                    <p style='color: white; margin: 0; font-weight: 600;'>{temp_range[0]:.1f}°C - {temp_range[1]:.1f}°C</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Humidity Filter
    if humidity_col:
        with st.expander("💧 Humidity Range"):
            hum_min = float(df_filtered[humidity_col].min())
            hum_max = float(df_filtered[humidity_col].max())
            
            st.markdown("<p style='color: white; font-weight: 600;'>Humidity (%):</p>", unsafe_allow_html=True)
            hum_range = st.slider(
                "Humidity Range",
                hum_min, hum_max,
                (hum_min, hum_max),
                key='hum_range',
                label_visibility="collapsed"
            )
            df_filtered = df_filtered[(df_filtered[humidity_col] >= hum_range[0]) & (df_filtered[humidity_col] <= hum_range[1])]
            
            st.markdown(f"""
                <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px; 
                            text-align: center; margin-top: 0.5rem; border: 1px solid rgba(255,255,255,0.3);'>
                    <p style='color: white; margin: 0; font-weight: 600;'>{hum_range[0]:.1f}% - {hum_range[1]:.1f}%</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Wind Speed Filter
    if wind_col:
        with st.expander("💨 Wind Speed Range"):
            wind_min = float(df_filtered[wind_col].min())
            wind_max = float(df_filtered[wind_col].max())
            
            st.markdown("<p style='color: white; font-weight: 600;'>Wind Speed (kph):</p>", unsafe_allow_html=True)
            wind_range = st.slider(
                "Wind Range",
                wind_min, wind_max,
                (wind_min, wind_max),
                key='wind_range',
                label_visibility="collapsed"
            )
            df_filtered = df_filtered[(df_filtered[wind_col] >= wind_range[0]) & (df_filtered[wind_col] <= wind_range[1])]
            
            st.markdown(f"""
                <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px; 
                            text-align: center; margin-top: 0.5rem; border: 1px solid rgba(255,255,255,0.3);'>
                    <p style='color: white; margin: 0; font-weight: 600;'>{wind_range[0]:.1f} - {wind_range[1]:.1f} kph</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Pressure Filter
    if pressure_col:
        with st.expander("🔽 Pressure Range"):
            pres_min = float(df_filtered[pressure_col].min())
            pres_max = float(df_filtered[pressure_col].max())
            
            st.markdown("<p style='color: white; font-weight: 600;'>Pressure (mb):</p>", unsafe_allow_html=True)
            pres_range = st.slider(
                "Pressure Range",
                pres_min, pres_max,
                (pres_min, pres_max),
                key='pres_range',
                label_visibility="collapsed"
            )
            df_filtered = df_filtered[(df_filtered[pressure_col] >= pres_range[0]) & (df_filtered[pressure_col] <= pres_range[1])]
            
            st.markdown(f"""
                <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px; 
                            text-align: center; margin-top: 0.5rem; border: 1px solid rgba(255,255,255,0.3);'>
                    <p style='color: white; margin: 0; font-weight: 600;'>{pres_range[0]:.1f} - {pres_range[1]:.1f} mb</p>
                </div>
            """, unsafe_allow_html=True)
    
    # UV Index Filter
    if 'uv_index' in df_filtered.columns:
        with st.expander("☀️ UV Index Range"):
            uv_min = float(df_filtered['uv_index'].min())
            uv_max = float(df_filtered['uv_index'].max())
            
            st.markdown("<p style='color: white; font-weight: 600;'>UV Index:</p>", unsafe_allow_html=True)
            uv_range = st.slider(
                "UV Range",
                uv_min, uv_max,
                (uv_min, uv_max),
                key='uv_range',
                label_visibility="collapsed"
            )
            df_filtered = df_filtered[(df_filtered['uv_index'] >= uv_range[0]) & (df_filtered['uv_index'] <= uv_range[1])]
            
            st.markdown(f"""
                <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px; 
                            text-align: center; margin-top: 0.5rem; border: 1px solid rgba(255,255,255,0.3);'>
                    <p style='color: white; margin: 0; font-weight: 600;'>{uv_range[0]:.1f} - {uv_range[1]:.1f}</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Visibility Filter
    if 'visibility_km' in df_filtered.columns:
        with st.expander("👁️ Visibility Range"):
            vis_min = float(df_filtered['visibility_km'].min())
            vis_max = float(df_filtered['visibility_km'].max())
            
            st.markdown("<p style='color: white; font-weight: 600;'>Visibility (km):</p>", unsafe_allow_html=True)
            vis_range = st.slider(
                "Visibility Range",
                vis_min, vis_max,
                (vis_min, vis_max),
                key='vis_range',
                label_visibility="collapsed"
            )
            df_filtered = df_filtered[(df_filtered['visibility_km'] >= vis_range[0]) & (df_filtered['visibility_km'] <= vis_range[1])]
            
            st.markdown(f"""
                <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px; 
                            text-align: center; margin-top: 0.5rem; border: 1px solid rgba(255,255,255,0.3);'>
                    <p style='color: white; margin: 0; font-weight: 600;'>{vis_range[0]:.1f} - {vis_range[1]:.1f} km</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Cloud Cover Filter
    if 'cloud' in df_filtered.columns:
        with st.expander("☁️ Cloud Cover"):
            cloud_min = float(df_filtered['cloud'].min())
            cloud_max = float(df_filtered['cloud'].max())
            
            st.markdown("<p style='color: white; font-weight: 600;'>Cloud Cover (%):</p>", unsafe_allow_html=True)
            cloud_range = st.slider(
                "Cloud Range",
                cloud_min, cloud_max,
                (cloud_min, cloud_max),
                key='cloud_range',
                label_visibility="collapsed"
            )
            df_filtered = df_filtered[(df_filtered['cloud'] >= cloud_range[0]) & (df_filtered['cloud'] <= cloud_range[1])]
            
            st.markdown(f"""
                <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px; 
                            text-align: center; margin-top: 0.5rem; border: 1px solid rgba(255,255,255,0.3);'>
                    <p style='color: white; margin: 0; font-weight: 600;'>{cloud_range[0]:.1f}% - {cloud_range[1]:.1f}%</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Weather Condition Filter
    if 'condition_text' in df_filtered.columns:
        with st.expander("🌤️ Weather Conditions"):
            all_conditions = sorted([str(c) for c in df_filtered['condition_text'].dropna().unique()])
            
            st.markdown("<p style='color: white; font-weight: 600;'>Select Conditions:</p>", unsafe_allow_html=True)
            selected_conditions = st.multiselect(
                "Conditions",
                options=all_conditions,
                default=[],
                key='conditions',
                label_visibility="collapsed"
            )
            
            if selected_conditions:
                df_filtered = df_filtered[df_filtered['condition_text'].isin(selected_conditions)]
                st.markdown(f"""
                    <div style='background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 8px; 
                                text-align: center; margin-top: 0.5rem; border: 1px solid rgba(255,255,255,0.3);'>
                        <p style='color: white; margin: 0; font-weight: 600;'>✅ {len(selected_conditions)} conditions</p>
                    </div>
                """, unsafe_allow_html=True)
    
    # Apply filters
    df = df_filtered.copy()
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; 
                    border: 2px solid rgba(255,255,255,0.4); margin-bottom: 1rem;'>
            <h3 style='color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); margin: 0; text-align: center;'>
                📊 Filter Summary
            </h3>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Records", f"{len(df):,}")
    with col2:
        pct = (len(df) / len(st.session_state.df_original) * 100)
        st.metric("Coverage", f"{pct:.1f}%")

    # Reset button
    st.markdown("""
        <div style='margin: 1.5rem 0;'>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 RESET ALL FILTERS", use_container_width=True, key="reset_btn"):
        # Clear all session state filter values
        for key in list(st.session_state.keys()):
            if key in ['date_range', 'country_search', 'countries', 'temp_range', 'hum_range', 
                       'wind_range', 'pres_range', 'uv_range', 'vis_range', 'cloud_range', 'conditions']:
                del st.session_state[key]
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Navigation Section
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; 
                    border: 2px solid rgba(255,255,255,0.4); margin-bottom: 1rem;'>
            <h3 style='color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); margin: 0; text-align: center;'>
                🧭 Quick Navigation
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons with session state for tab switching
    nav_col1, nav_col2 = st.columns(2)
    
    with nav_col1:
        if st.button("📊 Executive Dashboard", use_container_width=True, key="nav_exec"):
            st.session_state.active_tab = 0
            st.rerun()
        
        if st.button("📉 Data Distributions", use_container_width=True, key="nav_dist"):
            st.session_state.active_tab = 2
            st.rerun()
        
        if st.button("🌐 Regional Intelligence", use_container_width=True, key="nav_regional"):
            st.session_state.active_tab = 4
            st.rerun()
        
        if st.button("🔗 Correlations", use_container_width=True, key="nav_corr"):
            st.session_state.active_tab = 6
            st.rerun()
        
        if st.button("💧 Humidity Analysis", use_container_width=True, key="nav_humidity"):
            st.session_state.active_tab = 8
            st.rerun()
        
        if st.button("☀️ UV & Visibility", use_container_width=True, key="nav_uv"):
            st.session_state.active_tab = 10
            st.rerun()
        
        if st.button("🌡️ Comfort Index", use_container_width=True, key="nav_comfort"):
            st.session_state.active_tab = 12
            st.rerun()
    
    with nav_col2:
        if st.button("📈 Statistical Analysis", use_container_width=True, key="nav_stats"):
            st.session_state.active_tab = 1
            st.rerun()
        
        if st.button("🔥 Extreme Events", use_container_width=True, key="nav_extreme"):
            st.session_state.active_tab = 3
            st.rerun()
        
        if st.button("📅 Time Series", use_container_width=True, key="nav_time"):
            st.session_state.active_tab = 5
            st.rerun()
        
        if st.button("🗺️ Geographic Maps", use_container_width=True, key="nav_maps"):
            st.session_state.active_tab = 7
            st.rerun()
        
        if st.button("💨 Wind & Pressure", use_container_width=True, key="nav_wind"):
            st.session_state.active_tab = 9
            st.rerun()
        
        if st.button("☁️ Cloud & Weather", use_container_width=True, key="nav_cloud"):
            st.session_state.active_tab = 11
            st.rerun()
        
        if st.button("🌙 Astronomical Data", use_container_width=True, key="nav_astro"):
            st.session_state.active_tab = 13
            st.rerun()
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background: rgba(255,255,255,0.25); padding: 1rem; border-radius: 10px; 
                    border: 3px solid rgba(255,255,255,0.5); margin-bottom: 1rem;'>
            <h3 style='color: #FFFFFF; text-shadow: 2px 2px 4px rgba(0,0,0,0.7); margin: 0; text-align: center; font-size: 1.3rem;'>
                ℹ️ About
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background: rgba(255,255,255,0.15); padding: 1rem; border-radius: 10px; 
                    border: 2px solid rgba(255,255,255,0.3);'>
            <p style='color: white; line-height: 1.6; margin: 0;'>
                <strong>ClimateScope </strong> is an enterprise-grade weather analytics platform providing 
                real-time insights and predictive intelligence.
            </p>
            <br>
            <p style='color: white; margin: 5px 0;'><strong>Version:</strong> 3.0</p>
            <p style='color: white; margin: 5px 0;'><strong>Data Points:</strong> 1M+</p>
            <p style='color: white; margin: 5px 0;'><strong>Coverage:</strong> Global</p>
        </div>
    """, unsafe_allow_html=True)

# MAIN HORIZONTAL TABS

# Get the active tab from session state
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# Map tab index to tab name
tab_names = [
    "📊 Executive Dashboard",
    "📈 Statistical Analysis",
    "📉 Data Distributions",
    "🔥 Extreme Events",
    "🌐 Regional Intelligence",
    "📅 Time Series",
    "🔗 Correlations",
    "🗺️ Geographic Maps",
    "💧 Humidity Analysis",
    "💨 Wind & Pressure",
    "☀️ UV & Visibility",
    "☁️ Cloud & Weather",
    "🌡️ Comfort Index",
    "🌙 Astronomical Data"
]

# Create tabs with active state
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14 = st.tabs(tab_names)

# TAB 1: EXECUTIVE DASHBOARD

with tab1:
    st.markdown("## 📊 Executive Dashboard")
    st.markdown("Real-time key performance indicators and strategic insights")
    st.markdown("")
    
    # Top Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if country_col:
            st.metric("🌍 Countries", f"{df[country_col].nunique():,}", 
                     help="Number of unique countries in dataset")
    
    with col2:
        if location_col:
            st.metric("📍 Locations", f"{df[location_col].nunique():,}",
                     help="Number of unique monitoring stations")
    
    with col3:
        if temp_col:
            avg_temp = df[temp_col].mean()
            st.metric("🌡️ Avg Temperature", f"{avg_temp:.1f}°C",
                     delta=f"{avg_temp - 20:.1f}°C from 20°C",
                     help="Global average temperature")
    
    with col4:
        if wind_col:
            avg_wind = df[wind_col].mean()
            st.metric("💨 Avg Wind Speed", f"{avg_wind:.1f} kph",
                     help="Average wind speed across all locations")
    
    with col5:
        if date_col:
            days_range = (df[date_col].max() - df[date_col].min()).days
            st.metric("📅 Data Coverage", f"{days_range} days",
                     help="Temporal coverage of dataset")
    
    st.markdown("---")
    
    # Visual KPIs
    if temp_col and wind_col and humidity_col:
        st.markdown("### 🎯 Performance Indicators")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Temperature Gauge
            temp_avg = df[temp_col].mean()
            temp_min = df[temp_col].min()
            temp_max = df[temp_col].max()
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=temp_avg,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Temperature (°C)", 'font': {'size': 24, 'color': '#2c3e50'}},
                delta={'reference': 20, 'increasing': {'color': "#e74c3c"}, 'decreasing': {'color': "#3498db"}},
                gauge={
                    'axis': {'range': [temp_min, temp_max], 'tickwidth': 2, 'tickcolor': "#2c3e50"},
                    'bar': {'color': "#667eea", 'thickness': 0.75},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e9ecef",
                    'steps': [
                        {'range': [temp_min, temp_min + (temp_max-temp_min)*0.33], 'color': "#d1ecf1"},
                        {'range': [temp_min + (temp_max-temp_min)*0.33, temp_min + (temp_max-temp_min)*0.67], 'color': "#fff3cd"},
                        {'range': [temp_min + (temp_max-temp_min)*0.67, temp_max], 'color': "#f8d7da"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': temp_avg
                    }
                }
            ))
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Wind Speed Gauge
            wind_avg = df[wind_col].mean()
            wind_min = df[wind_col].min()
            wind_max = df[wind_col].max()
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=wind_avg,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Wind Speed (kph)", 'font': {'size': 24, 'color': '#2c3e50'}},
                delta={'reference': wind_max * 0.5},
                gauge={
                    'axis': {'range': [wind_min, wind_max], 'tickwidth': 2, 'tickcolor': "#2c3e50"},
                    'bar': {'color': "#4ECDC4", 'thickness': 0.75},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e9ecef",
                    'steps': [
                        {'range': [wind_min, wind_max * 0.5], 'color': "#d4edda"},
                        {'range': [wind_max * 0.5, wind_max], 'color': "#fff3cd"}
                    ],
                    'threshold': {
                        'line': {'color': "orange", 'width': 4},
                        'thickness': 0.75,
                        'value': wind_avg
                    }
                }
            ))
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Humidity Gauge
            hum_avg = df[humidity_col].mean()
            hum_min = df[humidity_col].min()
            hum_max = df[humidity_col].max()
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=hum_avg,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Humidity (%)", 'font': {'size': 24, 'color': '#2c3e50'}},
                gauge={
                    'axis': {'range': [hum_min, hum_max], 'tickwidth': 2, 'tickcolor': "#2c3e50"},
                    'bar': {'color': "#764ba2", 'thickness': 0.75},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e9ecef",
                    'steps': [
                        {'range': [hum_min, hum_max * 0.5], 'color': "#fff3cd"},
                        {'range': [hum_max * 0.5, hum_max], 'color': "#d1ecf1"}
                    ],
                    'threshold': {
                        'line': {'color': "blue", 'width': 4},
                        'thickness': 0.75,
                        'value': hum_avg
                    }
                }
            ))
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Quick Insights
    st.markdown("### 💡 Strategic Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if temp_col and country_col:
            hottest = df.groupby(country_col)[temp_col].mean().idxmax()
            hottest_temp = df.groupby(country_col)[temp_col].mean().max()
            st.markdown(f"""
                <div class='insight-card' style='border-left-color: #e74c3c;'>
                    <h3>🔥 Hottest Region</h3>
                    <p><strong style='font-size: 1.1em;'>{hottest}</strong></p>
                    <p style='font-size: 1.8em; color: #e74c3c; font-weight: 700; margin-top: 10px;'>{hottest_temp:.1f}°C</p>
                    <p style='color: #6c757d; margin-top: 10px; font-size: 0.9em;'>Average temperature significantly above global mean</p>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if temp_col and country_col:
            coldest = df.groupby(country_col)[temp_col].mean().idxmin()
            coldest_temp = df.groupby(country_col)[temp_col].mean().min()
            st.markdown(f"""
                <div class='insight-card' style='border-left-color: #3498db;'>
                    <h3>❄️ Coldest Region</h3>
                    <p><strong style='font-size: 1.1em;'>{coldest}</strong></p>
                    <p style='font-size: 1.8em; color: #3498db; font-weight: 700; margin-top: 10px;'>{coldest_temp:.1f}°C</p>
                    <p style='color: #6c757d; margin-top: 10px; font-size: 0.9em;'>Lowest average temperature recorded in dataset</p>
                </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if wind_col and country_col:
            windiest = df.groupby(country_col)[wind_col].mean().idxmax()
            windiest_speed = df.groupby(country_col)[wind_col].mean().max()
            st.markdown(f"""
                <div class='insight-card' style='border-left-color: #95a5a6;'>
                    <h3>💨 Windiest Region</h3>
                    <p><strong style='font-size: 1.1em;'>{windiest}</strong></p>
                    <p style='font-size: 1.8em; color: #95a5a6; font-weight: 700; margin-top: 10px;'>{windiest_speed:.1f} kph</p>
                    <p style='color: #6c757d; margin-top: 10px; font-size: 0.9em;'>Highest average wind speed among all regions</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Trend Overview
    if temp_col and date_col:
        st.markdown("### 📈 Temperature Trend Overview")
        
        # Prepare data
        df_temp = df[[date_col, temp_col]].dropna()
        
        if len(df_temp) > 0:
            df_temp = df_temp.set_index(date_col)
            daily_temp = df_temp.resample('D').mean().dropna()
            
            if len(daily_temp) > 1:
                fig = go.Figure()
                
                # Daily temperature line
                fig.add_trace(go.Scatter(
                    x=daily_temp.index,
                    y=daily_temp.values.flatten(),
                    mode='lines',
                    name='Daily Average',
                    line=dict(color='#667eea', width=2.5),
                    fill='tozeroy',
                    fillcolor='rgba(102, 126, 234, 0.15)',
                    hovertemplate='<b>Date:</b> %{x|%b %d, %Y}<br><b>Temperature:</b> %{y:.1f}°C<extra></extra>'
                ))
                
                # Add 7-day moving average
                if len(daily_temp) >= 7:
                    ma7 = daily_temp.rolling(window=7).mean().dropna()
                    fig.add_trace(go.Scatter(
                        x=ma7.index,
                        y=ma7.values.flatten(),
                        mode='lines',
                        name='7-Day Moving Average',
                        line=dict(color='#e74c3c', width=3, dash='dash'),
                        hovertemplate='<b>Date:</b> %{x|%b %d, %Y}<br><b>7-Day MA:</b> %{y:.1f}°C<extra></extra>'
                    ))
                
                fig.update_layout(
                    title={
                        'text': "Daily Temperature Trends with Moving Average",
                        'font': {'size': 20, 'color': '#2c3e50'}
                    },
                    xaxis=dict(
                        title="Date",
                        showgrid=True,
                        gridcolor='rgba(0,0,0,0.1)',
                        tickformat='%b %d\n%Y',
                        tickfont=dict(size=12)
                    ),
                    yaxis=dict(
                        title="Temperature (°C)",
                        showgrid=True,
                        gridcolor='rgba(0,0,0,0.1)',
                        tickfont=dict(size=12)
                    ),
                    height=450,
                    hovermode='x unified',
                    plot_bgcolor='white',
                    paper_bgcolor='rgba(0,0,0,0)',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        font=dict(size=12)
                    ),
                    margin=dict(l=60, r=40, t=80, b=60)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add insights below the chart
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_temp = float(daily_temp.mean().iloc[0]) if hasattr(daily_temp.mean(), 'iloc') else float(daily_temp.mean())
                    st.markdown(f"""
                        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    border-radius: 10px; color: white;'>
                            <h4 style='color: white; margin: 0;'>Average</h4>
                            <p style='font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;'>{avg_temp:.1f}°C</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    max_temp = float(daily_temp.max().iloc[0]) if hasattr(daily_temp.max(), 'iloc') else float(daily_temp.max())
                    max_date = daily_temp.idxmax()
                    if hasattr(max_date, 'iloc'):
                        max_date = max_date.iloc[0]
                    st.markdown(f"""
                        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); 
                                    border-radius: 10px; color: white;'>
                            <h4 style='color: white; margin: 0;'>Maximum</h4>
                            <p style='font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;'>{max_temp:.1f}°C</p>
                            <p style='font-size: 0.8rem; margin: 0;'>{max_date.strftime('%b %d, %Y')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    min_temp = float(daily_temp.min().iloc[0]) if hasattr(daily_temp.min(), 'iloc') else float(daily_temp.min())
                    min_date = daily_temp.idxmin()
                    if hasattr(min_date, 'iloc'):
                        min_date = min_date.iloc[0]
                    st.markdown(f"""
                        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); 
                                    border-radius: 10px; color: white;'>
                            <h4 style='color: white; margin: 0;'>Minimum</h4>
                            <p style='font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;'>{min_temp:.1f}°C</p>
                            <p style='font-size: 0.8rem; margin: 0;'>{min_date.strftime('%b %d, %Y')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
            else:
                st.info("ℹ️ Need multiple days of data for trend visualization. Try expanding your date range filter.")
        else:
            st.warning("⚠️ No temperature data available. Please adjust your filters.")

# TAB 2: STATISTICAL ANALYSIS

with tab2:
    st.markdown("## 📈 Statistical Analysis")
    st.markdown("Comprehensive statistical overview of weather data")
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Descriptive Statistics")
        numeric_cols = df.select_dtypes(include=[np.number]).columns[:8]
        stats_df = df[numeric_cols].describe().T
        stats_df = stats_df.round(2)
        
        st.dataframe(
            stats_df.style.background_gradient(cmap='RdYlGn', axis=1),
            use_container_width=True,
            height=400
        )
    
    with col2:
        st.markdown("#### 🔍 Data Quality Report")
        
        quality_data = pd.DataFrame({
            'Column': df.columns,
            'Non-Null': df.count(),
            'Null': df.isnull().sum(),
            'Null %': (df.isnull().sum() / len(df) * 100).round(2)
        })
        quality_data = quality_data[quality_data['Null'] > 0].sort_values('Null %', ascending=False)
        
        if len(quality_data) > 0:
            st.dataframe(
                quality_data.style.background_gradient(cmap='Reds', subset=['Null %']),
                use_container_width=True,
                height=400
            )
        else:
            st.markdown("""
                <div class='alert-success'>
                    <h4>✅ Perfect Data Quality!</h4>
                    <p>No missing values detected in the filtered dataset. All data points are complete and ready for analysis.</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Distribution Overview
    if temp_col and wind_col:
        st.markdown("#### 📊 Variable Distribution Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Box(
                y=df[temp_col],
                name='Temperature',
                marker_color='#667eea',
                boxmean='sd'
            ))
            fig.update_layout(
                title="Temperature Distribution (Box Plot)",
                yaxis_title="Temperature (°C)",
                height=350,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Box(
                y=df[wind_col],
                name='Wind Speed',
                marker_color='#4ECDC4',
                boxmean='sd'
            ))
            fig.update_layout(
                title="Wind Speed Distribution (Box Plot)",
                yaxis_title="Wind Speed (kph)",
                height=350,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

# TAB 3: DATA DISTRIBUTIONS

with tab3:
    st.markdown("## 📉 Data Distributions")
    st.markdown("Detailed distribution analysis of weather variables")
    st.markdown("")
    
    if temp_col:
        st.markdown("### 🌡️ Temperature Distribution Analysis")
        
        tab_hist, tab_violin, tab_country = st.tabs(["📊 Histogram", "🎻 Violin Plot", "🌍 By Country"])
        
        with tab_hist:
            fig = px.histogram(
                df, x=temp_col,
                nbins=50,
                marginal="box",
                color_discrete_sequence=['#667eea'],
                title="Temperature Distribution with Box Plot"
            )
            
            mean_temp = df[temp_col].mean()
            median_temp = df[temp_col].median()
            
            fig.add_vline(x=mean_temp, line_dash="dash", line_color="red", 
                         annotation_text=f"Mean: {mean_temp:.1f}°C", annotation_position="top")
            fig.add_vline(x=median_temp, line_dash="dot", line_color="green",
                         annotation_text=f"Median: {median_temp:.1f}°C", annotation_position="bottom")
            
            fig.update_layout(
                height=500,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Temperature (°C)",
                yaxis_title="Frequency"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab_violin:
            fig = go.Figure()
            fig.add_trace(go.Violin(
                y=df[temp_col],
                name="Temperature",
                box_visible=True,
                meanline_visible=True,
                fillcolor='#667eea',
                opacity=0.6,
                line_color='#764ba2'
            ))
            fig.update_layout(
                title="Temperature Density Distribution",
                yaxis_title="Temperature (°C)",
                height=500,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab_country:
            if country_col:
                top_countries = df[country_col].value_counts().head(10).index
                fig = px.box(
                    df[df[country_col].isin(top_countries)],
                    x=country_col,
                    y=temp_col,
                    title="Temperature Distribution by Top 10 Countries",
                    color=country_col,
                    points="outliers"
                )
                fig.update_xaxes(tickangle=-45)
                fig.update_layout(
                    height=500,
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Wind and Humidity
    col1, col2 = st.columns(2)
    
    with col1:
        if wind_col:
            st.markdown("### 💨 Wind Speed Distribution")
            fig = px.histogram(
                df, x=wind_col,
                nbins=50,
                marginal="rug",
                color_discrete_sequence=['#4ECDC4']
            )
            fig.add_vline(x=df[wind_col].mean(), line_dash="dash", line_color="red",
                         annotation_text="Mean")
            fig.update_layout(
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if humidity_col:
            st.markdown("### 💧 Humidity Distribution")
            fig = px.histogram(
                df, x=humidity_col,
                nbins=50,
                marginal="rug",
                color_discrete_sequence=['#F38181']
            )
            fig.add_vline(x=df[humidity_col].mean(), line_dash="dash", line_color="red",
                         annotation_text="Mean")
            fig.update_layout(
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

# TAB 4: EXTREME EVENTS

with tab4:
    st.markdown("## 🔥 Extreme Events Detection")
    st.markdown("Advanced anomaly detection using statistical methods")
    st.markdown("")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        sigma = st.slider(
            "🎚️ Detection Sensitivity (Standard Deviations)",
            1.0, 4.0, 3.0, 0.5,
            help="Higher values = stricter detection (fewer events)"
        )
    
    with col2:
        coverage = (1 - 2*(1-stats.norm.cdf(sigma)))*100
        st.metric("Coverage", f"{coverage:.2f}%", help="Percentage of data considered normal")
    
    # Detect extreme events
    extreme_results = {}
    
    if temp_col:
        extreme_high_temp, extreme_low_temp, upper_temp, lower_temp = detect_extreme_events(df, temp_col, sigma)
        extreme_results['Temperature'] = {
            'high': len(extreme_high_temp),
            'low': len(extreme_low_temp),
            'high_data': extreme_high_temp,
            'low_data': extreme_low_temp,
            'upper': upper_temp,
            'lower': lower_temp
        }
    
    if wind_col:
        extreme_high_wind, _, upper_wind, _ = detect_extreme_events(df, wind_col, sigma)
        extreme_results['Wind'] = {
            'high': len(extreme_high_wind),
            'high_data': extreme_high_wind,
            'upper': upper_wind
        }
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = extreme_results.get('Temperature', {}).get('high', 0) + extreme_results.get('Temperature', {}).get('low', 0)
        pct = (total / len(df) * 100) if len(df) > 0 else 0
        st.metric("🔥 Total Extremes", f"{total:,}", f"{pct:.2f}%")
    
    with col2:
        high_temp = extreme_results.get('Temperature', {}).get('high', 0)
        st.metric("🌡️ Heat Events", f"{high_temp:,}", delta="High")
    
    with col3:
        low_temp = extreme_results.get('Temperature', {}).get('low', 0)
        st.metric("❄️ Cold Events", f"{low_temp:,}", delta="Low")
    
    with col4:
        wind_extreme = extreme_results.get('Wind', {}).get('high', 0)
        st.metric("💨 Wind Events", f"{wind_extreme:,}", delta="Severe")
    
    st.markdown("---")
    
    # Visualization
    col1, col2 = st.columns(2)
    
    with col1:
        if temp_col and 'Temperature' in extreme_results:
            st.markdown("### 🌡️ Temperature Extremes")
            
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=df[temp_col],
                nbinsx=50,
                name='All Data',
                marker_color='lightblue',
                opacity=0.7
            ))
            
            if len(extreme_results['Temperature']['high_data']) > 0:
                fig.add_trace(go.Histogram(
                    x=extreme_results['Temperature']['high_data'][temp_col],
                    nbinsx=50,
                    name='Extreme High',
                    marker_color='red',
                    opacity=0.8
                ))
            
            if len(extreme_results['Temperature']['low_data']) > 0:
                fig.add_trace(go.Histogram(
                    x=extreme_results['Temperature']['low_data'][temp_col],
                    nbinsx=50,
                    name='Extreme Low',
                    marker_color='blue',
                    opacity=0.8
                ))
            
            fig.add_vline(x=extreme_results['Temperature']['upper'], line_dash="dash",
                         line_color="red", annotation_text="Upper Threshold")
            fig.add_vline(x=extreme_results['Temperature']['lower'], line_dash="dash",
                         line_color="blue", annotation_text="Lower Threshold")
            
            fig.update_layout(
                height=450,
                barmode='overlay',
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if wind_col and 'Wind' in extreme_results:
            st.markdown("### 💨 Wind Speed Extremes")
            
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=df[wind_col],
                nbinsx=50,
                name='All Data',
                marker_color='lightgreen',
                opacity=0.7
            ))
            
            if len(extreme_results['Wind']['high_data']) > 0:
                fig.add_trace(go.Histogram(
                    x=extreme_results['Wind']['high_data'][wind_col],
                    nbinsx=50,
                    name='Extreme High',
                    marker_color='darkred',
                    opacity=0.8
                ))
            
            fig.add_vline(x=extreme_results['Wind']['upper'], line_dash="dash",
                         line_color="red", annotation_text="Threshold")
            
            fig.update_layout(
                height=450,
                barmode='overlay',
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Extreme events table
    st.markdown("---")
    st.markdown("### 📋 Extreme Events Log")
    
    event_tabs = st.tabs(["🔴 High Temperature", "🔵 Low Temperature", "💨 High Wind"])
    
    with event_tabs[0]:
        if temp_col and len(extreme_results['Temperature']['high_data']) > 0:
            display_cols = [col for col in [date_col, country_col, location_col, temp_col] if col and col in df.columns]
            extreme_df = extreme_results['Temperature']['high_data'][display_cols].head(50)
            st.dataframe(
                extreme_df.style.background_gradient(cmap='Reds', subset=[temp_col]),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No extreme high temperature events detected.")
    
    with event_tabs[1]:
        if temp_col and len(extreme_results['Temperature']['low_data']) > 0:
            display_cols = [col for col in [date_col, country_col, location_col, temp_col] if col and col in df.columns]
            extreme_df = extreme_results['Temperature']['low_data'][display_cols].head(50)
            st.dataframe(
                extreme_df.style.background_gradient(cmap='Blues_r', subset=[temp_col]),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No extreme low temperature events detected.")
    
    with event_tabs[2]:
        if wind_col and len(extreme_results['Wind']['high_data']) > 0:
            display_cols = [col for col in [date_col, country_col, location_col, wind_col] if col and col in df.columns]
            extreme_df = extreme_results['Wind']['high_data'][display_cols].head(50)
            st.dataframe(
                extreme_df.style.background_gradient(cmap='Oranges', subset=[wind_col]),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No extreme high wind events detected.")

# TAB 5: REGIONAL INTELLIGENCE

with tab5:
    st.markdown("## 🌐 Regional Intelligence")
    st.markdown("Comparative analysis across geographic regions")
    st.markdown("")
    
    if country_col and temp_col and wind_col:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            top_n = st.slider("Number of Countries", 5, 30, 15, 5)
        
        with col2:
            sort_by = st.selectbox("Sort By", ["Temperature", "Wind Speed", "Data Points"])
        
        # Aggregate data
        country_stats = df.groupby(country_col).agg({
            temp_col: ['mean', 'std', 'min', 'max'],
            wind_col: ['mean', 'std', 'min', 'max'],
            country_col: 'count'
        }).reset_index()
        
        country_stats.columns = ['country', 'temp_mean', 'temp_std', 'temp_min', 'temp_max',
                                'wind_mean', 'wind_std', 'wind_min', 'wind_max', 'count']
        
        # Sort
        if sort_by == "Temperature":
            country_stats = country_stats.sort_values('temp_mean', ascending=False).head(top_n)
        elif sort_by == "Wind Speed":
            country_stats = country_stats.sort_values('wind_mean', ascending=False).head(top_n)
        else:
            country_stats = country_stats.sort_values('count', ascending=False).head(top_n)
        
        # Visualizations
        viz_tabs = st.tabs(["📊 Bar Charts", "🔄 Scatter Analysis", "🎯 Radar Chart"])
        
        with viz_tabs[0]:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    country_stats,
                    x='country',
                    y='temp_mean',
                    error_y='temp_std',
                    title=f"Top {top_n} Countries by Temperature",
                    color='temp_mean',
                    color_continuous_scale='RdYlBu_r'
                )
                fig.update_xaxes(tickangle=-45)
                fig.update_layout(height=450, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    country_stats,
                    x='country',
                    y='wind_mean',
                    error_y='wind_std',
                    title=f"Top {top_n} Countries by Wind Speed",
                    color='wind_mean',
                    color_continuous_scale='Viridis'
                )
                fig.update_xaxes(tickangle=-45)
                fig.update_layout(height=450, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        
        with viz_tabs[1]:
            fig = px.scatter(
                country_stats,
                x='temp_mean',
                y='wind_mean',
                size='count',
                hover_name='country',
                title="Temperature vs Wind Speed Correlation",
                color='temp_mean',
                color_continuous_scale='Turbo',
                size_max=50
            )
            fig.update_layout(height=500, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with viz_tabs[2]:
            # Radar chart for top 5
            top_5 = country_stats.head(5)
            
            fig = go.Figure()
            
            for _, row in top_5.iterrows():
                values = [
                    (row['temp_mean'] - country_stats['temp_mean'].min()) / (country_stats['temp_mean'].max() - country_stats['temp_mean'].min()),
                    (row['wind_mean'] - country_stats['wind_mean'].min()) / (country_stats['wind_mean'].max() - country_stats['wind_mean'].min()),
                    (row['temp_std'] - country_stats['temp_std'].min()) / (country_stats['temp_std'].max() - country_stats['temp_std'].min()),
                    (row['wind_std'] - country_stats['wind_std'].min()) / (country_stats['wind_std'].max() - country_stats['wind_std'].min()),
                    (row['count'] - country_stats['count'].min()) / (country_stats['count'].max() - country_stats['count'].min())
                ]
                
                fig.add_trace(go.Scatterpolar(
                    r=values + [values[0]],
                    theta=['Avg Temp', 'Avg Wind', 'Temp Variability', 'Wind Variability', 'Data Points', 'Avg Temp'],
                    fill='toself',
                    name=row['country']
                ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title="Multi-Dimensional Country Comparison (Top 5)",
                height=500,
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Statistics table
        st.markdown("---")
        st.markdown("### 📊 Detailed Statistics")
        
        styled_df = country_stats.style.format({
            'temp_mean': '{:.2f}',
            'temp_std': '{:.2f}',
            'temp_min': '{:.2f}',
            'temp_max': '{:.2f}',
            'wind_mean': '{:.2f}',
            'wind_std': '{:.2f}',
            'wind_min': '{:.2f}',
            'wind_max': '{:.2f}',
            'count': '{:,.0f}'
        }).background_gradient(cmap='RdYlGn', subset=['temp_mean'])\
          .background_gradient(cmap='Greens', subset=['wind_mean'])
        
        st.dataframe(styled_df, use_container_width=True, height=400)

# TAB 6: TIME SERIES

with tab6:
    st.markdown("## 📅 Time Series Analysis")
    st.markdown("Temporal trends and seasonal patterns")
    st.markdown("")
    
    if date_col:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            agg_method = st.selectbox("Aggregation", ['Daily', 'Weekly', 'Monthly'])
        
        with col2:
            show_trend = st.checkbox("Trend Line", value=True)
        
        with col3:
            show_ma = st.checkbox("Moving Average", value=False)
        
        freq = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M'}[agg_method]
        ma_window = {'Daily': 7, 'Weekly': 4, 'Monthly': 3}[agg_method]
        
        df_ts = df.copy().sort_values(date_col)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if temp_col:
                st.markdown("### 🌡️ Temperature Trend")
                
                ts_data = df_ts.set_index(date_col)[temp_col]
                ts_data = ts_data[ts_data.index.notna()]
                ts_data = ts_data.resample(freq).mean().dropna()
                
                st.info(f"📊 Data points: {len(ts_data)}")
                
                if len(ts_data) > 1:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=ts_data.index,
                        y=ts_data.values,
                        mode='lines+markers',
                        name='Temperature',
                        line=dict(color='#FF6B6B', width=3),
                        marker=dict(size=8)
                    ))
                    
                    if show_ma and len(ts_data) >= ma_window:
                        ma = ts_data.rolling(window=ma_window).mean()
                        fig.add_trace(go.Scatter(
                            x=ma.index,
                            y=ma.values,
                            mode='lines',
                            name=f'{ma_window}-MA',
                            line=dict(color='orange', width=2, dash='dot')
                        ))
                    
                    if show_trend and len(ts_data) >= 3:
                        x_num = np.arange(len(ts_data))
                        y_val = ts_data.values
                        mask = np.isfinite(y_val)
                        if mask.sum() >= 2:
                            z = np.polyfit(x_num[mask], y_val[mask], 1)
                            p = np.poly1d(z)
                            fig.add_trace(go.Scatter(
                                x=ts_data.index,
                                y=p(x_num),
                                mode='lines',
                                name='Trend',
                                line=dict(color='red', width=2, dash='dash')
                            ))
                    
                    fig.update_layout(
                        height=400,
                        plot_bgcolor='white',
                        paper_bgcolor='rgba(0,0,0,0)',
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"Switch to 'Daily' or expand date range")
        
        with col2:
            if wind_col:
                st.markdown("### 💨 Wind Speed Trend")
                
                ts_data = df_ts.set_index(date_col)[wind_col]
                ts_data = ts_data[ts_data.index.notna()]
                ts_data = ts_data.resample(freq).mean().dropna()
                
                st.info(f"📊 Data points: {len(ts_data)}")
                
                if len(ts_data) > 1:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=ts_data.index,
                        y=ts_data.values,
                        mode='lines+markers',
                        name='Wind Speed',
                        line=dict(color='#4ECDC4', width=3),
                        fill='tozeroy',
                        fillcolor='rgba(78, 205, 196, 0.2)',
                        marker=dict(size=8)
                    ))
                    
                    if show_ma and len(ts_data) >= ma_window:
                        ma = ts_data.rolling(window=ma_window).mean()
                        fig.add_trace(go.Scatter(
                            x=ma.index,
                            y=ma.values,
                            mode='lines',
                            name=f'{ma_window}-MA',
                            line=dict(color='darkblue', width=2, dash='dot')
                        ))
                    
                    fig.update_layout(
                        height=400,
                        plot_bgcolor='white',
                        paper_bgcolor='rgba(0,0,0,0)',
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"Switch to 'Daily' or expand date range")
        
        # Seasonal patterns
        if temp_col:
            st.markdown("---")
            st.markdown("### 📅 Seasonal Patterns")
            
            df_ts['month'] = df_ts[date_col].dt.month
            df_ts['season'] = df_ts['month'].map({
                12: 'Winter', 1: 'Winter', 2: 'Winter',
                3: 'Spring', 4: 'Spring', 5: 'Spring',
                6: 'Summer', 7: 'Summer', 8: 'Summer',
                9: 'Fall', 10: 'Fall', 11: 'Fall'
            })
            
            col1, col2 = st.columns(2)
            
            with col1:
                monthly = df_ts.groupby('month')[temp_col].agg(['mean', 'std']).reset_index()
                monthly['month_name'] = monthly['month'].map({
                    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
                    5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
                    9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
                })
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=monthly['month_name'],
                    y=monthly['mean'],
                    mode='lines+markers',
                    name='Average',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=10),
                    error_y=dict(type='data', array=monthly['std'])
                ))
                
                fig.update_layout(
                    title="Temperature by Month",
                    xaxis_title="Month",
                    yaxis_title="Temperature (°C)",
                    height=400,
                    plot_bgcolor='white',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.box(
                    df_ts,
                    x='season',
                    y=temp_col,
                    title="Temperature by Season",
                    color='season',
                    color_discrete_map={
                        'Winter': '#3498db',
                        'Spring': '#2ecc71',
                        'Summer': '#e74c3c',
                        'Fall': '#f39c12'
                    },
                    category_orders={'season': ['Winter', 'Spring', 'Summer', 'Fall']}
                )
                fig.update_layout(
                    height=400,
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)

# TAB 7: CORRELATIONS

with tab7:
    st.markdown("## 🔗 Correlation Analysis")
    st.markdown("Relationships between weather variables")
    st.markdown("")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns[:10]
    
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🔗 Correlation Heatmap")
            
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu_r',
                zmid=0,
                text=np.round(corr_matrix.values, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(title="Correlation")
            ))
            
            fig.update_layout(
                title="Variable Correlation Matrix",
                height=500,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 💪 Strong Correlations")
            
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.5:
                        strong_corr.append({
                            'Var 1': corr_matrix.columns[i],
                            'Var 2': corr_matrix.columns[j],
                            'Correlation': corr_val,
                            'Strength': 'Strong' if abs(corr_val) > 0.7 else 'Moderate'
                        })
            
            if strong_corr:
                strong_df = pd.DataFrame(strong_corr).sort_values('Correlation', key=abs, ascending=False)
                st.dataframe(
                    strong_df.style.background_gradient(cmap='RdYlGn', subset=['Correlation']),
                    use_container_width=True,
                    height=400
                )
            else:
                st.info("No strong correlations (|r| > 0.5) found")
        
        # Scatter matrix
        if temp_col and wind_col and humidity_col:
            st.markdown("---")
            st.markdown("### 📊 Multi-Variable Scatter Matrix")
            
            sample_df = df[[temp_col, wind_col, humidity_col]].dropna().sample(min(2000, len(df)))
            
            fig = px.scatter_matrix(
                sample_df,
                dimensions=[temp_col, wind_col, humidity_col],
                color=temp_col,
                color_continuous_scale='Turbo',
                opacity=0.6,
                height=600
            )
            fig.update_traces(diagonal_visible=False)
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

# TAB 8: GEOGRAPHIC MAPS

with tab8:
    st.markdown("## 🗺️ Geographic Visualizations")
    st.markdown("Interactive global weather mapping")
    st.markdown("")
    
    if country_col and temp_col:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            map_var = st.selectbox(
                "Select Variable",
                [temp_col, wind_col, humidity_col] if wind_col and humidity_col else [temp_col]
            )
        
        with col2:
            map_projection = st.selectbox(
                "Map Style",
                ["natural earth", "orthographic", "equirectangular"]
            )
        
        # Choropleth map
        country_avg = df.groupby(country_col)[map_var].mean().reset_index()
        country_avg.columns = ['country', 'avg_value']
        
        st.markdown(f"### 🗺️ Global {map_var} Distribution")
        
        fig = px.choropleth(
            country_avg,
            locations='country',
            locationmode='country names',
            color='avg_value',
            hover_name='country',
            color_continuous_scale='RdYlBu_r' if map_var == temp_col else 'Viridis',
            title=f"Average {map_var} by Country",
            labels={'avg_value': f'Avg {map_var}'},
            projection=map_projection
        )
        fig.update_geos(
            showcountries=True, 
            countrycolor="white",
            showcoastlines=True,
            coastlinecolor="white",
            bgcolor="black",
            showland=True,
            landcolor="rgba(50, 50, 50, 0.8)",
            showocean=True,
            oceancolor="black",
            showlakes=True,
            lakecolor="black"
        )
        fig.update_layout(
            height=600, 
            margin={"r":0,"t":50,"l":0,"b":0}, 
            paper_bgcolor='black',
            plot_bgcolor='black',
            geo=dict(bgcolor='black'),
            font=dict(color='white'),
            title=dict(font=dict(color='white'))
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Scatter geo map
        if location_col and 'latitude' in df.columns and 'longitude' in df.columns:
            st.markdown("---")
            st.markdown(f"### 📍 Location-based {map_var} Map")
            
            sample_size = st.slider("Number of locations", 100, 5000, 1000, 100)
            sample_df = df[[location_col, 'latitude', 'longitude', map_var]].dropna().sample(min(sample_size, len(df)))
            
            sample_df['marker_size'] = np.abs(sample_df[map_var] - sample_df[map_var].min()) + 1
            
            fig = px.scatter_geo(
                sample_df,
                lat='latitude',
                lon='longitude',
                color=map_var,
                hover_name=location_col,
                size='marker_size',
                color_continuous_scale='RdYlBu_r' if map_var == temp_col else 'Viridis',
                title=f"{map_var} Distribution by Location",
                projection='natural earth'
            )
            fig.update_geos(
                showcountries=True,
                countrycolor="white",
                showcoastlines=True,
                coastlinecolor="white",
                bgcolor="black",
                showland=True,
                landcolor="rgba(50, 50, 50, 0.8)",
                showocean=True,
                oceancolor="black",
                showlakes=True,
                lakecolor="black"
            )
            fig.update_layout(
                height=500,
                paper_bgcolor='black',
                plot_bgcolor='black',
                geo=dict(bgcolor='black'),
                font=dict(color='white'),
                title=dict(font=dict(color='white'))
            )
            st.plotly_chart(fig, use_container_width=True)
            
# TAB 9: HUMIDITY ANALYSIS

with tab9:
    st.markdown("## 💧 Humidity Analysis")
    st.markdown("Comprehensive humidity patterns and moisture analysis")
    st.markdown("")
    
    if humidity_col:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_hum = df[humidity_col].mean()
            st.metric("💧 Average Humidity", f"{avg_hum:.1f}%")
        
        with col2:
            max_hum = df[humidity_col].max()
            st.metric("📈 Maximum", f"{max_hum:.1f}%")
        
        with col3:
            min_hum = df[humidity_col].min()
            st.metric("📉 Minimum", f"{min_hum:.1f}%")
        
        with col4:
            std_hum = df[humidity_col].std()
            st.metric("📊 Std Dev", f"{std_hum:.1f}%")
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Humidity Distribution")
            fig = px.histogram(
                df, x=humidity_col,
                nbins=50,
                marginal="box",
                color_discrete_sequence=['#4ECDC4'],
                title="Humidity Distribution with Box Plot"
            )
            fig.add_vline(x=avg_hum, line_dash="dash", line_color="red",
                         annotation_text=f"Mean: {avg_hum:.1f}%")
            fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if temp_col:
                st.markdown("### 🌡️ Humidity vs Temperature")
                sample_df = df[[temp_col, humidity_col]].dropna().sample(min(5000, len(df)))
                fig = px.scatter(
                    sample_df,
                    x=temp_col,
                    y=humidity_col,
                    trendline="lowess",
                    color=humidity_col,
                    color_continuous_scale='Blues',
                    opacity=0.6
                )
                fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        
        # Time series
        if date_col:
            st.markdown("---")
            st.markdown("### 📅 Humidity Over Time")
            
            df_hum = df[[date_col, humidity_col]].dropna()
            df_hum = df_hum.set_index(date_col)
            daily_hum = df_hum.resample('D').mean().dropna()
            
            if len(daily_hum) > 1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=daily_hum.index,
                    y=daily_hum.values.flatten(),
                    mode='lines',
                    fill='tozeroy',
                    fillcolor='rgba(78, 205, 196, 0.15)',
                    line=dict(color='#4ECDC4', width=2.5)
                ))
                
                fig.update_layout(
                    title="Daily Average Humidity Trend",
                    xaxis_title="Date",
                    yaxis_title="Humidity (%)",
                    height=400,
                    plot_bgcolor='white',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # By country
        if country_col:
            st.markdown("---")
            st.markdown("### 🌍 Humidity by Country")
            
            top_countries = df[country_col].value_counts().head(15).index
            fig = px.box(
                df[df[country_col].isin(top_countries)],
                x=country_col,
                y=humidity_col,
                color=country_col,
                title="Humidity Distribution by Top 15 Countries"
            )
            fig.update_xaxes(tickangle=-45)
            fig.update_layout(height=500, showlegend=False, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Humidity data not available in the dataset.")

# TAB 10: WIND & PRESSURE ANALYSIS

with tab10:
    st.markdown("## 💨 Wind & Pressure Analysis")
    st.markdown("Atmospheric pressure and wind patterns")
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    # Wind Analysis
    with col1:
        if wind_col:
            st.markdown("### 💨 Wind Speed Analysis")
            
            wind_metrics = st.columns(3)
            with wind_metrics[0]:
                st.metric("Average", f"{df[wind_col].mean():.1f} kph")
            with wind_metrics[1]:
                st.metric("Maximum", f"{df[wind_col].max():.1f} kph")
            with wind_metrics[2]:
                st.metric("Std Dev", f"{df[wind_col].std():.1f} kph")
            
            # Wind distribution
            fig = px.histogram(
                df, x=wind_col,
                nbins=50,
                marginal="violin",
                color_discrete_sequence=['#95a5a6']
            )
            fig.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Wind direction
            if 'wind_direction' in df.columns:
                st.markdown("#### 🧭 Wind Direction Distribution")
                wind_dir_counts = df['wind_direction'].value_counts().head(8)
                fig = px.bar(
                    x=wind_dir_counts.index,
                    y=wind_dir_counts.values,
                    color=wind_dir_counts.values,
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    xaxis_title="Direction",
                    yaxis_title="Frequency",
                    height=300,
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Pressure Analysis
    with col2:
        if pressure_col:
            st.markdown("### 🔽 Atmospheric Pressure")
            
            pres_metrics = st.columns(3)
            with pres_metrics[0]:
                st.metric("Average", f"{df[pressure_col].mean():.1f} mb")
            with pres_metrics[1]:
                st.metric("Maximum", f"{df[pressure_col].max():.1f} mb")
            with pres_metrics[2]:
                st.metric("Std Dev", f"{df[pressure_col].std():.1f} mb")
            
            # Pressure distribution
            fig = px.histogram(
                df, x=pressure_col,
                nbins=50,
                marginal="box",
                color_discrete_sequence=['#3498db']
            )
            fig.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Pressure categories
            st.markdown("#### 📊 Pressure Categories")
            df_temp = df.copy()
            df_temp['pressure_category'] = pd.cut(
                df_temp[pressure_col],
                bins=[0, 1000, 1013, 1020, 2000],
                labels=['Low', 'Below Normal', 'Normal', 'High']
            )
            cat_counts = df_temp['pressure_category'].value_counts()
            fig = px.pie(
                values=cat_counts.values,
                names=cat_counts.index,
                color_discrete_sequence=['#e74c3c', '#f39c12', '#2ecc71', '#3498db']
            )
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    # Combined analysis
    if wind_col and pressure_col:
        st.markdown("---")
        st.markdown("### 🔄 Wind-Pressure Relationship")
        
        sample_df = df[[wind_col, pressure_col]].dropna().sample(min(5000, len(df)))
        fig = px.scatter(
            sample_df,
            x=pressure_col,
            y=wind_col,
            trendline="ols",
            color=wind_col,
            color_continuous_scale='Turbo',
            opacity=0.6
        )
        fig.update_layout(
            title="Correlation between Pressure and Wind Speed",
            height=450,
            plot_bgcolor='white',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

# TAB 11: UV & VISIBILITY

with tab11:
    st.markdown("## ☀️ UV Index & Visibility Analysis")
    st.markdown("Solar radiation and atmospheric visibility patterns")
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    # UV Index Analysis
    with col1:
        if 'uv_index' in df.columns:
            st.markdown("### ☀️ UV Index Analysis")
            
            uv_metrics = st.columns(3)
            with uv_metrics[0]:
                st.metric("Average UV", f"{df['uv_index'].mean():.1f}")
            with uv_metrics[1]:
                st.metric("Maximum", f"{df['uv_index'].max():.1f}")
            with uv_metrics[2]:
                high_uv = len(df[df['uv_index'] > 6])
                st.metric("High UV Days", f"{high_uv:,}")
            
            # UV distribution
            fig = px.histogram(
                df, x='uv_index',
                nbins=30,
                marginal="box",
                color_discrete_sequence=['#FF6B6B']
            )
            fig.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            # UV categories
            st.markdown("#### 📊 UV Risk Categories")
            df_temp = df.copy()
            df_temp['uv_category'] = pd.cut(
                df_temp['uv_index'],
                bins=[0, 2, 5, 7, 10, 100],
                labels=['Low', 'Moderate', 'High', 'Very High', 'Extreme']
            )
            cat_counts = df_temp['uv_category'].value_counts()
            fig = px.bar(
                x=cat_counts.index,
                y=cat_counts.values,
                color=cat_counts.index,
                color_discrete_map={
                    'Low': '#2ecc71',
                    'Moderate': '#f39c12',
                    'High': '#e67e22',
                    'Very High': '#e74c3c',
                    'Extreme': '#8e44ad'
                }
            )
            fig.update_layout(
                xaxis_title="UV Category",
                yaxis_title="Count",
                height=300,
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ UV Index data not available")
    
    # Visibility Analysis
    with col2:
        if 'visibility_km' in df.columns:
            st.markdown("### 👁️ Visibility Analysis")
            
            vis_metrics = st.columns(3)
            with vis_metrics[0]:
                st.metric("Average", f"{df['visibility_km'].mean():.1f} km")
            with vis_metrics[1]:
                st.metric("Maximum", f"{df['visibility_km'].max():.1f} km")
            with vis_metrics[2]:
                poor_vis = len(df[df['visibility_km'] < 5])
                st.metric("Poor Visibility", f"{poor_vis:,}")
            
            # Visibility distribution
            fig = px.histogram(
                df, x='visibility_km',
                nbins=50,
                marginal="violin",
                color_discrete_sequence=['#4ECDC4']
            )
            fig.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Visibility categories
            st.markdown("#### 📊 Visibility Categories")
            df_temp = df.copy()
            df_temp['vis_category'] = pd.cut(
                df_temp['visibility_km'],
                bins=[0, 1, 5, 10, 1000],
                labels=['Very Poor', 'Poor', 'Moderate', 'Good']
            )
            cat_counts = df_temp['vis_category'].value_counts()
            fig = px.pie(
                values=cat_counts.values,
                names=cat_counts.index,
                color_discrete_sequence=['#e74c3c', '#f39c12', '#3498db', '#2ecc71']
            )
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Visibility data not available")
    
    # Combined analysis
    if 'uv_index' in df.columns and 'visibility_km' in df.columns:
        st.markdown("---")
        st.markdown("### 🔄 UV vs Visibility Relationship")
        
        sample_df = df[['uv_index', 'visibility_km']].dropna().sample(min(5000, len(df)))
        fig = px.scatter(
            sample_df,
            x='visibility_km',
            y='uv_index',
            trendline="lowess",
            color='uv_index',
            color_continuous_scale='Sunset',
            opacity=0.6
        )
        fig.update_layout(
            title="Relationship between Visibility and UV Index",
            xaxis_title="Visibility (km)",
            yaxis_title="UV Index",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

# Continue with tabs 12-14...
# TAB 12: CLOUD & WEATHER CONDITIONS

with tab12:
    st.markdown("## ☁️ Cloud Cover & Weather Conditions")
    st.markdown("Cloud patterns and weather condition analysis")
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    # Cloud Analysis
    with col1:
        if 'cloud' in df.columns:
            st.markdown("### ☁️ Cloud Cover Analysis")
            
            cloud_metrics = st.columns(3)
            with cloud_metrics[0]:
                st.metric("Avg Cloud Cover", f"{df['cloud'].mean():.1f}%")
            with cloud_metrics[1]:
                st.metric("Clear Sky", f"{len(df[df['cloud'] < 20]):,}")
            with cloud_metrics[2]:
                st.metric("Overcast", f"{len(df[df['cloud'] > 80]):,}")
            
            # Cloud distribution
            fig = px.histogram(
                df, x='cloud',
                nbins=50,
                marginal="box",
                color_discrete_sequence=['#95a5a6']
            )
            fig.update_layout(
                title="Cloud Cover Distribution",
                height=350,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Cloud categories
            st.markdown("#### 📊 Sky Conditions")
            df_temp = df.copy()
            df_temp['sky_category'] = pd.cut(
                df_temp['cloud'],
                bins=[0, 20, 50, 80, 100],
                labels=['Clear', 'Partly Cloudy', 'Mostly Cloudy', 'Overcast']
            )
            cat_counts = df_temp['sky_category'].value_counts()
            fig = px.bar(
                x=cat_counts.index,
                y=cat_counts.values,
                color=cat_counts.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                xaxis_title="Sky Condition",
                yaxis_title="Count",
                height=300,
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Cloud cover data not available")
    
    # Weather Conditions
    with col2:
        if 'condition_text' in df.columns:
            st.markdown("### 🌤️ Weather Conditions")
            
            condition_counts = df['condition_text'].value_counts().head(10)
            
            st.markdown("#### Top 10 Weather Conditions")
            fig = px.bar(
                x=condition_counts.values,
                y=condition_counts.index,
                orientation='h',
                color=condition_counts.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                xaxis_title="Frequency",
                yaxis_title="",
                height=400,
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Pie chart
            st.markdown("#### Distribution")
            top_5 = df['condition_text'].value_counts().head(5)
            others = df['condition_text'].value_counts()[5:].sum()
            
            pie_data = pd.concat([top_5, pd.Series({'Others': others})])
            fig = px.pie(
                values=pie_data.values,
                names=pie_data.index,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Weather condition data not available")
    
    # Precipitation analysis
    if 'precip_mm' in df.columns:
        st.markdown("---")
        st.markdown("### 🌧️ Precipitation Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Precipitation", f"{df['precip_mm'].sum():.1f} mm")
        
        with col2:
            rainy_days = len(df[df['precip_mm'] > 0])
            st.metric("Rainy Records", f"{rainy_days:,}")
        
        with col3:
            avg_precip = df[df['precip_mm'] > 0]['precip_mm'].mean()
            st.metric("Avg When Raining", f"{avg_precip:.2f} mm")
        
        # Precipitation distribution
        fig = px.histogram(
            df[df['precip_mm'] > 0], x='precip_mm',
            nbins=50,
            marginal="box",
            color_discrete_sequence=['#3498db']
        )
        fig.update_layout(
            title="Precipitation Distribution (Rainy Days Only)",
            xaxis_title="Precipitation (mm)",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

# TAB 13: COMFORT INDEX

with tab13:
    st.markdown("## 🌡️ Human Comfort Index Analysis")
    st.markdown("Feels-like temperature and comfort conditions")
    st.markdown("")
    
    if 'feels_like_celsius' in df.columns and temp_col:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Avg Feels Like", f"{df['feels_like_celsius'].mean():.1f}°C")
        
        with col2:
            st.metric("Avg Actual", f"{df[temp_col].mean():.1f}°C")
        
        with col3:
            diff = (df['feels_like_celsius'] - df[temp_col]).mean()
            st.metric("Avg Difference", f"{diff:.1f}°C")
        
        with col4:
            uncomfortable = len(df[(df['feels_like_celsius'] < 10) | (df['feels_like_celsius'] > 30)])
            st.metric("Uncomfortable", f"{uncomfortable:,}")
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌡️ Feels Like vs Actual Temperature")
            
            sample_df = df[[temp_col, 'feels_like_celsius']].dropna().sample(min(5000, len(df)))
            fig = px.scatter(
                sample_df,
                x=temp_col,
                y='feels_like_celsius',
                trendline="ols",
                color='feels_like_celsius',
                color_continuous_scale='RdYlBu_r',
                opacity=0.6
            )
            
            # Add y=x line
            min_val = min(sample_df[temp_col].min(), sample_df['feels_like_celsius'].min())
            max_val = max(sample_df[temp_col].max(), sample_df['feels_like_celsius'].max())
            fig.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name='y=x (Equal)',
                line=dict(color='red', dash='dash', width=2)
            ))
            
            fig.update_layout(
                xaxis_title="Actual Temperature (°C)",
                yaxis_title="Feels Like (°C)",
                height=450,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Temperature Difference Distribution")
            
            df_temp = df.copy()
            df_temp['temp_diff'] = df_temp['feels_like_celsius'] - df_temp[temp_col]
            
            fig = px.histogram(
                df_temp, x='temp_diff',
                nbins=50,
                marginal="box",
                color_discrete_sequence=['#8e44ad']
            )
            fig.update_layout(
                title="Distribution of Temperature Difference (Feels Like - Actual)",
                xaxis_title="Temperature Difference (°C)",
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Comfort zones
        st.markdown("---")
        st.markdown("### 🎯 Comfort Zone Analysis")
        
        df_comfort = df.copy()
        df_comfort['comfort_zone'] = pd.cut(
            df_comfort['feels_like_celsius'],
            bins=[-100, 10, 18, 26, 35, 100],
            labels=['Too Cold', 'Cool', 'Comfortable', 'Warm', 'Too Hot']
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            comfort_counts = df_comfort['comfort_zone'].value_counts()
            fig = px.pie(
                values=comfort_counts.values,
                names=comfort_counts.index,
                color_discrete_sequence=['#3498db', '#5dade2', '#2ecc71', '#f39c12', '#e74c3c'],
                title="Comfort Zone Distribution"
            )
            fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Comfort by country
            if country_col:
                top_countries = df[country_col].value_counts().head(10).index
                comfort_by_country = df_comfort[df_comfort[country_col].isin(top_countries)].groupby([country_col, 'comfort_zone']).size().unstack(fill_value=0)
                
                fig = px.bar(
                    comfort_by_country.reset_index(),
                    x=country_col,
                    y=['Too Cold', 'Cool', 'Comfortable', 'Warm', 'Too Hot'],
                    title="Comfort Zones by Country",
                    color_discrete_sequence=['#3498db', '#5dade2', '#2ecc71', '#f39c12', '#e74c3c']
                )
                fig.update_xaxes(tickangle=-45)
                fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        
        # Heat Index calculation
        if humidity_col:
            st.markdown("---")
            st.markdown("### 🌡️ Heat Index Analysis")
            
            # Simple heat index approximation
            df_heat = df[[temp_col, humidity_col, 'feels_like_celsius']].dropna()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.scatter(
                    df_heat.sample(min(3000, len(df_heat))),
                    x=humidity_col,
                    y='feels_like_celsius',
                    color=temp_col,
                    color_continuous_scale='RdYlBu_r',
                    title="Feels Like vs Humidity (colored by Temperature)",
                    opacity=0.6
                )
                fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 3D scatter
                fig = px.scatter_3d(
                    df_heat.sample(min(2000, len(df_heat))),
                    x=temp_col,
                    y=humidity_col,
                    z='feels_like_celsius',
                    color='feels_like_celsius',
                    color_continuous_scale='Turbo',
                    title="3D Comfort Index",
                    opacity=0.7
                )
                fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Feels-like temperature data not available in the dataset.")

# TAB 14: ASTRONOMICAL DATA

with tab14:
    st.markdown("## 🌙 Astronomical Data Analysis")
    st.markdown("Sunrise, sunset, moonrise, moonset, and moon phase analysis")
    st.markdown("")
    
    # Check for astronomical columns
    astro_cols = [col for col in df.columns if any(x in col.lower() for x in ['sunrise', 'sunset', 'moonrise', 'moonset', 'moon'])]
    
    if len(astro_cols) > 0:
        st.markdown("### 🌅 Available Astronomical Data")
        st.info(f"📊 Found {len(astro_cols)} astronomical columns: {', '.join(astro_cols)}")
        
        # Sunrise/Sunset Analysis
        if 'sunrise' in df.columns and 'sunset' in df.columns:
            st.markdown("---")
            st.markdown("### ☀️ Daylight Analysis")
            
            df_astro = df.copy()
            
            # Convert to datetime if string
            if df_astro['sunrise'].dtype == 'object':
                df_astro['sunrise_time'] = pd.to_datetime(df_astro['sunrise'], format='%I:%M %p', errors='coerce')
                df_astro['sunset_time'] = pd.to_datetime(df_astro['sunset'], format='%I:%M %p', errors='coerce')
            else:
                df_astro['sunrise_time'] = pd.to_datetime(df_astro['sunrise'], errors='coerce')
                df_astro['sunset_time'] = pd.to_datetime(df_astro['sunset'], errors='coerce')
            
            # Calculate daylight hours
            df_astro['daylight_hours'] = (df_astro['sunset_time'] - df_astro['sunrise_time']).dt.total_seconds() / 3600
            
            if df_astro['daylight_hours'].notna().sum() > 0:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_daylight = df_astro['daylight_hours'].mean()
                    st.metric("Avg Daylight", f"{avg_daylight:.1f} hrs")
                
                with col2:
                    max_daylight = df_astro['daylight_hours'].max()
                    st.metric("Maximum", f"{max_daylight:.1f} hrs")
                
                with col3:
                    min_daylight = df_astro['daylight_hours'].min()
                    st.metric("Minimum", f"{min_daylight:.1f} hrs")
                
                with col4:
                    std_daylight = df_astro['daylight_hours'].std()
                    st.metric("Std Dev", f"{std_daylight:.1f} hrs")
                
                # Visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.histogram(
                        df_astro[df_astro['daylight_hours'].notna()],
                        x='daylight_hours',
                        nbins=50,
                        marginal="box",
                        color_discrete_sequence=['#f39c12'],
                        title="Daylight Hours Distribution"
                    )
                    fig.add_vline(x=avg_daylight, line_dash="dash", line_color="red",
                                 annotation_text=f"Mean: {avg_daylight:.1f}h")
                    fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if country_col:
                        top_countries = df[country_col].value_counts().head(10).index
                        fig = px.box(
                            df_astro[df_astro[country_col].isin(top_countries)],
                            x=country_col,
                            y='daylight_hours',
                            color=country_col,
                            title="Daylight Hours by Country"
                        )
                        fig.update_xaxes(tickangle=-45)
                        fig.update_layout(height=400, showlegend=False, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig, use_container_width=True)
                
                # Time series
                if date_col:
                    st.markdown("---")
                    st.markdown("### 📅 Daylight Hours Over Time")
                    
                    df_daylight = df_astro[[date_col, 'daylight_hours']].dropna()
                    df_daylight = df_daylight.set_index(date_col).resample('D').mean().dropna()
                    
                    if len(df_daylight) > 1:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df_daylight.index,
                            y=df_daylight['daylight_hours'],
                            mode='lines',
                            fill='tozeroy',
                            fillcolor='rgba(243, 156, 18, 0.2)',
                            line=dict(color='#f39c12', width=3),
                            name='Daylight Hours'
                        ))
                        
                        fig.update_layout(
                            title="Daily Daylight Hours Trend",
                            xaxis_title="Date",
                            yaxis_title="Hours",
                            height=400,
                            plot_bgcolor='white',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        # Moon Phase Analysis
        if 'moon_phase' in df.columns:
            st.markdown("---")
            st.markdown("### 🌙 Moon Phase Analysis")
            
            moon_counts = df['moon_phase'].value_counts().head(10)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    x=moon_counts.index,
                    y=moon_counts.values,
                    color=moon_counts.values,
                    color_continuous_scale='Bluyl',
                    title="Moon Phase Distribution"
                )
                fig.update_xaxes(tickangle=-45)
                fig.update_layout(height=400, showlegend=False, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.pie(
                    values=moon_counts.values,
                    names=moon_counts.index,
                    title="Moon Phase Proportion",
                    color_discrete_sequence=px.colors.sequential.Bluyl
                )
                fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        
        # Moon Illumination
        if 'moon_illumination' in df.columns:
            st.markdown("---")
            st.markdown("### 🌕 Moon Illumination")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_illum = df['moon_illumination'].mean()
                st.metric("Avg Illumination", f"{avg_illum:.1f}%")
            
            with col2:
                full_moon = len(df[df['moon_illumination'] > 95])
                st.metric("Full Moon Days", f"{full_moon:,}")
            
            with col3:
                new_moon = len(df[df['moon_illumination'] < 5])
                st.metric("New Moon Days", f"{new_moon:,}")
            
            with col4:
                std_illum = df['moon_illumination'].std()
                st.metric("Variability", f"{std_illum:.1f}%")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.histogram(
                    df,
                    x='moon_illumination',
                    nbins=50,
                    marginal="violin",
                    color_discrete_sequence=['#9b59b6'],
                    title="Moon Illumination Distribution"
                )
                fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if date_col:
                    df_moon = df[[date_col, 'moon_illumination']].dropna()
                    df_moon = df_moon.set_index(date_col).resample('D').mean().dropna()
                    
                    if len(df_moon) > 1:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df_moon.index,
                            y=df_moon['moon_illumination'],
                            mode='lines+markers',
                            line=dict(color='#9b59b6', width=2),
                            marker=dict(size=6),
                            name='Illumination'
                        ))
                        
                        fig.update_layout(
                            title="Moon Illumination Over Time",
                            xaxis_title="Date",
                            yaxis_title="Illumination (%)",
                            height=400,
                            plot_bgcolor='white',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        # Moonrise/Moonset
        if 'moonrise' in df.columns and 'moonset' in df.columns:
            st.markdown("---")
            st.markdown("### 🌛 Moonrise & Moonset Patterns")
            
            st.info("📊 Moonrise and moonset times available in dataset")
            
            # Display sample data
            moon_data = df[['moonrise', 'moonset']].dropna().head(20)
            if len(moon_data) > 0:
                st.dataframe(moon_data, use_container_width=True)
        
        # Astronomical events correlation
        if temp_col and 'moon_illumination' in df.columns:
            st.markdown("---")
            st.markdown("### 🔗 Temperature vs Moon Illumination")
            
            sample_df = df[[temp_col, 'moon_illumination']].dropna().sample(min(5000, len(df)))
            
            fig = px.scatter(
                sample_df,
                x='moon_illumination',
                y=temp_col,
                trendline="lowess",
                color=temp_col,
                color_continuous_scale='RdYlBu_r',
                opacity=0.6,
                title="Exploring Temperature-Moon Correlation"
            )
            fig.update_layout(height=450, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate correlation
            corr = sample_df[temp_col].corr(sample_df['moon_illumination'])
            
            if abs(corr) < 0.1:
                st.success(f"✅ No significant correlation found (r = {corr:.3f}). Temperature and moon illumination are independent.")
            elif abs(corr) < 0.3:
                st.info(f"ℹ️ Weak correlation detected (r = {corr:.3f}). Minimal relationship between temperature and moon phase.")
            else:
                st.warning(f"⚠️ Moderate correlation found (r = {corr:.3f}). Interesting pattern detected!")
    
    else:
        st.warning("⚠️ No astronomical data columns found in the dataset.")
        st.info("💡 Astronomical data typically includes: sunrise, sunset, moonrise, moonset, moon phase, and moon illumination.")

# EXPORT SECTION

st.markdown("---")
st.markdown("## 💾 Export Data & Reports")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 Statistics", use_container_width=True):
        stats = df.select_dtypes(include=[np.number]).describe()
        csv = stats.to_csv()
        st.download_button(
            "📥 Download",
            csv,
            f"statistics_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv",
            use_container_width=True
        )

with col2:
    if st.button("🔥 Extremes", use_container_width=True):
        if 'extreme_results' in locals():
            all_ext = pd.concat([
                extreme_results.get('Temperature', {}).get('high_data', pd.DataFrame()),
                extreme_results.get('Temperature', {}).get('low_data', pd.DataFrame())
            ])
            if len(all_ext) > 0:
                csv = all_ext.to_csv(index=False)
                st.download_button(
                    "📥 Download",
                    csv,
                    f"extremes_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv",
                    use_container_width=True
                )

with col3:
    if st.button("🌍 Regional", use_container_width=True):
        if country_col and temp_col:
            stats = df.groupby(country_col).agg({
                temp_col: ['mean', 'std', 'min', 'max']
            }).reset_index()
            csv = stats.to_csv(index=False)
            st.download_button(
                "📥 Download",
                csv,
                f"regional_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv",
                use_container_width=True
            )

with col4:
    if st.button("📋 Full Data", use_container_width=True):
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download",
            csv,
            f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv",
            use_container_width=True
        )

# DOCUMENTATION

with st.expander("📚 Documentation & Help"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Quick Start Guide
        
        1. **Use the sidebar** to apply filters (date, country, temperature)
        2. **Navigate tabs** to access different analysis modules
        3. **Hover over charts** for detailed information
        4. **Export results** using the buttons above
        
        ### 🔍 Key Features
        
        - **Real-time filtering** with instant updates
        - **Interactive visualizations** with zoom/pan
        - **Statistical analysis** with confidence intervals
        - **Extreme event detection** using z-score method
        - **Geographic mapping** with multiple projections
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Understanding Metrics
        
        **Temperature Metrics:**
        - Measured in Celsius (°C)
        - Global average typically 15-20°C
        
        **Wind Speed:**
        - Measured in kilometers per hour (kph)
        - Average ranges 10-30 kph
        
        **Extreme Events:**
        - Detected using statistical thresholds
        - 3σ = 99.7% confidence level
        
        ### 💡 Pro Tips
        
        - Use "Daily" aggregation for detailed time series
        - Adjust extreme event threshold for sensitivity
        - Compare multiple countries in Regional Intelligence
        """)

# FOOTER

st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; color: white; box-shadow: 0 10px 20px rgba(0,0,0,0.1);'>
        <h2 style='color: white; margin: 0;'>🌍 ClimateScope</h2>
        <h4 style='color: white; margin-top: 10px;'>Weather Intelligence Platform</h4>
        <p style='margin-top: 20px;'><strong>Last Updated:</strong> {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        <p><strong>Active Records:</strong> {len(df):,} | <strong>Countries:</strong> {df[country_col].nunique() if country_col else 'N/A'} | <strong>Locations:</strong> {df[location_col].nunique() if location_col else 'N/A'}</p>
        <div style='margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;'>
            <p style='margin: 5px 0; font-size: 0.9em;'>✅ Real-time Analytics | 📊 Advanced Statistics | 🔥 Extreme Event Detection</p>
            <p style='margin: 5px 0; font-size: 0.9em;'>🌐 Regional Intelligence | 📅 Time Series Analysis | 🗺️ Geographic Mapping</p>
        </div>
        <p style='margin-top: 20px; font-size: 0.85em; opacity: 0.9;'>Powered by Streamlit • Plotly • Pandas • NumPy</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 10px; margin-top: 20px;'>
        <p style='color: #6c757d; margin: 0; font-size: 0.9em;'>
            <strong>ClimateScope</strong> | Weather Analytics Platform
        </p>
        <p style='color: #adb5bd; margin: 5px 0; font-size: 0.8em;'>
            © 2024 ClimateScope | All Rights Reserved | Empowering Climate Intelligence
        </p>
    </div>
""", unsafe_allow_html=True)
