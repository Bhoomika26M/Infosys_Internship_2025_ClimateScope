"""
ClimateScope - Weather Analytics Platform
Advanced Features: ML Predictions, Real-time Analysis, Comprehensive Insights

🔧 BUILT-IN DIAGNOSTIC TOOLS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run these commands in Python/Terminal to troubleshoot Kaggle:

  # Show setup instructions
  from task4 import show_kaggle_setup_instructions
  show_kaggle_setup_instructions()

  # Run diagnostic check
  from task4 import diagnose_kaggle_setup
  diagnose_kaggle_setup()

  # Quick auth test
  from kaggle.api.kaggle_api_extended import KaggleApi
  api = KaggleApi()
  api.authenticate()
  print("✅ Kaggle ready!")

📂 DATA LOADING STRATEGY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Priority order:
  1. Try Kaggle API (fresh data) if credentials exist
  2. Fall back to local global_weather_cleaned.csv
  3. Show error if both fail

"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from scipy import stats
from scipy.stats import pearsonr, spearmanr
from datetime import datetime, timedelta
import warnings
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import json
import os

warnings.filterwarnings('ignore')

# COMPLETE KAGGLE API SETUP & DIAGNOSTIC TOOLS

# This section contains everything needed for Kaggle integration:
# - Credential checking
# - Authentication handling
# - Data fetching with fallback
# - Built-in diagnostic functions

def setup_kaggle_credentials():
    """
    Return True if a local Kaggle credential file exists.
    Expected path: ~/.kaggle/kaggle (1).json (or equivalent on Windows). The
    existence check is sufficient here; actual authentication is performed by
    the Kaggle client during the download step.
    """
    kaggle_json_path = os.path.expanduser('~/.kaggle/kaggle (1).json')
    return os.path.exists(kaggle_json_path)

# Check credentials on app start so callers can decide whether to attempt a
# Kaggle download or fall back to a packaged CSV.

credentials_setup = setup_kaggle_credentials()


# ----------------------- KAGGLE DATA FETCHING (OPTIONAL) -----------------
def download_and_load_from_kaggle():
    """
    Download and load dataset directly from the Kaggle API.
    This function is intended for deployments where Kaggle credentials are
    available (e.g., Streamlit Cloud secrets). It downloads the dataset to a
    temporary directory, unzips it, loads the first CSV found, preprocesses
    it and returns the DataFrame along with a success flag and a user-facing
    message describing the result.
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        import tempfile
        import shutil
        
        # Setup Kaggle API
        api = KaggleApi()
        api.authenticate()
        
        # Create temporary directory (auto-cleanup)
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Download dataset
            with st.spinner("📥 Downloading latest data from Kaggle..."):
                api.dataset_download_files(
                    'nelgiriyewithana/global-weather-repository',
                    path=temp_dir,
                    unzip=True
                )
            
            # Find and load the CSV file
            csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]
            
            if not csv_files:
                raise FileNotFoundError("No CSV files found in downloaded dataset")
            
            csv_path = os.path.join(temp_dir, csv_files[0])
            
            # Load the data
            with st.spinner("📊 Processing fresh dataset..."):
                df = pd.read_csv(csv_path)
                
                # Get file modification time to show dataset freshness
                dataset_date = datetime.fromtimestamp(os.path.getmtime(csv_path))
                
                # Preprocess data
                df = preprocess_data(df)
            
            return df, True#, f"✅ Loaded {len(df):,} records | Dataset updated: {dataset_date.strftime('%Y-%m-%d %H:%M')}"
            
        finally:
            # Always cleanup temp directory
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
        
    except Exception as e:
        error_msg = str(e)
        
        # Provide specific error messages
        if "Could not find kaggle.json" in error_msg or "OSError" in error_msg:
            return None, False, """
❌ **Kaggle API credentials not found!**

**To fix this for deployment:**

### For Streamlit Cloud:
1. Go to your app settings on Streamlit Cloud
2. Click on "Secrets" in the left sidebar
3. Add your Kaggle credentials in TOML format:
```toml
[kaggle]
username = "your_kaggle_username"
key = "your_kaggle_api_key"
```

### For local development:
1. Get your API token from kaggle.com/settings
2. Create `~/.kaggle/kaggle.json` (Linux/Mac) or `C:\\Users\\<username>\\.kaggle\\kaggle.json` (Windows)
3. Add your credentials:
```json
{"username":"your_username","key":"your_api_key"}
```
4. Run: `chmod 600 ~/.kaggle/kaggle.json` (Linux/Mac only)

**Get your API key:** https://www.kaggle.com/settings
"""
        elif "403" in error_msg or "Forbidden" in error_msg:
            return None, False, """
❌ **Access Denied to Kaggle Dataset**

Please ensure:
1. Your Kaggle API credentials are correct
2. You've accepted the dataset's terms at: https://www.kaggle.com/datasets/nelgiriyewithana/global-weather-repository
3. Your Kaggle account is verified
"""
        else:
            return None, False, f"❌ Error downloading from Kaggle: {error_msg}"

def preprocess_data(df):
    """Clean and preprocess the raw dataset"""
    
    # Convert date/time columns
    if 'last_updated' in df.columns:
        df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')
    
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    for col in date_cols:
        if col != 'last_updated_epoch':
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except:
                pass
    
    # Handle missing values for numerical columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            
            if missing_pct < 5:
                df[col] = df[col].interpolate(method='linear', limit_direction='both')
            elif missing_pct < 30:
                df[col].fillna(df[col].median(), inplace=True)
    
    # Handle missing values for categorical columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df[col].isnull().sum() > 0:
            mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown'
            df[col].fillna(mode_val, inplace=True)
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Normalize column names
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    return df


# ========================= BUILT-IN DIAGNOSTIC TOOLS =========================
# These functions help troubleshoot Kaggle API issues embedded in task4.py

def diagnose_kaggle_setup():
    """Built-in diagnostic: Check Kaggle credentials and configuration"""
    print("\n" + "="*60)
    print("🔍 KAGGLE API DIAGNOSTIC")
    print("="*60)
    
    # Check 1: kaggle.json exists
    kaggle_path = os.path.expanduser('~/.kaggle/kaggle.json')
    print(f"\n1️⃣  Checking for kaggle.json...")
    print(f"   Path: {kaggle_path}")
    
    if os.path.exists(kaggle_path):
        print("   ✅ FOUND")
        try:
            with open(kaggle_path) as f:
                import json
                creds = json.load(f)
            if 'username' in creds and 'key' in creds:
                print(f"   ✅ Valid format (username: {creds['username']})")
            else:
                print("   ❌ Invalid format: missing 'username' or 'key'")
        except json.JSONDecodeError:
            print("   ❌ Invalid JSON format")
    else:
        print("   ❌ NOT FOUND")
        print("   📝 Create: ~/.kaggle/kaggle.json with format:")
        print('      {"username":"your_user","key":"your_key"}')
    
    # Check 2: kaggle package
    print(f"\n2️⃣  Checking for kaggle package...")
    try:
        from kaggle import __version__
        print(f"   ✅ Installed (version: {__version__})")
    except ImportError:
        print("   ❌ NOT installed")
        print("   📝 Run: pip install kaggle")
    
    # Check 3: Can authenticate
    print(f"\n3️⃣  Attempting authentication...")
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        print("   ✅ Authentication successful!")
    except Exception as e:
        print(f"   ❌ Authentication failed: {str(e)[:100]}")
    
    print("\n" + "="*60 + "\n")


def show_kaggle_setup_instructions():
    """Built-in instructions: How to set up Kaggle API"""
    instructions = """
╔════════════════════════════════════════════════════════════════╗
║          KAGGLE API SETUP INSTRUCTIONS (Built-in)              ║
╚════════════════════════════════════════════════════════════════╝

STEP 1: Get your Kaggle API credentials
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Go to: https://www.kaggle.com/settings/account
  2. Scroll down to "API" section
  3. Click "Create New API Token"
  4. A file called kaggle.json will download

STEP 2: Save to the correct location
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Windows:  C:\\Users\\<YourUsername>\\.kaggle\\kaggle.json
  Mac/Linux: ~/.kaggle/kaggle.json

STEP 3: Set permissions (Mac/Linux only)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  chmod 600 ~/.kaggle/kaggle.json

STEP 4: Run diagnostic to verify
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  In Python/Terminal:
  from task4 import diagnose_kaggle_setup
  diagnose_kaggle_setup()

QUICK TEST in Python:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  from kaggle.api.kaggle_api_extended import KaggleApi
  api = KaggleApi()
  api.authenticate()
  print("✅ Kaggle is ready!")

FALLBACK: If Kaggle fails
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ClimateScope will automatically use local CSV if:
  • Place global_weather_cleaned.csv in app directory
  • Kaggle API fails for any reason
"""
    print(instructions)


# --------------------------- PAGE CONFIGURATION ---------------------------
# Configure Streamlit's page parameters (title, icon, layout). Keep this
# near the top so the page settings apply before elements are rendered.

st.set_page_config(
    page_title="ClimateScope",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- PREMIUM CSS STYLING (THEME & LAYOUT) ------------------
# Custom CSS injected into the Streamlit page to provide a dark, polished
# theme, custom fonts, and improved layout for tabs, cards, and charts. The
# styles below affect both the main canvas and the sidebar. Modify carefully
# — these styles rely on Streamlit's DOM structure and data attributes.

st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap');
    
    /* ======================== GLOBAL STYLES ======================== */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        padding: 0rem 1rem;
        background: #0d1117;
        color: #e6edf3;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* ======================== TOP NAVIGATION BAR ======================== */
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
    
    /* ======================== ENHANCED TAB STYLING ======================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #161b22;
        padding: 10px 15px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        overflow-x: auto;
        display: flex;
        flex-wrap: wrap;
    }

    .stTabs [data-baseweb="tab"] {
        height: 60px;
        min-width: 150px;
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        border-radius: 12px;
        padding: 12px 20px;
        font-weight: 600;
        color: #e6edf3;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* ======================== SECTION HEADERS ======================== */
    h1, h2, h3, h4 {
        color: #e6edf3;
        font-weight: 700;
    }
    
    h2 {
        font-size: 1.8rem;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    /* ======================== INTERPRETATION BOX ======================== */
    .interpretation-box {
        background: linear-gradient(135deg, #1a4d2e 0%, #0f3d1e 100%);
        border-left: 5px solid #4caf50;
        padding: 1.2rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #a8e6a1;
    }
    
    .interpretation-box h4 {
        color: #4caf50;
        margin: 0 0 0.8rem 0;
        font-size: 1.15rem;
        font-weight: 700;
    }
    
    .interpretation-box p {
        margin: 0.4rem 0;
        line-height: 1.7;
        font-size: 0.95rem;
        color: #c9d1d9;
    }
    
    /* ======================== METRIC CARDS ======================== */
    .metric-card {
        background: #161b22;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
    }
    
    .stMetric {
        background: #161b22;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .stMetric label {
        color: #8b949e !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #e6edf3 !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
    }
    
    /* ======================== INSIGHT CARDS ======================== */
    .insight-card {
        background: linear-gradient(135deg, #161b22 0%, #1f2937 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        margin: 1rem 0;
        border-left: 5px solid #3498db;
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        box-shadow: 0 8px 24px rgba(52, 152, 219, 0.4);
        transform: translateX(5px);
    }
    
    .insight-card h3 {
        color: #e6edf3;
        margin-bottom: 0.5rem;
        font-size: 1.3rem;
    }
    
    .insight-card p {
        color: #c9d1d9;
        line-height: 1.6;
        margin: 0;
    }
    
    /* ======================== ALERT BOXES ======================== */
    .alert-info {
        background: linear-gradient(135deg, #0d3d56 0%, #082d42 100%);
        border-left: 5px solid #17a2b8;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #9ddff8;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #1a4d2e 0%, #0f3d1e 100%);
        border-left: 5px solid #28a745;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #a8e6a1;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #4d3d0a 0%, #3d2d05 100%);
        border-left: 5px solid #ffc107;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #ffeaa7;
    }
    
    .alert-danger {
        background: linear-gradient(135deg, #4d1a1a 0%, #3d0f0f 100%);
        border-left: 5px solid #dc3545;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #f8a1a8;
    }
    
    /* ======================== BUTTONS ======================== */
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
    
    /* ======================== SIDEBAR ENHANCED ======================== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #e6edf3 !important;
    }
    
    /* Fixed: Search box visibility */
    [data-testid="stSidebar"] input[type="text"] {
        background: #0d1117 !important;
        color: #e6edf3 !important;
        border: 2px solid #30363d !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] input[type="text"]::placeholder {
        color: #8b949e !important;
        opacity: 1 !important;
    }
    
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] select {
        background: #0d1117 !important;
        color: #e6edf3 !important;
        border: 2px solid #30363d !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] div {
        color: #e6edf3 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background: rgba(102, 126, 234, 0.3) !important;
        color: #e6edf3 !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%) !important;
        color: #FFFFFF !important;
        border: 3px solid rgba(139, 92, 246, 0.3) !important;
        font-weight: 700 !important;
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4) !important;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: linear-gradient(135deg, #A78BFA 0%, #F472B6 100%) !important;
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.6) !important;
    }
    
    /* ======================== DATAFRAMES ======================== */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        background: #161b22;
        color: #e6edf3;
    }
    
    /* ======================== PLOTLY CHARTS ======================== */
    .js-plotly-plot {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* ======================== EXPANDERS ======================== */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        border-radius: 10px;
        font-weight: 600;
        color: #e6edf3;
        padding: 1rem;
    }
    
    /* ======================== CUSTOM SCROLLBAR ======================== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #161b22;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* ======================== RESPONSIVE DESIGN ======================== */
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
            display: none;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px;
            font-size: 0.85rem;
            min-width: 120px;
        }
    }
    </style>
""", unsafe_allow_html=True)


# --------------------------- UTILITY FUNCTIONS ---------------------------
# Small reusable helpers used across multiple tabs and analyses. These
# functions encapsulate common tasks (interpretation panel, extreme event
# detection, health metrics, etc.) so the UI code stays concise and focused on
# layout/visualization.

def add_interpretation(title, what_showing, how_to_read, what_means, conclusions):
    """
    Render an interpretation/help box below a visualization.
    Parameters:
    - title: short title for the interpretation
    - what_showing: human readable explanation of what the chart shows
    - how_to_read: guidance for interpreting the chart
    - what_means: numeric meaning/context
    - conclusions: suggested conclusions or applications
    """
    st.markdown(f"""
        <div class='interpretation-box'>
            <h4>💡 {title}</h4>
            <p><strong>📊 What is this chart showing?</strong><br>{what_showing}</p>
            <p><strong>📖 How do I read this?</strong><br>{how_to_read}</p>
            <p><strong>🔢 What does this number mean?</strong><br>{what_means}</p>
            <p><strong>✅ What conclusions can I make from this?</strong><br>{conclusions}</p>
        </div>
    """, unsafe_allow_html=True)

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

def calculate_heat_index(temp, humidity):
    """Calculate heat index (feels like temperature)"""
    try:
        if temp < 27:
            return temp
        
        HI = (
            -8.78469475556 + 
            1.61139411 * temp + 
            2.33854883889 * humidity + 
            -0.14611605 * temp * humidity + 
            -0.012308094 * temp**2 + 
            -0.0164248277778 * humidity**2 + 
            0.002211732 * temp**2 * humidity + 
            0.00072546 * temp * humidity**2 + 
            -0.000003582 * temp**2 * humidity**2
        )
        return HI
    except:
        return temp

def get_comfort_level(feels_like):
    """Determine comfort level based on feels like temperature"""
    if feels_like < 10:
        return "Too Cold ❄", "#3498db"
    elif feels_like < 18:
        return "Cool 🌤", "#5dade2"
    elif feels_like < 26:
        return "Comfortable ✅", "#2ecc71"
    elif feels_like < 35:
        return "Warm ☀", "#f39c12"
    else:
        return "Too Hot 🔥", "#e74c3c"

def get_uv_category(uv_index):
    """Get UV risk category"""
    if uv_index <= 2:
        return "Low", "#2ecc71"
    elif uv_index <= 5:
        return "Moderate", "#f39c12"
    elif uv_index <= 7:
        return "High", "#e67e22"
    elif uv_index <= 10:
        return "Very High", "#e74c3c"
    else:
        return "Extreme", "#8e44ad"

def get_wind_description(wind_kph):
    """Get wind description based on Beaufort scale"""
    if wind_kph < 1:
        return "Calm", "#95a5a6"
    elif wind_kph < 6:
        return "Light Air", "#3498db"
    elif wind_kph < 12:
        return "Light Breeze", "#2ecc71"
    elif wind_kph < 20:
        return "Gentle Breeze", "#f39c12"
    elif wind_kph < 29:
        return "Moderate Breeze", "#e67e22"
    elif wind_kph < 39:
        return "Fresh Breeze", "#e74c3c"
    elif wind_kph < 50:
        return "Strong Breeze", "#c0392b"
    elif wind_kph < 62:
        return "Near Gale", "#8e44ad"
    elif wind_kph < 75:
        return "Gale", "#6c3483"
    elif wind_kph < 89:
        return "Strong Gale", "#4a235a"
    elif wind_kph < 103:
        return "Storm", "#2c3e50"
    elif wind_kph < 118:
        return "Violent Storm", "#1c2833"
    else:
        return "Hurricane", "#0b0c0d"

def calculate_dewpoint(temp, humidity):
    """Calculate dew point temperature"""
    try:
        a = 17.27
        b = 237.7
        alpha = ((a * temp) / (b + temp)) + np.log(humidity/100.0)
        dewpoint = (b * alpha) / (a - alpha)
        return dewpoint
    except:
        return temp

def get_weather_emoji(condition):
    """Get emoji for weather condition"""
    condition_lower = str(condition).lower()
    if 'clear' in condition_lower or 'sunny' in condition_lower:
        return "☀️"
    elif 'cloud' in condition_lower:
        return "☁️"
    elif 'rain' in condition_lower:
        return "🌧️"
    elif 'snow' in condition_lower:
        return "❄️"
    elif 'storm' in condition_lower or 'thunder' in condition_lower:
        return "⛈️"
    elif 'fog' in condition_lower or 'mist' in condition_lower:
        return "🌫️"
    elif 'wind' in condition_lower:
        return "💨"
    else:
        return "🌤️"
    

# --------------------------- DATA LOADING FUNCTIONS ----------------------
# These functions handle loading the dataset (from local CSV or Kaggle),
# lightweight preprocessing (datetime parsing, deduplication) and column
# identification. Caching is applied via `st.cache_data` to avoid repeated
# expensive I/O during interactive sessions.

@st.cache_data(show_spinner=False)
def load_data():
    """
    Load and preprocess dataset with dual-source strategy.
    
    Priority order:
    1. Try Kaggle API (if credentials exist) for fresh data
    2. Fall back to local 'global_weather_cleaned.csv'
    3. Fail with helpful error if neither is available
    
    Returns a preprocessed DataFrame with normalized column names and
    proper datetime parsing.
    """


    # ATTEMPT 1: Try Kaggle API if credentials detected at startup
    if credentials_setup:
        # st.info("📥 Attempting to load fresh data from Kaggle...")
        df_kaggle, kaggle_success = download_and_load_from_kaggle()
        
        if kaggle_success:
            # st.success(kaggle_msg)
            return df_kaggle
        else:
            # Show Kaggle error but don't stop—try local CSV next
            # st.warning(kaggle_msg)
            st.info("⏮️ Falling back to local CSV file...")
    
    # ATTEMPT 2: Try local CSV as fallback (always)
    try:
        df = pd.read_csv('global_weather_cleaned.csv')
        #st.success("✅ Loaded data from local CSV file")
        
        # Convert last_updated to datetime
        if 'last_updated' in df.columns:
            df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')
        
        # Convert other date columns
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        for col in date_cols:
            if col != 'last_updated_epoch':
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        return df
    except FileNotFoundError:
        st.error("""
❌ **No data source available!**

Both Kaggle and local CSV failed. Please try one of:

1. **Setup Kaggle API (recommended):**
   - Get your API key from https://www.kaggle.com/settings
   - Create `~/.kaggle/kaggle.json` with credentials
   - For Windows: `C:\\Users\\<username>\\.kaggle\\kaggle.json`
   - Format: `{"username":"your_user","key":"your_key"}`

2. **Or place local CSV:**
   - Add `global_weather_cleaned.csv` to the app directory
        """)
        st.stop()
        return None
    except Exception as e:
        st.error(f"❌ **Error loading data:** {str(e)}")
        st.stop()
        return None

@st.cache_data
def identify_columns(df):
    """Intelligently identify key columns in the dataset"""
    
    # Date column - prioritize last_updated
    date_col = None
    if 'last_updated' in df.columns:
        date_col = 'last_updated'
    else:
        date_candidates = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
        if date_candidates:
            date_col = max(date_candidates, key=lambda x: df[x].notna().sum())
    
    # Location column
    location_col = None
    for col in ['location_name', 'name', 'location', 'city']:
        if col in df.columns:
            location_col = col
            break
    
    # Country column
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

# LOAD DATA AND IDENTIFY COLUMNS

with st.spinner('🚀 Loading ClimateScope...'):
    df = load_data()
    
    if df is not None:
        date_col, location_col, country_col, temp_col, wind_col, pressure_col, humidity_col = identify_columns(df)
        # st.success(f'✅ ClimateScope Loaded Successfully! ({len(df):,} records)')
    else:
        st.error("Failed to load data. Please check the instructions above.")
        st.stop()

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


# SIDEBAR CONTROLS - COMPREHENSIVE FILTERING


with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; margin-bottom: 1.5rem; border: 2px solid rgba(102, 126, 234, 0.3);'>
            <h2 style='color: white; margin: 0; font-size: 1.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>
                🎯 Control Center
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # ========== TABLE OF CONTENTS ==========
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1f2937 0%, #111827 100%); 
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem;
                    border: 2px solid #667eea;'>
            <h3 style='color: #667eea; margin: 0 0 1rem 0; text-align: center;'>📑 Table of Contents</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for TOC
    if 'show_filters' not in st.session_state:
        st.session_state.show_filters = True
    
    # Show/Hide Filters Button
    if st.button("🔽 Show Filters" if not st.session_state.show_filters else "🔼 Hide Filters", 
                 use_container_width=True, 
                 key="toggle_filters"):
        st.session_state.show_filters = not st.session_state.show_filters
    
    # Tab navigation buttons
    st.markdown("<h4 style='color: #e6edf3; margin-top: 1rem;'>Quick Navigation:</h4>", unsafe_allow_html=True)
    
    tabs_info = [
        ("📊", "Dashboard"),
        ("📈", "Statistics"),
        ("📉", "Distributions"),
        ("🔥", "Extremes"),
        ("🏙️", "City Analysis"),
        ("📅", "Time Series"),
        ("🔗", "Correlations"),
        ("🗺️", "Maps"),
        ("💧", "Humidity"),
        ("💨", "Wind & Pressure"),
        ("☀️", "UV & Visibility"),
        ("☁️", "Cloud & Weather"),
        ("🤖", "Predictions"),
        ("🌙", "Astronomical"),
        ("😊", "Comfort Index")
    ]
    
    for emoji, name in tabs_info:
        st.markdown(f"""
            <div style='padding: 0.5rem; margin: 0.3rem 0; 
                        background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
                        border-left: 4px solid #667eea; border-radius: 8px;
                        cursor: pointer; transition: all 0.3s ease;'>
                <span style='color: #e6edf3; font-weight: 600;'>{emoji} {name}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color: rgba(102, 126, 234, 0.3); margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    # Initialize session state
    if 'df_original' not in st.session_state:
        st.session_state.df_original = df.copy()
    
    df_filtered = st.session_state.df_original.copy()
    
    # ========== FILTERS (SHOW/HIDE) ==========
    if st.session_state.show_filters:
        st.markdown("<h3 style='color: #667eea; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);'>🔍 Advanced Filters</h3>", unsafe_allow_html=True)
        
        # ========== COUNTRY FILTER (PRIMARY) ==========
        if country_col:
            with st.expander("🌐 Country Filter", expanded=True):
                all_countries = sorted([str(c) for c in df_filtered[country_col].dropna().unique()])
                
                st.markdown("<p style='color: #e6edf3; font-weight: 600;'>Search & Select Countries:</p>", unsafe_allow_html=True)
                search = st.text_input("Search Countries", "", key='country_search', label_visibility="collapsed", 
                                      placeholder="🔍 Type to search countries...")
                
                filtered_countries = [c for c in all_countries if search.lower() in c.lower()] if search else all_countries
                
                selected_countries = st.multiselect(
                    "Select Countries",
                    options=filtered_countries,
                    default=filtered_countries[:3] if len(filtered_countries) <= 5 else [],
                    key='countries',
                    label_visibility="collapsed"
                )
                
                if selected_countries:
                    df_filtered = df_filtered[df_filtered[country_col].isin(selected_countries)]
                    st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    padding: 0.5rem; border-radius: 8px; 
                                    text-align: center; margin-top: 0.5rem; 
                                    border: 1px solid rgba(102, 126, 234, 0.5);'>
                            <p style='color: white; margin: 0; font-weight: 600;'>✅ {len(selected_countries)} countries selected</p>
                        </div>
                    """, unsafe_allow_html=True)
        
        # ========== DATE RANGE FILTER ==========
        if date_col:
            with st.expander("📅 Date Range"):
                df_filtered[date_col] = pd.to_datetime(df_filtered[date_col], errors='coerce')
                min_date = pd.Timestamp(df_filtered[date_col].min())
                max_date = pd.Timestamp(df_filtered[date_col].max())
                
                if pd.notna(min_date) and pd.notna(max_date):
                    st.markdown("<p style='color: #e6edf3; font-weight: 600;'>Select Time Period:</p>", unsafe_allow_html=True)
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
                        df_filtered[date_col] = pd.to_datetime(df_filtered[date_col], errors='coerce')
                        df_filtered = df_filtered[(df_filtered[date_col] >= start_date) & (df_filtered[date_col] < end_date)]
                        
                        days = (end_date - start_date).days
                        st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                        padding: 0.5rem; border-radius: 8px; 
                                        text-align: center; margin-top: 0.5rem;'>
                                <p style='color: white; margin: 0; font-weight: 600;'>✅ {days} days selected</p>
                            </div>
                        """, unsafe_allow_html=True)
        
        # ========== TEMPERATURE FILTER ==========
        if temp_col:
            with st.expander("🌡 Temperature Range"):
                temp_min = float(df_filtered[temp_col].min())
                temp_max = float(df_filtered[temp_col].max())
                
                st.markdown("<p style='color: #e6edf3; font-weight: 600;'>Temperature (°C):</p>", unsafe_allow_html=True)
                temp_range = st.slider(
                    "Temperature Range",
                    temp_min, temp_max,
                    (temp_min, temp_max),
                    key='temp_range',
                    label_visibility="collapsed"
                )
                df_filtered = df_filtered[(df_filtered[temp_col] >= temp_range[0]) & (df_filtered[temp_col] <= temp_range[1])]
                
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 0.5rem; border-radius: 8px; 
                                text-align: center; margin-top: 0.5rem;'>
                        <p style='color: white; margin: 0; font-weight: 600;'>{temp_range[0]:.1f}°C - {temp_range[1]:.1f}°C</p>
                    </div>
                """, unsafe_allow_html=True)
        
        # ========== HUMIDITY FILTER ==========
        if humidity_col:
            with st.expander("💧 Humidity Range"):
                hum_min = float(df_filtered[humidity_col].min())
                hum_max = float(df_filtered[humidity_col].max())
                hum_range = st.slider("Humidity (%)", hum_min, hum_max, (hum_min, hum_max), key='hum_range', label_visibility="collapsed")
                df_filtered = df_filtered[(df_filtered[humidity_col] >= hum_range[0]) & (df_filtered[humidity_col] <= hum_range[1])]
                st.markdown(f"<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.5rem; border-radius: 8px; text-align: center; margin-top: 0.5rem;'><p style='color: white; margin: 0; font-weight: 600;'>{hum_range[0]:.1f}% - {hum_range[1]:.1f}%</p></div>", unsafe_allow_html=True)        
        
        # ========== WIND FILTER ==========
        if wind_col:
            with st.expander("💨 Wind Speed Range"):
                wind_min = float(df_filtered[wind_col].min())
                wind_max = float(df_filtered[wind_col].max())
                wind_range = st.slider("Wind (kph)", wind_min, wind_max, (wind_min, wind_max), key='wind_range', label_visibility="collapsed")
                df_filtered = df_filtered[(df_filtered[wind_col] >= wind_range[0]) & (df_filtered[wind_col] <= wind_range[1])]
                st.markdown(f"<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.5rem; border-radius: 8px; text-align: center; margin-top: 0.5rem;'><p style='color: white; margin: 0; font-weight: 600;'>{wind_range[0]:.1f} - {wind_range[1]:.1f} kph</p></div>", unsafe_allow_html=True)
        
        # ========== PRESSURE FILTER ==========
        if pressure_col:
            with st.expander("🔽 Pressure Range"):
                pres_min = float(df_filtered[pressure_col].min())
                pres_max = float(df_filtered[pressure_col].max())
                pres_range = st.slider("Pressure (mb)", pres_min, pres_max, (pres_min, pres_max), key='pres_range', label_visibility="collapsed")
                df_filtered = df_filtered[(df_filtered[pressure_col] >= pres_range[0]) & (df_filtered[pressure_col] <= pres_range[1])]
                st.markdown(f"<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.5rem; border-radius: 8px; text-align: center; margin-top: 0.5rem;'><p style='color: white; margin: 0; font-weight: 600;'>{pres_range[0]:.1f} - {pres_range[1]:.1f} mb</p></div>", unsafe_allow_html=True)
        
        # ========== UV INDEX FILTER ==========
        if 'uv_index' in df_filtered.columns:
            with st.expander("☀️ UV Index Range"):
                uv_min = float(df_filtered['uv_index'].min())
                uv_max = float(df_filtered['uv_index'].max())
                uv_range = st.slider("UV Index", uv_min, uv_max, (uv_min, uv_max), key='uv_range', label_visibility="collapsed")
                df_filtered = df_filtered[(df_filtered['uv_index'] >= uv_range[0]) & (df_filtered['uv_index'] <= uv_range[1])]
                st.markdown(f"<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.5rem; border-radius: 8px; text-align: center; margin-top: 0.5rem;'><p style='color: white; margin: 0; font-weight: 600;'>{uv_range[0]:.1f} - {uv_range[1]:.1f}</p></div>", unsafe_allow_html=True)
        
        # ========== VISIBILITY FILTER ==========
        if 'visibility_km' in df_filtered.columns:
            with st.expander("👁️ Visibility Range"):
                vis_min = float(df_filtered['visibility_km'].min())
                vis_max = float(df_filtered['visibility_km'].max())
                vis_range = st.slider("Visibility (km)", vis_min, vis_max, (vis_min, vis_max), key='vis_range', label_visibility="collapsed")
                df_filtered = df_filtered[(df_filtered['visibility_km'] >= vis_range[0]) & (df_filtered['visibility_km'] <= vis_range[1])]
                st.markdown(f"<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.5rem; border-radius: 8px; text-align: center; margin-top: 0.5rem;'><p style='color: white; margin: 0; font-weight: 600;'>{vis_range[0]:.1f} - {vis_range[1]:.1f} km</p></div>", unsafe_allow_html=True)
        
        # ========== CLOUD COVER FILTER ==========
        if 'cloud' in df_filtered.columns:
            with st.expander("☁️ Cloud Cover"):
                cloud_min = float(df_filtered['cloud'].min())
                cloud_max = float(df_filtered['cloud'].max())
                cloud_range = st.slider("Cloud (%)", cloud_min, cloud_max, (cloud_min, cloud_max), key='cloud_range', label_visibility="collapsed")
                df_filtered = df_filtered[(df_filtered['cloud'] >= cloud_range[0]) & (df_filtered['cloud'] <= cloud_range[1])]
                st.markdown(f"<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.5rem; border-radius: 8px; text-align: center; margin-top: 0.5rem;'><p style='color: white; margin: 0; font-weight: 600;'>{cloud_range[0]:.1f}% - {cloud_range[1]:.1f}%</p></div>", unsafe_allow_html=True)
        
        # ========== WEATHER CONDITIONS FILTER ==========
        if 'condition_text' in df_filtered.columns:
            with st.expander("🌤️ Weather Conditions"):
                all_conditions = sorted([str(c) for c in df_filtered['condition_text'].dropna().unique()])
                selected_conditions = st.multiselect("Conditions", options=all_conditions, default=[], key='conditions', label_visibility="collapsed")
                if selected_conditions:
                    df_filtered = df_filtered[df_filtered['condition_text'].isin(selected_conditions)]
                    st.markdown(f"<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.5rem; border-radius: 8px; text-align: center; margin-top: 0.5rem;'><p style='color: white; margin: 0; font-weight: 600;'>✅ {len(selected_conditions)} conditions</p></div>", unsafe_allow_html=True)
    
    # ========== APPLY FILTERS (OUTSIDE OF IF BLOCK) ==========
    # Apply all filters
    df = df_filtered.copy()
    
    st.markdown("<hr style='border-color: rgba(102, 126, 234, 0.3); margin: 1.5rem 0;'>", unsafe_allow_html=True)

    # Filter Summary
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 10px; 
                    border: 2px solid rgba(102, 126, 234, 0.5); margin-bottom: 1rem;'>
            <h3 style='color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); margin: 0; text-align: center;'>
                📊 Filter Summary
            </h3>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div style='background: #161b22; padding: 1rem; border-radius: 10px; text-align: center;
                        border: 2px solid #30363d;'>
                <p style='color: #8b949e; margin: 0; font-size: 0.9rem;'>Active Records</p>
                <p style='color: #e6edf3; margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;'>{len(df):,}</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if location_col:
            st.markdown(f"""
                <div style='background: #161b22; padding: 1rem; border-radius: 10px; text-align: center;
                            border: 2px solid #30363d;'>
                    <p style='color: #8b949e; margin: 0; font-size: 0.9rem;'>Cities</p>
                    <p style='color: #e6edf3; margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;'>{df[location_col].nunique():,}</p>
                </div>
            """, unsafe_allow_html=True)

    # Reset button
    if st.button("🔄 RESET ALL FILTERS", use_container_width=True, key="reset_btn"):
        for key in list(st.session_state.keys()):
            if key in ['date_range', 'country_search', 'countries', 'temp_range', 'hum_range', 
                       'wind_range', 'pres_range', 'uv_range', 'vis_range', 'cloud_range', 'conditions']:
                del st.session_state[key]
        st.rerun()

# MAIN TABS - ALL 15 TABS

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15 = st.tabs([
    "📊 Dashboard",
    "📈 Statistics", 
    "📉 Distributions",
    "🔥 Extremes",
    "🏙️ City Analysis",
    "📅 Time Series",
    "🔗 Correlations",
    "🗺️ Maps",
    "💧 Humidity",
    "💨 Wind & Pressure",
    "☀️ UV & Visibility",
    "☁️ Cloud & Weather",
    "🤖 Predictions",
    "🌙 Astronomical",
    "😊 Comfort Index"
])

# TAB 1: EXECUTIVE DASHBOARD

with tab1:
    st.markdown("## 📊 Executive Dashboard")
    
    add_interpretation(
        "Dashboard Overview",
        "Quick snapshot of your filtered weather data showing key counts and averages across selected countries and cities.",
        "Each metric card displays a count (how many) or average (typical value). Higher numbers = more data coverage.",
        "These numbers represent: Countries = unique countries, Cities = unique locations, Avg Temp = mean temperature, Avg Wind = mean wind speed.",
        "Use this to verify filters are working. Low city count? Your country filter might be too strict. Numbers look good? Ready to explore detailed analysis!"
    )
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if country_col:
            st.metric("🗺️ Countries", f"{df[country_col].nunique():,}")
    with col2:
        if location_col:
            st.metric("🏙️ Cities", f"{df[location_col].nunique():,}")
    with col3:
        st.metric("📍 Records", f"{len(df):,}")
    with col4:
        if temp_col:
            st.metric("🌡️ Avg Temp", f"{df[temp_col].mean():.1f}°C")
    with col5:
        if wind_col:
            st.metric("💨 Avg Wind", f"{df[wind_col].mean():.1f} kph")
    
    st.markdown("---")
    
    # Visual KPIs with Gauges
    if temp_col and wind_col and humidity_col:
        st.markdown("### 🎯 Performance Indicators")
        col1, col2, col3 = st.columns(3)
        
        with col1:
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
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': temp_avg}
                }
            ))
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
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
                    'threshold': {'line': {'color': "orange", 'width': 4}, 'thickness': 0.75, 'value': wind_avg}
                }
            ))
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
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
                    'threshold': {'line': {'color': "blue", 'width': 4}, 'thickness': 0.75, 'value': hum_avg}
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
    
    # Temperature Trend Overview
    if temp_col and date_col:
        st.markdown("### 📈 Temperature Trend Overview")
        
        df_temp = df[[date_col, temp_col]].dropna()
        
        if len(df_temp) > 0:
            df_temp = df_temp.set_index(date_col)
            daily_temp = df_temp.resample('D').mean().dropna()
            
            if len(daily_temp) > 1:
                fig = go.Figure()
                
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
                    title={'text': "Daily Temperature Trends with Moving Average", 'font': {'size': 20, 'color': '#2c3e50'}},
                    xaxis=dict(title="Date", showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                    yaxis=dict(title="Temperature (°C)", showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                    height=450,
                    hovermode='x unified',
                    plot_bgcolor='white',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_temp = float(daily_temp.mean().iloc[0]) if hasattr(daily_temp.mean(), 'iloc') else float(daily_temp.mean())
                    st.markdown(f"<div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;'><h4 style='color: white; margin: 0;'>Average</h4><p style='font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;'>{avg_temp:.1f}°C</p></div>", unsafe_allow_html=True)
                
                with col2:
                    max_temp = float(daily_temp.max().iloc[0]) if hasattr(daily_temp.max(), 'iloc') else float(daily_temp.max())
                    max_date = daily_temp.idxmax()
                    if hasattr(max_date, 'iloc'):
                        max_date = max_date.iloc[0]
                    st.markdown(f"<div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); border-radius: 10px; color: white;'><h4 style='color: white; margin: 0;'>Maximum</h4><p style='font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;'>{max_temp:.1f}°C</p><p style='font-size: 0.8rem; margin: 0;'>{max_date.strftime('%b %d, %Y')}</p></div>", unsafe_allow_html=True)
                
                with col3:
                    min_temp = float(daily_temp.min().iloc[0]) if hasattr(daily_temp.min(), 'iloc') else float(daily_temp.min())
                    min_date = daily_temp.idxmin()
                    if hasattr(min_date, 'iloc'):
                        min_date = min_date.iloc[0]
                    st.markdown(f"<div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); border-radius: 10px; color: white;'><h4 style='color: white; margin: 0;'>Minimum</h4><p style='font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;'>{min_temp:.1f}°C</p><p style='font-size: 0.8rem; margin: 0;'>{min_date.strftime('%b %d, %Y')}</p></div>", unsafe_allow_html=True)

# TAB 2: STATISTICAL ANALYSIS

with tab2:
    st.markdown("## 📈 Statistical Analysis")
    
    add_interpretation(
        "Statistical Overview",
        "Detailed statistical summary showing mean, standard deviation, min, max, and quartiles for all numeric weather variables.",
        "Each row = one weather variable. Columns show: count (data points), mean (average), std (variability), min/max (extremes), 25%/50%/75% (quartiles).",
        "Mean = typical value, Std = how much it varies, Min/Max = extremes, 50% = median (middle value).",
        "Higher std = more variable weather. Compare means across variables to understand typical conditions. Check min/max to see extremes."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Descriptive Statistics")
        numeric_cols = df.select_dtypes(include=[np.number]).columns[:8]
        stats_df = df[numeric_cols].describe().T.round(2)
        
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
                    <p>No missing values detected in the filtered dataset.</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Distribution Overview
    if temp_col and wind_col:
        st.markdown("#### 📊 Variable Distribution Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Box(y=df[temp_col], name='Temperature', marker_color='#667eea', boxmean='sd'))
            fig.update_layout(title="Temperature Distribution", yaxis_title="Temperature (°C)", height=350, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Box(y=df[wind_col], name='Wind Speed', marker_color='#4ECDC4', boxmean='sd'))
            fig.update_layout(title="Wind Speed Distribution", yaxis_title="Wind Speed (kph)", height=350, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    # Advanced Statistical Tests
    st.markdown("---")
    st.markdown("### 🔬 Advanced Statistical Tests")
    
    if temp_col and humidity_col:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Normality Test
            from scipy.stats import normaltest
            stat, p_value = normaltest(df[temp_col].dropna())
            is_normal = "Yes" if p_value > 0.05 else "No"
            st.markdown(f"""
                <div class='metric-card'>
                    <h4>📊 Normality Test</h4>
                    <p><strong>Variable:</strong> Temperature</p>
                    <p><strong>P-value:</strong> {p_value:.4f}</p>
                    <p><strong>Normal Distribution:</strong> {is_normal}</p>
                    </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Skewness
            skewness = df[temp_col].skew()
            skew_type = "Right-skewed" if skewness > 0 else "Left-skewed" if skewness < 0 else "Symmetric"
            st.markdown(f"""
                <div class='metric-card'>
                    <h4>📐 Skewness Analysis</h4>
                    <p><strong>Variable:</strong> Temperature</p>
                    <p><strong>Skewness:</strong> {skewness:.4f}</p>
                    <p><strong>Type:</strong> {skew_type}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Kurtosis
            kurtosis = df[temp_col].kurtosis()
            kurt_type = "Heavy-tailed" if kurtosis > 0 else "Light-tailed"
            st.markdown(f"""
                <div class='metric-card'>
                    <h4>📏 Kurtosis Analysis</h4>
                    <p><strong>Variable:</strong> Temperature</p>
                    <p><strong>Kurtosis:</strong> {kurtosis:.4f}</p>
                    <p><strong>Type:</strong> {kurt_type}</p>
                </div>
            """, unsafe_allow_html=True)

# TAB 3: DATA DISTRIBUTIONS

with tab3:
    st.markdown("## 📉 Data Distributions")
    
    add_interpretation(
        "Temperature Distribution",
        "Shows how often different temperatures occur - basically a frequency chart of temperature ranges.",
        "Each bar = temperature range. Taller bar = more common. Red line = average. Shape shows if temperatures cluster around one value or spread out.",
        "If most bars are in middle, temperatures are consistent. Spread out bars = highly variable temperatures.",
        "Conclusions: (1) What's the most common temperature? (2) Is temperature consistent or variable? (3) Are there any unusual outliers?"
    )
    
    if temp_col:
        tab_hist, tab_violin, tab_country, tab_radar, tab_scatter = st.tabs([
            "📊 Histogram", "🎻 Violin Plot", "🌍 By Country", "📡 Radar Analysis", "🔬 Scatter Analysis"
        ])
        
        with tab_hist:
            fig = px.histogram(df, x=temp_col, nbins=50, marginal="box", color_discrete_sequence=['#667eea'])
            mean_temp = df[temp_col].mean()
            median_temp = df[temp_col].median()
            fig.add_vline(x=mean_temp, line_dash="dash", line_color="red", annotation_text=f"Mean: {mean_temp:.1f}°C", annotation_position="top")
            fig.add_vline(x=median_temp, line_dash="dot", line_color="green", annotation_text=f"Median: {median_temp:.1f}°C", annotation_position="bottom")
            fig.update_layout(height=500, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)', xaxis_title="Temperature (°C)", yaxis_title="Frequency")
            st.plotly_chart(fig, use_container_width=True)
        
        with tab_violin:
            fig = go.Figure()
            fig.add_trace(go.Violin(y=df[temp_col], name="Temperature", box_visible=True, meanline_visible=True, fillcolor='#667eea', opacity=0.6, line_color='#764ba2'))
            fig.update_layout(title="Temperature Density Distribution", yaxis_title="Temperature (°C)", height=500, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab_country:
            if country_col:
                top_countries = df[country_col].value_counts().head(10).index
                fig = px.box(df[df[country_col].isin(top_countries)], x=country_col, y=temp_col, title="Temperature Distribution by Top 10 Countries", color=country_col, points="outliers")
                fig.update_xaxes(tickangle=-45)
                fig.update_layout(height=500, showlegend=False, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        
        # RADAR CHART ANALYSIS
        with tab_radar:
            st.markdown("### 📡 Multi-Variable Radar Analysis")
            
            if country_col and temp_col and wind_col and humidity_col:
                # Select top countries
                top_countries = df[country_col].value_counts().head(5).index
                
                radar_data = df[df[country_col].isin(top_countries)].groupby(country_col).agg({
                    temp_col: 'mean',
                    wind_col: 'mean',
                    humidity_col: 'mean'
                }).reset_index()
                
                # Normalize data for radar chart (0-100 scale)
                from sklearn.preprocessing import MinMaxScaler
                scaler = MinMaxScaler(feature_range=(0, 100))
                
                radar_data[[temp_col, wind_col, humidity_col]] = scaler.fit_transform(
                    radar_data[[temp_col, wind_col, humidity_col]]
                )
                
                fig = go.Figure()
                
                categories = ['Temperature', 'Wind Speed', 'Humidity']
                
                for idx, row in radar_data.iterrows():
                    fig.add_trace(go.Scatterpolar(
                        r=[row[temp_col], row[wind_col], row[humidity_col]],
                        theta=categories,
                        fill='toself',
                        name=row[country_col]
                    ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )
                    ),
                    showlegend=True,
                    title="Weather Characteristics by Country (Normalized)",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("""
                    <div class='interpretation-box'>
                        <h4>📡 How to Read Radar Charts</h4>
                        <p>Each colored polygon represents one country. The further from center, the higher the value (0-100 normalized).</p>
                        <p><strong>Large polygons</strong> = High overall weather metrics</p>
                        <p><strong>Small polygons</strong> = Low overall weather metrics</p>
                        <p><strong>Uneven shapes</strong> = Varying characteristics across metrics</p>
                    </div>
                """, unsafe_allow_html=True)
        
        # SCATTER ANALYSIS
        with tab_scatter:
            st.markdown("### 🔬 Advanced Scatter Analysis")
            
            if temp_col and humidity_col and wind_col:
                col1, col2 = st.columns(2)
                
                with col1:
                    # 3D Scatter Plot
                    sample_3d = df[[temp_col, humidity_col, wind_col]].dropna().sample(min(2000, len(df)))
                    
                    fig = px.scatter_3d(
                        sample_3d,
                        x=temp_col,
                        y=humidity_col,
                        z=wind_col,
                        color=temp_col,
                        color_continuous_scale='Turbo',
                        opacity=0.7,
                        title="3D Weather Space"
                    )
                    fig.update_layout(height=500, scene=dict(
                        xaxis_title='Temperature (°C)',
                        yaxis_title='Humidity (%)',
                        zaxis_title='Wind Speed (kph)'
                    ))
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Density Contour
                    sample_2d = df[[temp_col, humidity_col]].dropna().sample(min(3000, len(df)))
                    
                    fig = px.density_contour(
                        sample_2d,
                        x=temp_col,
                        y=humidity_col,
                        color_discrete_sequence=['#667eea'],
                        title="Temperature-Humidity Density"
                    )
                    fig.update_traces(contours_coloring="fill", contours_showlabels=True)
                    fig.update_layout(height=500, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Scatter Matrix with Correlation
                st.markdown("#### 📊 Complete Scatter Matrix")
                
                numeric_cols_scatter = [temp_col, humidity_col, wind_col]
                if pressure_col:
                    numeric_cols_scatter.append(pressure_col)
                
                sample_matrix = df[numeric_cols_scatter].dropna().sample(min(1500, len(df)))
                
                fig = px.scatter_matrix(
                    sample_matrix,
                    dimensions=numeric_cols_scatter,
                    color=temp_col,
                    color_continuous_scale='Viridis',
                    opacity=0.5,
                    title="Multi-Variable Scatter Matrix with Correlations"
                )
                fig.update_traces(diagonal_visible=False, showupperhalf=False)
                fig.update_layout(height=700, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if wind_col:
            st.markdown("### 💨 Wind Speed Distribution")
            fig = px.histogram(df, x=wind_col, nbins=50, marginal="rug", color_discrete_sequence=['#4ECDC4'])
            fig.add_vline(x=df[wind_col].mean(), line_dash="dash", line_color="red", annotation_text="Mean")
            fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if humidity_col:
            st.markdown("### 💧 Humidity Distribution")
            fig = px.histogram(df, x=humidity_col, nbins=50, marginal="rug", color_discrete_sequence=['#F38181'])
            fig.add_vline(x=df[humidity_col].mean(), line_dash="dash", line_color="red", annotation_text="Mean")
            fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    # Additional Distributions
    st.markdown("---")
    st.markdown("### 📊 Multi-Variable Distribution Comparison")
    
    if pressure_col and 'visibility_km' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(df, x=pressure_col, nbins=40, marginal="box", color_discrete_sequence=['#9b59b6'])
            fig.add_vline(x=df[pressure_col].mean(), line_dash="dash", line_color="red")
            fig.update_layout(title="Pressure Distribution", height=400, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.histogram(df, x='visibility_km', nbins=40, marginal="box", color_discrete_sequence=['#1abc9c'])
            fig.add_vline(x=df['visibility_km'].mean(), line_dash="dash", line_color="red")
            fig.update_layout(title="Visibility Distribution", height=400, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

# TAB 4: EXTREME EVENTS DETECTION

with tab4:
    st.markdown("## 🔥 Extreme Events Detection")
    
    add_interpretation(
        "Extreme Event Detection",
        "Identifies unusually hot, cold, or windy conditions using statistical thresholds (standard deviations from mean).",
        "Sensitivity slider controls strictness: 3σ = strictest (finds only most extreme), 1σ = lenient (finds more events).", 
        "Events beyond thresholds are 'extreme'. 3σ means top/bottom 0.3% of data.",
        "Extremes indicate: (1) heat waves/cold snaps, (2) storms, (3) climate anomalies, or (4) potential data errors."
    )

    col1, col2 = st.columns([3, 1])
    
    with col1:
        sigma = st.slider("🎚️ Detection Sensitivity (σ)", 1.0, 4.0, 3.0, 0.5, help="Higher values = stricter detection")
    
    with col2:
        coverage = (1 - 2*(1-stats.norm.cdf(sigma)))*100
        st.metric("Coverage", f"{coverage:.2f}%")
    
    extreme_results = {}
    
    if temp_col:
        extreme_high_temp, extreme_low_temp, upper_temp, lower_temp = detect_extreme_events(df, temp_col, sigma)
        extreme_results['Temperature'] = {
            'high': len(extreme_high_temp), 'low': len(extreme_low_temp),
            'high_data': extreme_high_temp, 'low_data': extreme_low_temp,
            'upper': upper_temp, 'lower': lower_temp
        }
    
    if wind_col:
        extreme_high_wind, _, upper_wind, _ = detect_extreme_events(df, wind_col, sigma)
        extreme_results['Wind'] = {'high': len(extreme_high_wind), 'high_data': extreme_high_wind, 'upper': upper_wind}
    
    if humidity_col:
        extreme_high_hum, extreme_low_hum, upper_hum, lower_hum = detect_extreme_events(df, humidity_col, sigma)
        extreme_results['Humidity'] = {
            'high': len(extreme_high_hum), 'low': len(extreme_low_hum),
            'high_data': extreme_high_hum, 'low_data': extreme_low_hum,
            'upper': upper_hum, 'lower': lower_hum
        }
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = extreme_results.get('Temperature', {}).get('high', 0) + extreme_results.get('Temperature', {}).get('low', 0)
        pct = (total / len(df) * 100) if len(df) > 0 else 0
        st.metric("🔥 Total Extremes", f"{total:,}", f"{pct:.2f}%")
    
    with col2:
        high_temp = extreme_results.get('Temperature', {}).get('high', 0)
        st.metric("🌡️ Heat Events", f"{high_temp:,}")
    
    with col3:
        low_temp = extreme_results.get('Temperature', {}).get('low', 0)
        st.metric("❄️ Cold Events", f"{low_temp:,}")
    
    with col4:
        wind_extreme = extreme_results.get('Wind', {}).get('high', 0)
        st.metric("💨 Wind Events", f"{wind_extreme:,}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if temp_col and 'Temperature' in extreme_results:
            st.markdown("### 🌡️ Temperature Extremes")
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=df[temp_col], nbinsx=50, name='All Data', marker_color='lightblue', opacity=0.7))
            
            if len(extreme_results['Temperature']['high_data']) > 0:
                fig.add_trace(go.Histogram(x=extreme_results['Temperature']['high_data'][temp_col], nbinsx=50, name='Extreme High', marker_color='red', opacity=0.8))
            
            if len(extreme_results['Temperature']['low_data']) > 0:
                fig.add_trace(go.Histogram(x=extreme_results['Temperature']['low_data'][temp_col], nbinsx=50, name='Extreme Low', marker_color='blue', opacity=0.8))
            
            fig.add_vline(x=extreme_results['Temperature']['upper'], line_dash="dash", line_color="red", annotation_text="Upper")
            fig.add_vline(x=extreme_results['Temperature']['lower'], line_dash="dash", line_color="blue", annotation_text="Lower")
            
            fig.update_layout(height=450, barmode='overlay', plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if wind_col and 'Wind' in extreme_results:
            st.markdown("### 💨 Wind Speed Extremes")
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=df[wind_col], nbinsx=50, name='All Data', marker_color='lightgreen', opacity=0.7))
            
            if len(extreme_results['Wind']['high_data']) > 0:
                fig.add_trace(go.Histogram(x=extreme_results['Wind']['high_data'][wind_col], nbinsx=50, name='Extreme High', marker_color='darkred', opacity=0.8))
            
            fig.add_vline(x=extreme_results['Wind']['upper'], line_dash="dash", line_color="red", annotation_text="Threshold")
            
            fig.update_layout(height=450, barmode='overlay', plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    # Extreme Events Timeline
    if temp_col and date_col and 'Temperature' in extreme_results:
        st.markdown("---")
        st.markdown("### 📅 Extreme Events Timeline")
        
        all_extremes = pd.concat([
            extreme_results['Temperature']['high_data'],
            extreme_results['Temperature']['low_data']
        ])
        
        if len(all_extremes) > 0 and date_col in all_extremes.columns:
            all_extremes['event_type'] = all_extremes[temp_col].apply(
                lambda x: 'Heat Wave' if x > extreme_results['Temperature']['upper'] else 'Cold Snap'
            )
            
            fig = px.scatter(all_extremes, x=date_col, y=temp_col, color='event_type',
                           color_discrete_map={'Heat Wave': '#e74c3c', 'Cold Snap': '#3498db'},
                           title="Extreme Temperature Events Over Time",
                           labels={temp_col: 'Temperature (°C)', date_col: 'Date'})
            fig.update_traces(marker=dict(size=10))
            fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    # EXTREME EVENTS LOG
    st.markdown("---")
    st.markdown("### 📋 Extreme Events Log")
    
    if temp_col and 'Temperature' in extreme_results:
        all_extreme_events = pd.concat([
            extreme_results['Temperature']['high_data'],
            extreme_results['Temperature']['low_data']
        ])
        
        if len(all_extreme_events) > 0:
            # Add event classification
            all_extreme_events['Event Type'] = all_extreme_events[temp_col].apply(
                lambda x: '🔥 Heat Wave' if x > extreme_results['Temperature']['upper'] else '❄️ Cold Snap'
            )
            
            # Add severity
            mean_temp = df[temp_col].mean()
            all_extreme_events['Deviation'] = abs(all_extreme_events[temp_col] - mean_temp)
            all_extreme_events['Severity'] = pd.cut(
                all_extreme_events['Deviation'],
                bins=[0, 10, 20, 100],
                labels=['Moderate', 'Severe', 'Extreme']
            )
            
            # Select columns for display
            log_cols = ['Event Type', temp_col, 'Severity']
            if date_col in all_extreme_events.columns:
                log_cols.insert(0, date_col)
            if location_col in all_extreme_events.columns:
                log_cols.insert(1, location_col)
            if country_col in all_extreme_events.columns:
                log_cols.insert(2, country_col)
            
            display_log = all_extreme_events[log_cols].head(50).copy()
            display_log.columns = [col.replace('_', ' ').title() for col in display_log.columns]
            
            st.markdown("#### 🔝 Top 50 Extreme Events")
            st.dataframe(
                display_log.style.background_gradient(cmap='RdYlBu_r', subset=[col for col in display_log.columns if 'Temp' in col or 'temp' in col]),
                use_container_width=True,
                height=400
            )
            
            # Event Summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                heat_waves = len(all_extreme_events[all_extreme_events['Event Type'] == '🔥 Heat Wave'])
                st.markdown(f"""
                    <div class='alert-danger'>
                        <h4>🔥 Heat Waves</h4>
                        <p style='font-size: 2rem; font-weight: 700; margin: 0.5rem 0;'>{heat_waves}</p>
                        <p>Extreme high temperature events</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                cold_snaps = len(all_extreme_events[all_extreme_events['Event Type'] == '❄️ Cold Snap'])
                st.markdown(f"""
                    <div class='alert-info'>
                        <h4>❄️ Cold Snaps</h4>
                        <p style='font-size: 2rem; font-weight: 700; margin: 0.5rem 0;'>{cold_snaps}</p>
                        <p>Extreme low temperature events</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                extreme_severity = len(all_extreme_events[all_extreme_events['Severity'] == 'Extreme'])
                st.markdown(f"""
                    <div class='alert-warning'>
                        <h4>⚠️ Extreme Severity</h4>
                        <p style='font-size: 2rem; font-weight: 700; margin: 0.5rem 0;'>{extreme_severity}</p>
                        <p>Highest severity events</p>
                    </div>
                """, unsafe_allow_html=True)

# TAB 5: CITY-LEVEL ANALYSIS

with tab5:
    st.markdown("## 🏙️ City-Level Weather Analysis")
    
    add_interpretation(
        "City Comparison",
        "Detailed weather comparison across cities within your selected countries. Shows which cities are hottest, coldest, windiest, etc.",
        "Each bar = one city. Bar height = average value. Cities are sorted by the metric you choose. Color intensity shows relative values.",
        "Cities at top of chart have highest values for selected metric. Compare cities within same country or across countries.",
        "Use to: (1) Find hottest/coldest cities, (2) Compare urban climates, (3) Identify best weather for activities, (4) Understand local climate variations."
    )
    
    if location_col and temp_col and country_col:
        top_n = st.slider("Number of Cities to Display", 10, 50, 20, 5)
        
        metric_options = ["Temperature"]
        if wind_col:
            metric_options.append("Wind Speed")
        if humidity_col:
            metric_options.append("Humidity")
        if pressure_col:
            metric_options.append("Pressure")
        
        sort_by = st.selectbox("Sort By", metric_options)
        
        # Prepare city statistics
        agg_dict = {temp_col: ['mean', 'std', 'min', 'max']}
        if wind_col:
            agg_dict[wind_col] = ['mean']
        if humidity_col:
            agg_dict[humidity_col] = ['mean']
        if pressure_col:
            agg_dict[pressure_col] = ['mean']
        
        city_stats = df.groupby([location_col, country_col]).agg(agg_dict).reset_index()
        
        city_stats.columns = ['_'.join(col).strip('_') for col in city_stats.columns.values]
        
        # Rename columns for clarity
        new_cols = ['city', 'country', 'temp_mean', 'temp_std', 'temp_min', 'temp_max']
        if wind_col:
            new_cols.append('wind_mean')
        if humidity_col:
            new_cols.append('hum_mean')
        if pressure_col:
            new_cols.append('pres_mean')
        
        city_stats.columns = new_cols
        
        # Sort based on selected metric
        if sort_by == "Temperature":
            city_stats = city_stats.sort_values('temp_mean', ascending=False).head(top_n)
            metric = 'temp_mean'
            title = f"Top {top_n} Cities by Temperature"
            yaxis = "Temperature (°C)"
            colorscale = 'RdYlBu_r'
        elif sort_by == "Wind Speed" and wind_col:
            city_stats = city_stats.sort_values('wind_mean', ascending=False).head(top_n)
            metric = 'wind_mean'
            title = f"Top {top_n} Cities by Wind Speed"
            yaxis = "Wind Speed (kph)"
            colorscale = 'Viridis'
        elif sort_by == "Humidity" and humidity_col:
            city_stats = city_stats.sort_values('hum_mean', ascending=False).head(top_n)
            metric = 'hum_mean'
            title = f"Top {top_n} Cities by Humidity"
            yaxis = "Humidity (%)"
            colorscale = 'Blues'
        elif sort_by == "Pressure" and pressure_col:
            city_stats = city_stats.sort_values('pres_mean', ascending=False).head(top_n)
            metric = 'pres_mean'
            title = f"Top {top_n} Cities by Pressure"
            yaxis = "Pressure (mb)"
            colorscale = 'Plasma'
        
        city_stats['city_country'] = city_stats['city'].fillna('Unknown').astype(str) + ', ' + city_stats['country'].fillna('Unknown').astype(str)
        
        fig = px.bar(city_stats, x='city_country', y=metric, color=metric, 
                     color_continuous_scale=colorscale, title=title)
        fig.update_xaxes(tickangle=-45)
        fig.update_layout(height=500, plot_bgcolor='white', xaxis_title="City", yaxis_title=yaxis)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📊 Detailed City Statistics")
        display_cols = city_stats[['city', 'country', 'temp_mean', 'temp_std', 'temp_min', 'temp_max']].copy()
        display_cols.columns = ['City', 'Country', 'Avg Temp (°C)', 'Std Dev', 'Min Temp', 'Max Temp']
        st.dataframe(
            display_cols.style.format({
                'Avg Temp (°C)': '{:.1f}', 
                'Std Dev': '{:.1f}', 
                'Min Temp': '{:.1f}', 
                'Max Temp': '{:.1f}'
            }).background_gradient(cmap='RdYlGn', subset=['Avg Temp (°C)']),
            use_container_width=True, height=400
        )
        
        # City Weather Comparison Chart
        st.markdown("---")
        st.markdown("### 🎯 Multi-Metric City Comparison")
        
        if len(city_stats) >= 5:
            top5_cities = city_stats.head(5)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Temperature',
                x=top5_cities['city_country'],
                y=top5_cities['temp_mean'],
                marker_color='#e74c3c'
            ))
            
            if 'wind_mean' in top5_cities.columns:
                fig.add_trace(go.Bar(
                    name='Wind Speed (×2)',
                    x=top5_cities['city_country'],
                    y=top5_cities['wind_mean'] * 2,
                    marker_color='#3498db'
                ))
            
            if 'hum_mean' in top5_cities.columns:
                fig.add_trace(go.Bar(
                    name='Humidity (÷2)',
                    x=top5_cities['city_country'],
                    y=top5_cities['hum_mean'] / 2,
                    marker_color='#2ecc71'
                ))
            
            fig.update_layout(
                barmode='group',
                title="Top 5 Cities - Multi-Metric Comparison",
                xaxis_tickangle=-45,
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)

# TAB 6: TIME SERIES ANALYSIS

with tab6:
    st.markdown("## 📅 Weather Trends Over Time")
    
    add_interpretation(
        "Time Series Analysis",
        "Shows how weather changes over time - warming/cooling trends, seasonal patterns, and day-to-day variations.",
        "Line goes up = warming, down = cooling. Trend line shows overall direction. Wiggles show daily/seasonal variations.",
        "Positive trend slope = temperatures increasing. Negative = cooling. Flat = stable. Steeper line = faster change.",
        "Use to: (1) Identify warming/cooling trends, (2) Spot seasonal patterns, (3) Compare time periods, (4) Detect unusual events."
    )
    
    if date_col and temp_col:
        agg_method = st.selectbox("Time Grouping", ['Daily', 'Weekly', 'Monthly'])
        freq = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M'}[agg_method]
        
        col1, col2 = st.columns(2)
        with col1:
            show_trend = st.checkbox("Show Trend Line", value=True)
        with col2:
            show_ma = st.checkbox("Moving Average", value=False)
        
        df_ts = df.copy().sort_values(date_col)
        ts_data = df_ts.set_index(date_col)[temp_col].resample(freq).mean().dropna()
        
        if len(ts_data) > 1:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=ts_data.index, 
                y=ts_data.values, 
                mode='lines+markers', 
                name='Temperature', 
                line=dict(color='#667eea', width=3),
                marker=dict(size=6)
            ))
            
            ma_window = {'Daily': 7, 'Weekly': 4, 'Monthly': 3}[agg_method]
            if show_ma and len(ts_data) >= ma_window:
                ma = ts_data.rolling(window=ma_window).mean()
                fig.add_trace(go.Scatter(
                    x=ma.index,
                    y=ma.values,
                    mode='lines',
                    name=f'{ma_window}-Period MA',
                    line=dict(color='orange', width=2, dash='dot')
                ))
            
            if show_trend and len(ts_data) >= 3:
                x_num = np.arange(len(ts_data))
                z = np.polyfit(x_num, ts_data.values, 1)
                p = np.poly1d(z)
                fig.add_trace(go.Scatter(
                    x=ts_data.index, 
                    y=p(x_num), 
                    mode='lines', 
                    name='Trend', 
                    line=dict(color='red', width=2, dash='dash')
                ))
                
                # Calculate trend
                trend_direction = "Increasing" if z[0] > 0 else "Decreasing" if z[0] < 0 else "Stable"
                trend_value = abs(z[0])
                
                st.markdown(f"""
                    <div class='alert-info'>
                        <h4>📈 Trend Analysis</h4>
                        <p><strong>Direction:</strong> {trend_direction}</p>
                        <p><strong>Rate:</strong> {trend_value:.4f}°C per period</p>
                    </div>
                """, unsafe_allow_html=True)
            
            fig.update_layout(
                title="Temperature Trend Analysis", 
                xaxis_title="Date", 
                yaxis_title="Temperature (°C)", 
                height=450, 
                plot_bgcolor='white', 
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # NEW: WIND SPEED TREND
        if wind_col:
            st.markdown("---")
            st.markdown("### 💨 Wind Speed Trend Analysis")
            
            wind_ts_data = df_ts.set_index(date_col)[wind_col].resample(freq).mean().dropna()
            
            if len(wind_ts_data) > 1:
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=wind_ts_data.index,
                    y=wind_ts_data.values,
                    mode='lines+markers',
                    name='Wind Speed',
                    line=dict(color='#4ECDC4', width=3),
                    marker=dict(size=6),
                    fill='tozeroy',
                    fillcolor='rgba(78, 205, 196, 0.2)'
                ))
                
                if show_ma and len(wind_ts_data) >= ma_window:
                    wind_ma = wind_ts_data.rolling(window=ma_window).mean()
                    fig.add_trace(go.Scatter(
                        x=wind_ma.index,
                        y=wind_ma.values,
                        mode='lines',
                        name=f'{ma_window}-Period MA',
                        line=dict(color='#e67e22', width=2, dash='dot')
                    ))
                
                if show_trend and len(wind_ts_data) >= 3:
                    x_num = np.arange(len(wind_ts_data))
                    z_wind = np.polyfit(x_num, wind_ts_data.values, 1)
                    p_wind = np.poly1d(z_wind)
                    fig.add_trace(go.Scatter(
                        x=wind_ts_data.index,
                        y=p_wind(x_num),
                        mode='lines',
                        name='Trend',
                        line=dict(color='red', width=2, dash='dash')
                    ))
                
                fig.update_layout(
                    title="Wind Speed Over Time",
                    xaxis_title="Date",
                    yaxis_title="Wind Speed (kph)",
                    height=450,
                    plot_bgcolor='white',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Wind Speed Statistics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Avg Wind", f"{wind_ts_data.mean():.1f} kph")
                with col2:
                    st.metric("Max Wind", f"{wind_ts_data.max():.1f} kph")
                with col3:
                    st.metric("Min Wind", f"{wind_ts_data.min():.1f} kph")
                with col4:
                    st.metric("Variability", f"{wind_ts_data.std():.1f} kph")
        
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
                    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
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
        
        # Year-over-Year Comparison
        if len(df_ts) > 365:
            st.markdown("---")
            st.markdown("### 📆 Year-over-Year Comparison")
            
            df_ts['year'] = df_ts[date_col].dt.year
            df_ts['day_of_year'] = df_ts[date_col].dt.dayofyear
            
            years = sorted(df_ts['year'].unique())
            
            if len(years) >= 2:
                fig = go.Figure()
                
                for year in years[-3:]:  # Last 3 years
                    year_data = df_ts[df_ts['year'] == year]
                    fig.add_trace(go.Scatter(
                        x=year_data['day_of_year'],
                        y=year_data[temp_col],
                        mode='lines',
                        name=str(year),
                        opacity=0.7
                    ))
                
                fig.update_layout(
                    title="Temperature Comparison - Last 3 Years",
                    xaxis_title="Day of Year",
                    yaxis_title="Temperature (°C)",
                    height=400,
                    plot_bgcolor='white',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)

# TAB 7: CORRELATION ANALYSIS

with tab7:
    st.markdown("## 🔗 Correlation Analysis")
    
    add_interpretation(
        "Variable Relationships",
        "Shows how weather variables relate to each other. Do temperature and humidity move together or opposite?",
        "Red = positive correlation (both increase together), Blue = negative (one up, other down), White = no relationship.",
        "Values range from -1 to +1. |r| > 0.7 = strong, 0.4-0.7 = moderate, < 0.4 = weak.",
        "Strong correlations reveal: (1) How factors interact, (2) Which variables can predict others, (3) Climate patterns."
    )

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
        
        # Scatter plots for top correlations
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
        
        # Individual Scatter Plots
        st.markdown("---")
        st.markdown("### 🎯 Detailed Relationship Analysis")
        
        if temp_col and humidity_col:
            col1, col2 = st.columns(2)
            
            with col1:
                sample_data = df[[temp_col, humidity_col]].dropna().sample(min(3000, len(df)))
                fig = px.scatter(
                    sample_data, 
                    x=temp_col, 
                    y=humidity_col, 
                    trendline="ols",
                    color=humidity_col,
                    color_continuous_scale='Blues',
                    opacity=0.5,
                    title="Temperature vs Humidity"
                )
                fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if wind_col:
                    sample_data = df[[temp_col, wind_col]].dropna().sample(min(3000, len(df)))
                    fig = px.scatter(
                        sample_data, 
                        x=temp_col, 
                        y=wind_col, 
                        trendline="ols",
                        color=wind_col,
                        color_continuous_scale='Viridis',
                        opacity=0.5,
                        title="Temperature vs Wind Speed"
                    )
                    fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)

# TAB 8: GEOGRAPHIC MAPS WITH BLACK BACKGROUND

with tab8:
    st.markdown("## 🗺️ Geographic Visualizations")
    
    add_interpretation(
        "Global Weather Visualization",
        "Interactive world map showing weather data by color. Hot regions = red/orange, cold regions = blue/purple.",
        "Hover over countries to see exact values. Dark colors = extreme values, light colors = moderate values.", 
        "Map shows average values for entire countries. Useful for seeing global patterns at a glance.",
        "Insights: (1) Which regions are hottest/coldest? (2) Climate zones visible? (3) Continental differences?"
    )
    
    if country_col and temp_col:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            map_var_options = [temp_col]
            if wind_col:
                map_var_options.append(wind_col)
            if humidity_col:
                map_var_options.append(humidity_col)
            if pressure_col:
                map_var_options.append(pressure_col)
            map_var = st.selectbox("Select Variable", map_var_options)
        
        with col2:
            map_projection = st.selectbox("Map Style", ["natural earth", "orthographic", "equirectangular", "mercator"])
        
        # Country-level Choropleth Map with BLACK BACKGROUND
        st.markdown(f"### 🗺️ Global {map_var} Distribution (Country Level)")
        
        country_avg = df.groupby(country_col)[map_var].mean().reset_index()
        country_avg.columns = ['country', 'avg_value']
        
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
        
        # BLACK BACKGROUND
        fig.update_geos(
            showcountries=True, 
            countrycolor="white", 
            showcoastlines=True, 
            coastlinecolor="white", 
            bgcolor="#000000",  # Black background
            showland=True,
            landcolor="#1a1a1a",
            showocean=True,
            oceancolor="#0d1117"
        )
        
        fig.update_layout(
            height=600, 
            margin={"r":0,"t":50,"l":0,"b":0},
            paper_bgcolor="#000000",  # Black paper background
            font=dict(color="white"),
            title_font=dict(color="white")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # LOCATION-BASED TEMPERATURE MAP with BLACK BACKGROUND
        if location_col and temp_col and 'latitude' in df.columns and 'longitude' in df.columns:
            st.markdown("---")
            st.markdown("### 📍 Location-Based Temperature Map")
            
            # Prepare location data
            location_data = df.groupby([location_col, 'latitude', 'longitude']).agg({
                temp_col: 'mean'
            }).reset_index()
            
            location_data.columns = ['Location', 'Latitude', 'Longitude', 'Temperature']
            
            # Remove invalid coordinates
            location_data = location_data[
                (location_data['Latitude'].notna()) & 
                (location_data['Longitude'].notna()) &
                (location_data['Latitude'].between(-90, 90)) &
                (location_data['Longitude'].between(-180, 180))
            ]
            
            if len(location_data) > 0:
                # Convert temperature to positive scale for size (size must be >= 0)
                # Shift temperature so minimum is 1, then scale to 5-20 range
                temp_min = location_data['Temperature'].min()
                temp_max = location_data['Temperature'].max()
                if temp_min == temp_max:
                    location_data['Size'] = 10
                else:
                    location_data['Size'] = 5 + 15 * (location_data['Temperature'] - temp_min) / (temp_max - temp_min)
                
                fig = px.scatter_geo(
                    location_data,
                    lat='Latitude',
                    lon='Longitude',
                    color='Temperature',
                    size='Size',
                    hover_name='Location',
                    hover_data={'Temperature': ':.1f', 'Latitude': ':.2f', 'Longitude': ':.2f', 'Size': False},
                    color_continuous_scale='RdYlBu_r',
                    size_max=20,
                    title="Temperature Distribution by City Location",
                    projection=map_projection
                )
                
                # BLACK BACKGROUND for location map
                fig.update_geos(
                    showcountries=True,
                    countrycolor="rgba(255,255,255,0.3)",
                    showcoastlines=True,
                    coastlinecolor="white",
                    bgcolor="#000000",
                    showland=True,
                    landcolor="#1a1a1a",
                    showocean=True,
                    oceancolor="#0d1117"
                )
                
                fig.update_layout(
                    height=600,
                    margin={"r":0,"t":50,"l":0,"b":0},
                    paper_bgcolor="#000000",
                    font=dict(color="white"),
                    title_font=dict(color="white")
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("""
                    <div class='interpretation-box'>
                        <h4>📍 How to Read Location Maps</h4>
                        <p><strong>Bubble Size:</strong> Larger bubbles = higher temperatures</p>
                        <p><strong>Bubble Color:</strong> Red = hot, Blue = cold, Yellow = moderate</p>
                        <p><strong>Hover:</strong> See exact city name, coordinates, and temperature</p>
                        <p><strong>Zoom:</strong> Double-click to reset view, scroll to zoom</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ No valid location coordinates found in the dataset for mapping.")
        
        # Regional Breakdown
        st.markdown("---")
        st.markdown("### 🌍 Regional Statistics")
        
        regional_stats = df.groupby(country_col).agg({
            map_var: ['mean', 'min', 'max', 'std', 'count']
        }).reset_index()
        
        regional_stats.columns = ['Country', 'Mean', 'Min', 'Max', 'Std Dev', 'Data Points']
        regional_stats = regional_stats.sort_values('Mean', ascending=False).head(20)
        
        st.dataframe(
            regional_stats.style.format({
                'Mean': '{:.2f}',
                'Min': '{:.2f}',
                'Max': '{:.2f}',
                'Std Dev': '{:.2f}',
                'Data Points': '{:.0f}'
            }).background_gradient(cmap='RdYlGn', subset=['Mean']),
            use_container_width=True,
            height=400
        )
        
        # Top/Bottom Countries 
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### 🔥 Top 10 Highest {map_var}")
            top_countries = country_avg.nlargest(10, 'avg_value')
            fig = px.bar(
                top_countries,
                x='country',
                y='avg_value', 
                color='avg_value',
                color_continuous_scale='Reds',
                title=f"Highest {map_var}"
            )
            fig.update_xaxes(tickangle=-45)
            fig.update_layout(height=400, showlegend=False, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(f"### ❄️ Top 10 Lowest {map_var}")
            bottom_countries = country_avg.nsmallest(10, 'avg_value')
            fig = px.bar(
                bottom_countries,
                x='country',
                y='avg_value',
                color='avg_value', 
                color_continuous_scale='Blues',
                title=f"Lowest {map_var}"
            )
            fig.update_xaxes(tickangle=-45)
            fig.update_layout(height=400, showlegend=False, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

# TAB 9: HUMIDITY ANALYSIS

with tab9:
    st.markdown("## 💧 Humidity Analysis")
    
    add_interpretation(
        "Moisture in the Air",
        "Humidity measures water vapor in air (0% = bone dry, 100% = saturated). Affects comfort and weather.",
        "Bar height = frequency of that humidity level. Box plot shows typical range. Most data in box = common range.",
        "40-60% = comfortable, <30% = dry, >70% = humid/sticky. High humidity makes heat feel hotter.",
        "Conclusions: (1) Is your region humid or dry? (2) Humidity consistent or variable? (3) Comfort level?"
    )
    
    if humidity_col:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_hum = df[humidity_col].mean()
            st.metric("💧 Average", f"{avg_hum:.1f}%")
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Humidity Distribution")
            fig = px.histogram(df, x=humidity_col, nbins=50, marginal="box", color_discrete_sequence=['#4ECDC4'])
            fig.add_vline(x=avg_hum, line_dash="dash", line_color="red", annotation_text=f"Mean: {avg_hum:.1f}%")
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
                    opacity=0.5,
                    title="Temperature vs Humidity"
                )
                fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        
        # Humidity Categories
        st.markdown("---")
        st.markdown("### 📋 Humidity Categories")
        
        df['humidity_category'] = pd.cut(
            df[humidity_col], 
            bins=[0, 30, 60, 80, 100],
            labels=['Dry (<30%)', 'Comfortable (30-60%)', 'Humid (60-80%)', 'Very Humid (>80%)']
        )
        
        category_counts = df['humidity_category'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                values=category_counts.values, 
                names=category_counts.index,
                title="Humidity Distribution by Category",
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                x=category_counts.index, 
                y=category_counts.values,
                color=category_counts.values,
                color_continuous_scale='Blues',
                title="Records per Humidity Category"
            )
            fig.update_layout(
                height=400, 
                showlegend=False, 
                xaxis_title="Category",
                yaxis_title="Count",
                plot_bgcolor='white', 
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Humidity by Country
        if country_col:
            st.markdown("---")
            st.markdown("### 🌍 Humidity by Country")
            
            top_countries = df[country_col].value_counts().head(10).index
            fig = px.box(
                df[df[country_col].isin(top_countries)], 
                x=country_col, 
                y=humidity_col,
                color=country_col,
                title="Humidity Distribution - Top 10 Countries"
            )
            fig.update_xaxes(tickangle=-45)
            fig.update_layout(height=400, showlegend=False, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

# TAB 10: WIND & PRESSURE ANALYSIS WITH DIRECTION AND CATEGORIES

with tab10:
    st.markdown("## 💨 Wind & Pressure Analysis")
    
    add_interpretation(
        "Atmospheric Dynamics",
        "Wind and pressure are interconnected - pressure differences drive wind. Lower pressure = stronger winds typically.",
        "Wind speed shows movement intensity. Pressure shows atmospheric weight. Both affect weather patterns.",
        "Normal pressure ~1013 mb. High pressure = clear skies, Low pressure = clouds/storms. Wind >50 kph = strong.",
        "Use to: (1) Identify storm systems, (2) Predict weather changes, (3) Assess wind energy potential, (4) Safety planning."
    )
    
    col1, col2 = st.columns(2)
    
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
            
            fig = px.histogram(df, x=wind_col, nbins=50, marginal="violin", color_discrete_sequence=['#95a5a6'])
            fig.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Wind Categories (Beaufort Scale)
            df['wind_category'] = pd.cut(
                df[wind_col],
                bins=[0, 12, 29, 50, 89, 1000],
                labels=['Light (0-12)', 'Moderate (12-29)', 'Strong (29-50)', 'Gale (50-89)', 'Storm (>89)']
            )
            
            wind_cat_counts = df['wind_category'].value_counts()
            
            fig = px.bar(
                x=wind_cat_counts.index,
                y=wind_cat_counts.values,
                color=wind_cat_counts.values,
                color_continuous_scale='YlOrRd',
                title="Wind Speed Categories (Beaufort Scale)"
            )
            fig.update_layout(
                height=300,
                showlegend=False,
                xaxis_title="Category",
                yaxis_title="Frequency",
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    
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
            
            fig = px.histogram(df, x=pressure_col, nbins=50, marginal="box", color_discrete_sequence=['#3498db'])
            fig.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            # PRESSURE CATEGORIES
            df['pressure_category'] = pd.cut(
                df[pressure_col],
                bins=[0, 1000, 1013, 1020, 2000],
                labels=['Low (<1000)', 'Normal (1000-1013)', 'High (1013-1020)', 'Very High (>1020)']
            )
            
            pres_cat_counts = df['pressure_category'].value_counts()
            
            fig = px.bar(
                x=pres_cat_counts.index,
                y=pres_cat_counts.values,
                color=pres_cat_counts.values,
                color_continuous_scale='Blues',
                title="Atmospheric Pressure Categories"
            )
            fig.update_layout(
                height=300,
                showlegend=False,
                xaxis_title="Category",
                yaxis_title="Frequency",
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # WIND DIRECTION DISTRIBUTION
    if 'wind_degree' in df.columns or 'wind_dir' in df.columns:
        st.markdown("---")
        st.markdown("### 🧭 Wind Direction Distribution")
        
        wind_dir_col = 'wind_degree' if 'wind_degree' in df.columns else 'wind_dir'
        
        if 'wind_degree' in df.columns:
            # Convert degrees to cardinal directions
            def degree_to_direction(degree):
                if pd.isna(degree):
                    return None
                directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                             'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
                idx = int((degree + 11.25) / 22.5) % 16
                return directions[idx]
            
            df['wind_direction'] = df['wind_degree'].apply(degree_to_direction)
        else:
            df['wind_direction'] = df['wind_dir']
        
        if 'wind_direction' in df.columns:
            wind_dir_counts = df['wind_direction'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Wind Rose Chart (Polar Bar Chart)
                directions_order = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                                   'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
                
                # Reindex to ensure all directions are present
                wind_dir_counts = wind_dir_counts.reindex(directions_order, fill_value=0)
                
                fig = go.Figure()
                
                fig.add_trace(go.Barpolar(
                    r=wind_dir_counts.values,
                    theta=directions_order,
                    marker_color=wind_dir_counts.values,
                    marker_colorscale='Viridis',
                    marker_line_color="black",
                    marker_line_width=1,
                    opacity=0.8
                ))
                
                fig.update_layout(
                    title="Wind Rose - Direction Distribution",
                    polar=dict(
                        radialaxis=dict(visible=True, showticklabels=True),
                        angularaxis=dict(direction="clockwise")
                    ),
                    height=450,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Bar chart of wind directions
                fig = px.bar(
                    x=wind_dir_counts.index,
                    y=wind_dir_counts.values,
                    color=wind_dir_counts.values,
                    color_continuous_scale='Viridis',
                    title="Wind Direction Frequency"
                )
                fig.update_layout(
                    height=450,
                    showlegend=False,
                    xaxis_title="Direction",
                    yaxis_title="Frequency",
                    plot_bgcolor='white',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Dominant wind direction analysis
            dominant_direction = wind_dir_counts.idxmax()
            dominant_percentage = (wind_dir_counts.max() / wind_dir_counts.sum() * 100)
            
            st.markdown(f"""
                <div class='alert-info'>
                    <h4>🧭 Dominant Wind Direction</h4>
                    <p><strong>Primary Direction:</strong> {dominant_direction}</p>
                    <p><strong>Frequency:</strong> {wind_dir_counts.max():,} occurrences ({dominant_percentage:.1f}%)</p>
                    <p><strong>Interpretation:</strong> Winds predominantly blow from the {dominant_direction} direction, 
                    which can indicate prevailing weather patterns in this region.</p>
                </div>
            """, unsafe_allow_html=True)
    
    # PRESSURE CATEGORIES ANALYSIS
    if pressure_col and 'pressure_category' in df.columns:
        st.markdown("---")
        st.markdown("### 🔽 Atmospheric Pressure Categories Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                values=pres_cat_counts.values,
                names=pres_cat_counts.index,
                title="Pressure Distribution by Category",
                color_discrete_sequence=px.colors.sequential.Blues,
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Pressure trend by category
            if temp_col:
                avg_temp_by_pressure = df.groupby('pressure_category')[temp_col].mean().sort_index()
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=avg_temp_by_pressure.index,
                    y=avg_temp_by_pressure.values,
                    marker_color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c'],
                    text=avg_temp_by_pressure.values.round(1),
                    textposition='auto'
                ))
                
                fig.update_layout(
                    title="Average Temperature by Pressure Category",
                    xaxis_title="Pressure Category",
                    yaxis_title="Average Temperature (°C)",
                    height=400,
                    plot_bgcolor='white',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Detailed pressure category breakdown
        st.markdown("#### 📊 Pressure Category Details")
        
        for category in ['Low (<1000)', 'Normal (1000-1013)', 'High (1013-1020)', 'Very High (>1020)']:
            if category in pres_cat_counts.index:
                count = pres_cat_counts[category]
                percentage = (count / len(df)) * 100
                
                if 'Low' in category:
                    color = "#e74c3c"
                    icon = "⛈️"
                    description = "Associated with storms, clouds, and precipitation"
                elif 'Normal' in category:
                    color = "#2ecc71"
                    icon = "✅"
                    description = "Standard atmospheric conditions, variable weather"
                elif 'High' in category and 'Very' not in category:
                    color = "#f39c12"
                    icon = "☀️"
                    description = "Often associated with clear skies and stable weather"
                else:
                    color = "#9b59b6"
                    icon = "🌤️"
                    description = "Very stable conditions, typically clear and dry"
                
                st.markdown(f"""
                    <div style='padding: 1rem; background: linear-gradient(135deg, {color}22 0%, {color}44 100%); 
                                border-left: 5px solid {color}; border-radius: 10px; margin: 0.5rem 0;'>
                        <h4 style='color: {color}; margin: 0;'>{icon} {category}</h4>
                        <p style='margin: 0.5rem 0 0 0; color: #2c3e50;'>
                            <strong>{count:,} data points</strong> ({percentage:.1f}%)
                        </p>
                        <p style='margin: 0.3rem 0 0 0; color: #2c3e50;'>
                            <strong>Description:</strong> {description}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
    
    # Wind vs Pressure Relationship
    if wind_col and pressure_col:
        st.markdown("---")
        st.markdown("### 🔄 Wind-Pressure Relationship")
        
        sample_data = df[[wind_col, pressure_col]].dropna().sample(min(5000, len(df)))
        
        fig = px.scatter(
            sample_data,
            x=pressure_col,
            y=wind_col,
            trendline="ols",
            color=wind_col,
            color_continuous_scale='Viridis',
            opacity=0.5,
            title="Wind Speed vs Atmospheric Pressure"
        )
        fig.update_layout(
            height=450,
            xaxis_title="Pressure (mb)",
            yaxis_title="Wind Speed (kph)",
            plot_bgcolor='white',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate correlation
        corr = df[[wind_col, pressure_col]].corr().iloc[0, 1]
        
        st.markdown(f"""
            <div class='alert-info'>
                <h4>📊 Correlation Analysis</h4>
                <p><strong>Correlation Coefficient:</strong> {corr:.3f}</p>
                <p><strong>Interpretation:</strong> {'Negative correlation - Higher pressure tends to mean lower wind speeds (typical pattern)' if corr < -0.3 else 'Positive correlation - Higher pressure tends to mean higher wind speeds (unusual pattern)' if corr > 0.3 else 'Weak correlation between pressure and wind speed'}</p>
            </div>
        """, unsafe_allow_html=True)

# TAB 11: UV INDEX & VISIBILITY WITH RELATIONSHIP AND RISK CATEGORIES

with tab11:
    st.markdown("## ☀️ UV Index & Visibility Analysis")
    
    add_interpretation(
        "Solar Radiation & Clarity",
        "UV Index measures sun radiation intensity (0-11+). Visibility shows atmospheric clarity in kilometers.",
        "UV 0-2=Low, 3-5=Moderate, 6-7=High, 8-10=Very High, 11+=Extreme. Visibility <5km=Poor, >10km=Good.",
        "High UV requires sun protection. Low visibility affects travel safety. Both vary with weather and time.",
        "Insights: (1) Sun protection needs? (2) Visibility patterns? (3) Seasonal variations? (4) Safety considerations?"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'uv_index' in df.columns:
            st.markdown("### ☀️ UV Index")
            
            uv_metrics = st.columns(3)
            with uv_metrics[0]:
                st.metric("Average", f"{df['uv_index'].mean():.1f}")
            with uv_metrics[1]:
                st.metric("Maximum", f"{df['uv_index'].max():.1f}")
            with uv_metrics[2]:
                high_uv = len(df[df['uv_index'] > 6])
                st.metric("High UV Days", f"{high_uv:,}")
            
            fig = px.histogram(df, x='uv_index', nbins=30, marginal="box", color_discrete_sequence=['#FF6B6B'])
            fig.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            # UV RISK CATEGORIES
            df['uv_category'] = pd.cut(
                df['uv_index'],
                bins=[0, 2, 5, 7, 10, 100],
                labels=['Low (0-2)', 'Moderate (3-5)', 'High (6-7)', 'Very High (8-10)', 'Extreme (11+)']
            )
            
            uv_cat_counts = df['uv_category'].value_counts()
            
            fig = px.pie(
                values=uv_cat_counts.values,
                names=uv_cat_counts.index,
                title="UV Index Distribution by Risk Level",
                color_discrete_sequence=px.colors.sequential.Reds,
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'visibility_km' in df.columns:
            st.markdown("### 👁️ Visibility")
            
            vis_metrics = st.columns(3)
            with vis_metrics[0]:
                st.metric("Average", f"{df['visibility_km'].mean():.1f} km")
            with vis_metrics[1]:
                st.metric("Maximum", f"{df['visibility_km'].max():.1f} km")
            with vis_metrics[2]:
                poor_vis = len(df[df['visibility_km'] < 5])
                st.metric("Poor Visibility", f"{poor_vis:,}")
            
            fig = px.histogram(df, x='visibility_km', nbins=30, marginal="violin", color_discrete_sequence=['#1ABC9C'])
            fig.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Visibility Categories
            df['vis_category'] = pd.cut(
                df['visibility_km'],
                bins=[0, 1, 5, 10, 1000],
                labels=['Very Poor (<1km)', 'Poor (1-5km)', 'Moderate (5-10km)', 'Good (>10km)']
            )
            
            vis_cat_counts = df['vis_category'].value_counts()
            
            fig = px.pie(
                values=vis_cat_counts.values,
                names=vis_cat_counts.index,
                title="Visibility Distribution by Category",
                color_discrete_sequence=px.colors.sequential.Teal,
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    # UV AND VISIBILITY RELATIONSHIP
    if 'uv_index' in df.columns and 'visibility_km' in df.columns:
        st.markdown("---")
        st.markdown("### 🔗 UV vs Visibility Relationship")
        
        sample_uv_vis = df[['uv_index', 'visibility_km']].dropna().sample(min(5000, len(df)))
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.scatter(
                sample_uv_vis,
                x='visibility_km',
                y='uv_index',
                trendline="ols",
                color='uv_index',
                color_continuous_scale='Reds',
                opacity=0.5,
                title="UV Index vs Visibility"
            )
            fig.update_layout(
                height=400,
                xaxis_title="Visibility (km)",
                yaxis_title="UV Index",
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Hexbin density plot
            fig = px.density_heatmap(
                sample_uv_vis,
                x='visibility_km',
                y='uv_index',
                nbinsx=30,
                nbinsy=20,
                color_continuous_scale='YlOrRd',
                title="UV-Visibility Density Map"
            )
            fig.update_layout(
                height=400,
                xaxis_title="Visibility (km)",
                yaxis_title="UV Index",
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Correlation analysis
        uv_vis_corr = df[['uv_index', 'visibility_km']].corr().iloc[0, 1]
        
        st.markdown(f"""
            <div class='alert-info'>
                <h4>🔗 UV-Visibility Correlation</h4>
                <p><strong>Correlation Coefficient:</strong> {uv_vis_corr:.3f}</p>
                <p><strong>Interpretation:</strong> {'Positive correlation - Better visibility often means higher UV levels (clear skies)' if uv_vis_corr > 0.3 else 'Negative correlation - Poor visibility associated with higher UV (unusual)' if uv_vis_corr < -0.3 else 'Weak relationship between UV and visibility'}</p>
                <p><strong>Insight:</strong> Clear days (high visibility) typically have higher UV exposure, requiring sun protection.</p>
            </div>
        """, unsafe_allow_html=True)
    
    # UV RISK CATEGORIES DETAILED ANALYSIS
    if 'uv_index' in df.columns and 'uv_category' in df.columns:
        st.markdown("---")
        st.markdown("### ☀️ UV Risk Categories - Detailed Analysis")
        
        uv_categories = ['Low (0-2)', 'Moderate (3-5)', 'High (6-7)', 'Very High (8-10)', 'Extreme (11+)']
        
        for category in uv_categories:
            if category in uv_cat_counts.index:
                count = uv_cat_counts[category]
                percentage = (count / len(df)) * 100
                
                if 'Low' in category:
                    color = "#2ecc71"
                    icon = "✅"
                    protection = "Minimal protection required"
                    recommendation = "Safe for outdoor activities"
                elif 'Moderate' in category:
                    color = "#f39c12"
                    icon = "⚠️"
                    protection = "SPF 30+, hat recommended"
                    recommendation = "Seek shade during midday hours"
                elif 'High' in category and 'Very' not in category:
                    color = "#e67e22"
                    icon = "🔶"
                    protection = "SPF 30+, hat, sunglasses required"
                    recommendation = "Reduce sun exposure 10am-4pm"
                elif 'Very High' in category:
                    color = "#e74c3c"
                    icon = "🔴"
                    protection = "SPF 50+, protective clothing essential"
                    recommendation = "Avoid sun during peak hours"
                else:  # Extreme
                    color = "#8e44ad"
                    icon = "🚨"
                    protection = "Maximum protection required"
                    recommendation = "Stay indoors during peak hours"
                
                st.markdown(f"""
                    <div style='padding: 1rem; background: linear-gradient(135deg, {color}22 0%, {color}44 100%); 
                                border-left: 5px solid {color}; border-radius: 10px; margin: 0.5rem 0;'>
                        <h4 style='color: {color}; margin: 0;'>{icon} {category}</h4>
                        <p style='margin: 0.5rem 0 0 0; color: #2c3e50;'>
                            <strong>{count:,} data points</strong> ({percentage:.1f}%)
                        </p>
                        <p style='margin: 0.3rem 0 0 0; color: #2c3e50;'>
                            <strong>Protection:</strong> {protection}
                        </p>
                        <p style='margin: 0.3rem 0 0 0; color: #2c3e50;'>
                            <strong>Recommendation:</strong> {recommendation}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
    
    # UV and Visibility over Time
    if date_col and 'uv_index' in df.columns and 'visibility_km' in df.columns:
        st.markdown("---")
        st.markdown("### 📅 Trends Over Time")
        
        df_time = df[[date_col, 'uv_index', 'visibility_km']].dropna()
        df_time = df_time.set_index(date_col)
        daily_data = df_time.resample('D').mean().dropna()
        
        if len(daily_data) > 1:
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=("UV Index Over Time", "Visibility Over Time"),
                vertical_spacing=0.12
            )
            
            fig.add_trace(
                go.Scatter(
                    x=daily_data.index, 
                    y=daily_data['uv_index'], 
                    mode='lines', 
                    name='UV Index', 
                    line=dict(color='#FF6B6B', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(255, 107, 107, 0.2)'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=daily_data.index, 
                    y=daily_data['visibility_km'], 
                    mode='lines', 
                    name='Visibility', 
                    line=dict(color='#1ABC9C', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(26, 188, 156, 0.2)'
                ),
                row=2, col=1
            )
            
            fig.update_xaxes(title_text="Date", row=2, col=1)
            fig.update_yaxes(title_text="UV Index", row=1, col=1)
            fig.update_yaxes(title_text="Visibility (km)", row=2, col=1)
            
            fig.update_layout(height=600, showlegend=False, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

# TAB 12: CLOUD COVER & WEATHER CONDITIONS

with tab12:
    st.markdown("## ☁️ Cloud Cover & Weather Analysis")
    
    # Cloud Cover Summary
    st.markdown("### ☁️ Cloud Cover Summary")
    total_records = len(df)
    if 'cloud' in df.columns:
        df['cloud_category'] = pd.cut(df['cloud'],
            bins=[-float('inf'), 20, 50, 80, float('inf')],
            labels=['Clear (<20%)', 'Partly Cloudy (20-50%)', 'Mostly Cloudy (50-80%)', 'Overcast (>80%)']
        )
        cloud_cat_counts = df['cloud_category'].value_counts()
        
        for condition, emoji in [('Clear (<20%)', '☀️'), ('Partly Cloudy (20-50%)', '🌤️'), 
                               ('Mostly Cloudy (50-80%)', '☁️'), ('Overcast (>80%)', '🌥️')]:
            if condition in cloud_cat_counts.index:
                count = cloud_cat_counts[condition]
                percentage = (count / total_records) * 100
                st.markdown(f"""
                    <div class='alert-info' style='padding: 1rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                                border-left: 5px solid #6c757d; border-radius: 10px; margin: 0.5rem 0;'>
                        <h4 style='color: #495057;'>{emoji} {condition}</h4>
                        <p style='margin: 0.3rem 0 0 0; color: #495057;'>
                            <strong>Records:</strong> {count:,} ({percentage:.2f}%)
                        </p>
                    </div>
                """, unsafe_allow_html=True)
    
    # Weather Conditions Analysis
    st.markdown("---")
    st.markdown("### 🌤️ Weather Conditions Analysis")
    
    if 'condition_text' in df.columns:
        condition_counts = df['condition_text'].value_counts().head(10)
        
        fig = px.bar(
            x=condition_counts.values, 
            y=condition_counts.index, 
            orientation='h', 
            color=condition_counts.values, 
            color_continuous_scale='Viridis',
            title="Top 10 Weather Conditions"
        )
        fig.update_layout(
            xaxis_title="Frequency", 
            yaxis_title="", 
            height=350, 
            showlegend=False, 
            plot_bgcolor='white', 
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Weather Condition with Emojis
        st.markdown("#### 🎭 Weather Breakdown")
        
        top_conditions = condition_counts.head(5)
        for condition, count in top_conditions.items():
            emoji = get_weather_emoji(condition)
            percentage = (count / len(df)) * 100
            st.markdown(f"""
                <div style='padding: 0.5rem; background: rgba(255,255,255,0.5); 
                            border-radius: 8px; margin: 0.3rem 0;'>
                    <strong>{emoji} {condition}:</strong> {count:,} records ({percentage:.1f}%)
                </div>
            """, unsafe_allow_html=True)
    
    # Cloud Cover and Temperature Relationship
    if 'cloud' in df.columns and temp_col:
        st.markdown("---")
        st.markdown("### 🌡️ Cloud Cover vs Temperature")
        
        sample_data = df[['cloud', temp_col]].dropna().sample(min(5000, len(df)))
        
        fig = px.scatter(
            sample_data,
            x='cloud',
            y=temp_col,
            trendline="lowess",
            color='cloud',
            color_continuous_scale='Greys',
            opacity=0.4,
            title="Impact of Cloud Cover on Temperature"
        )
        fig.update_layout(
            height=400,
            xaxis_title="Cloud Cover (%)",
            yaxis_title="Temperature (°C)",
            plot_bgcolor='white',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate correlation
        cloud_temp_corr = df[['cloud', temp_col]].corr().iloc[0, 1]
        
        st.markdown(f"""
            <div class='alert-info'>
                <h4>☁️ Cloud-Temperature Relationship</h4>
                <p><strong>Correlation:</strong> {cloud_temp_corr:.3f}</p>
                <p><strong>Insight:</strong> {'More clouds tend to reduce temperature (negative correlation)' if cloud_temp_corr < -0.2 else 'More clouds tend to increase temperature (positive correlation)' if cloud_temp_corr > 0.2 else 'Weak relationship between cloud cover and temperature'}</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Weather Conditions by Country
    if 'condition_text' in df.columns and country_col:
        st.markdown("---")
        st.markdown("### 🌍 Weather Patterns by Country")
        
        top_countries = df[country_col].value_counts().head(5).index
        country_weather = df[df[country_col].isin(top_countries)].groupby([country_col, 'condition_text']).size().reset_index(name='count')
        
        fig = px.sunburst(
            country_weather,
            path=[country_col, 'condition_text'],
            values='count',
            title="Weather Condition Distribution by Country",
            color='count',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# TAB 13: MACHINE LEARNING PREDICTIONS

with tab13:
    st.markdown("## 🤖 Machine Learning Predictions")
    
    add_interpretation(
        "AI-Powered Weather Forecasting",
        "Uses historical patterns to predict future temperatures based on other weather variables. Machine learning models learn relationships from data.",
        "Input current conditions (humidity, wind, pressure) → Model predicts likely temperature. Confidence intervals show uncertainty.",
        "Higher R² score = better predictions. RMSE shows average error. Use for short-term local forecasts.",
        "Applications: (1) Activity planning, (2) Travel decisions, (3) Outdoor event scheduling, (4) Quality of life assessment."
    )
    
    if temp_col and humidity_col and wind_col and pressure_col:
        st.markdown("### 🎯 Temperature Prediction Model")
        
        # Prepare data
        features = [humidity_col, wind_col, pressure_col]
        df_ml = df[features + [temp_col]].dropna()
        
        if len(df_ml) >= 100:
            X = df_ml[features].values
            y = df_ml[temp_col].values
            
            # Split data
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Train model
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            model = LinearRegression()
            model.fit(X_train_scaled, y_train)
            
            # Predictions
            y_pred = model.predict(X_test_scaled)
            
            # Metrics
            r2 = model.score(X_test_scaled, y_test)
            rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
            mae = np.mean(np.abs(y_test - y_pred))
            mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("R² Score", f"{r2:.3f}", help="Coefficient of determination (0-1, higher is better)")
            with col2:
                st.metric("RMSE", f"{rmse:.2f}°C", help="Root Mean Square Error")
            with col3:
                st.metric("MAE", f"{mae:.2f}°C", help="Mean Absolute Error")
            with col4:
                st.metric("Test Samples", f"{len(y_test):,}")
            
            # Visualization
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Actual vs Predicted")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=y_test, 
                    y=y_pred, 
                    mode='markers', 
                    name='Predictions', 
                    marker=dict(color='#667eea', opacity=0.6, size=8)
                ))
                fig.add_trace(go.Scatter(
                    x=[y_test.min(), y_test.max()], 
                    y=[y_test.min(), y_test.max()], 
                    mode='lines', 
                    name='Perfect Fit', 
                    line=dict(color='red', dash='dash', width=3)
                ))
                fig.update_layout(
                    xaxis_title="Actual Temperature (°C)", 
                    yaxis_title="Predicted Temperature (°C)", 
                    height=400, 
                    plot_bgcolor='white', 
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📉 Prediction Errors")
                errors = y_test - y_pred
                fig = px.histogram(
                    x=errors, 
                    nbins=50, 
                    color_discrete_sequence=['#e74c3c'],
                    title="Distribution of Prediction Errors"
                )
                fig.update_layout(
                    xaxis_title="Error (°C)", 
                    yaxis_title="Frequency", 
                    height=400, 
                    plot_bgcolor='white', 
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Feature importance
            st.markdown("---")
            st.markdown("### 📊 Feature Importance")
            
            importance = pd.DataFrame({
                'Feature': features,
                'Coefficient': model.coef_,
                'Abs_Coefficient': np.abs(model.coef_)
            }).sort_values('Abs_Coefficient', ascending=False)
            
            fig = px.bar(
                importance, 
                x='Feature', 
                y='Coefficient', 
                color='Coefficient', 
                color_continuous_scale='RdBu_r', 
                title="Feature Impact on Temperature Prediction"
            )
            fig.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Model Insights
            st.markdown(f"""
                <div class='alert-success'>
                    <h4>🎓 Model Insights</h4>
                    <p><strong>Model Type:</strong> Linear Regression</p>
                    <p><strong>Training Samples:</strong> {len(X_train):,}</p>
                    <p><strong>Test Samples:</strong> {len(X_test):,}</p>
                    <p><strong>Accuracy:</strong> The model explains {r2*100:.1f}% of temperature variance</p>
                    <p><strong>Error Margin:</strong> Predictions typically within ±{rmse:.1f}°C of actual values</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Interactive Predictor
            st.markdown("---")
            st.markdown("### 🎮 Interactive Temperature Predictor")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                input_hum = st.slider(
                    "Humidity (%)", 
                    float(df[humidity_col].min()), 
                    float(df[humidity_col].max()), 
                    float(df[humidity_col].mean())
                )
            with col2:
                input_wind = st.slider(
                    "Wind Speed (kph)", 
                    float(df[wind_col].min()), 
                    float(df[wind_col].max()), 
                    float(df[wind_col].mean())
                )
            with col3:
                input_pressure = st.slider(
                    "Pressure (mb)", 
                    float(df[pressure_col].min()), 
                    float(df[pressure_col].max()), 
                    float(df[pressure_col].mean())
                )
            
            if st.button("🔮 Predict Temperature", use_container_width=True):
                input_data = np.array([[input_hum, input_wind, input_pressure]])
                input_scaled = scaler.transform(input_data)
                prediction = model.predict(input_scaled)[0]
                
                # Calculate confidence interval
                ci_lower = prediction - 1.96 * rmse
                ci_upper = prediction + 1.96 * rmse
                
                st.markdown(f"""
                    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                border-radius: 15px; margin-top: 1rem;'>
                        <h2 style='color: white; margin: 0;'>Predicted Temperature</h2>
                        <p style='font-size: 3rem; color: white; font-weight: 800; margin: 1rem 0;'>{prediction:.1f}°C</p>
                        <p style='color: rgba(255,255,255,0.9); margin: 0;'>95% Confidence Interval: {ci_lower:.1f}°C - {ci_upper:.1f}°C</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Show input summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Input Humidity", f"{input_hum:.1f}%")
                with col2:
                    st.metric("Input Wind", f"{input_wind:.1f} kph")
                with col3:
                    st.metric("Input Pressure", f"{input_pressure:.1f} mb")
            
            # Random Forest Comparison
            st.markdown("---")
            st.markdown("### 🌲 Advanced Model: Random Forest")
            
            with st.spinner("Training Random Forest model..."):
                rf_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
                rf_model.fit(X_train_scaled, y_train)
                rf_pred = rf_model.predict(X_test_scaled)
                
                rf_r2 = rf_model.score(X_test_scaled, y_test)
                rf_rmse = np.sqrt(np.mean((y_test - rf_pred) ** 2))
                rf_mae = np.mean(np.abs(y_test - rf_pred))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("RF R² Score", f"{rf_r2:.3f}", f"{(rf_r2-r2)*100:.1f}%")
            with col2:
                st.metric("RF RMSE", f"{rf_rmse:.2f}°C", f"{(rmse-rf_rmse):.2f}°C")
            with col3:
                st.metric("RF MAE", f"{rf_mae:.2f}°C", f"{(mae-rf_mae):.2f}°C")
            
            # Model Comparison
            comparison_df = pd.DataFrame({
                'Model': ['Linear Regression', 'Random Forest'],
                'R² Score': [r2, rf_r2],
                'RMSE': [rmse, rf_rmse],
                'MAE': [mae, rf_mae]
            })
            
            st.markdown("#### 📈 Model Performance Comparison")
            st.dataframe(
                comparison_df.style.highlight_max(
                    subset=['R² Score'], 
                    color='lightgreen'
                ).highlight_min(
                    subset=['RMSE', 'MAE'], 
                    color='lightgreen'
                ),
                use_container_width=True
            )
        
        else:
            st.warning("⚠️ Insufficient data for machine learning. Need at least 100 complete records.")
    else:
        st.info("ℹ️ Temperature, humidity, wind, and pressure data required for predictions.")

# TAB 14: ASTRONOMICAL DATA WITH DAYLIGHT AND MOON ANALYSIS

with tab14:
    st.markdown("## 🌙 Astronomical Data Analysis")
    
    add_interpretation(
        "Celestial Events & Patterns",
        "Tracks sunrise, sunset, moonrise, moonset, moon phases, and illumination. Helps understand day length and lunar cycles.",
        "Daylight hours = sunset - sunrise. Moon illumination = 0% (new) to 100% (full). Phases cycle every ~29.5 days.",
        "Longer daylight in summer, shorter in winter. Moon affects tides and some behaviors. Useful for planning outdoor activities.",
        "Applications: (1) Photography timing, (2) Tide predictions, (3) Activity planning, (4) Agricultural cycles."
    )
    
    astro_cols = [col for col in df.columns if any(x in col.lower() for x in ['sunrise', 'sunset', 'moonrise', 'moonset', 'moon'])]
    
    if len(astro_cols) > 0:
        if 'sunrise' in df.columns and 'sunset' in df.columns:
            st.markdown("### ☀️ Daylight Analysis")
            
            df_astro = df.copy()
            
            # Parse sunrise/sunset times
            if df_astro['sunrise'].dtype == 'object':
                df_astro['sunrise_time'] = pd.to_datetime(df_astro['sunrise'], format='%I:%M %p', errors='coerce')
                df_astro['sunset_time'] = pd.to_datetime(df_astro['sunset'], format='%I:%M %p', errors='coerce')
            else:
                df_astro['sunrise_time'] = pd.to_datetime(df_astro['sunrise'], errors='coerce')
                df_astro['sunset_time'] = pd.to_datetime(df_astro['sunset'], errors='coerce')
            
            df_astro['daylight_hours'] = (df_astro['sunset_time'] - df_astro['sunrise_time']).dt.total_seconds() / 3600
            
            if df_astro['daylight_hours'].notna().sum() > 0:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_daylight = df_astro['daylight_hours'].mean()
                    st.metric("Avg Daylight", f"{avg_daylight:.1f} hrs")
                with col2:
                    max_daylight = df_astro['daylight_hours'].max()
                    st.metric("Max Daylight", f"{max_daylight:.1f} hrs")
                with col3:
                    min_daylight = df_astro['daylight_hours'].min()
                    st.metric("Min Daylight", f"{min_daylight:.1f} hrs")
                with col4:
                    std_daylight = df_astro['daylight_hours'].std()
                    st.metric("Variability", f"{std_daylight:.1f} hrs")
                
                # NEW: DAYLIGHT HOURS OVER TIME
                if date_col:
                    st.markdown("---")
                    st.markdown("### 📅 Daylight Hours Over Time")
                    
                    df_daylight = df_astro[[date_col, 'daylight_hours']].dropna()
                    df_daylight = df_daylight.set_index(date_col)
                    daily_daylight = df_daylight.resample('D').mean().dropna()
                    
                    if len(daily_daylight) > 1:
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=daily_daylight.index,
                            y=daily_daylight['daylight_hours'],
                            mode='lines+markers',
                            name='Daylight Hours',
                            line=dict(color='#f39c12', width=2),
                            marker=dict(size=4),
                            fill='tozeroy',
                            fillcolor='rgba(243, 156, 18, 0.2)'
                        ))
                        
                        # Add seasonal markers
                        fig.add_hline(y=12, line_dash="dash", line_color="gray", 
                                     annotation_text="12 Hours (Equinox)", annotation_position="right")
                        
                        fig.update_layout(
                            title="Daylight Duration Throughout the Year",
                            xaxis_title="Date",
                            yaxis_title="Daylight Hours",
                            height=450,
                            plot_bgcolor='white',
                            paper_bgcolor='rgba(0,0,0,0)',
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Seasonal analysis
                        if 'month' in df_astro.columns or date_col in df_astro.columns:
                            if 'month' not in df_astro.columns:
                                df_astro['month'] = pd.to_datetime(df_astro[date_col]).dt.month
                            
                            monthly_daylight = df_astro.groupby('month')['daylight_hours'].mean()
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                longest_month = monthly_daylight.idxmax()
                                longest_hours = monthly_daylight.max()
                                month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                                             7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
                                
                                st.markdown(f"""
                                    <div class='alert-warning'>
                                        <h4>☀️ Longest Days</h4>
                                        <p><strong>Month:</strong> {month_names.get(longest_month, longest_month)}</p>
                                        <p><strong>Average Daylight:</strong> {longest_hours:.1f} hours</p>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                shortest_month = monthly_daylight.idxmin()
                                shortest_hours = monthly_daylight.min()
                                
                                st.markdown(f"""
                                    <div class='alert-info'>
                                        <h4>🌙 Shortest Days</h4>
                                        <p><strong>Month:</strong> {month_names.get(shortest_month, shortest_month)}</p>
                                        <p><strong>Average Daylight:</strong> {shortest_hours:.1f} hours</p>
                                    </div>
                                """, unsafe_allow_html=True)
                
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
                    fig.add_vline(x=avg_daylight, line_dash="dash", line_color="red", annotation_text=f"Mean: {avg_daylight:.1f}h")
                    fig.update_layout(
                        height=400,
                        plot_bgcolor='white',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
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
        
        # ENHANCED MOON PHASE ANALYSIS
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
                    color_discrete_sequence=px.colors.sequential.Bluyl,
                    title="Moon Phase Proportions",
                    hole=0.4
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            # Moon phase details
            st.markdown("#### 🌙 Moon Phase Guide")
            
            moon_phase_info = {
                'New Moon': ('🌑', 'Invisible moon, darkest night', '#1a1a1a'),
                'Waxing Crescent': ('🌒', 'Growing sliver of light', '#3d3d3d'),
                'First Quarter': ('🌓', 'Half moon, right side lit', '#666666'),
                'Waxing Gibbous': ('🌔', 'More than half, growing', '#999999'),
                'Full Moon': ('🌕', 'Completely illuminated', '#f1f1f1'),
                'Waning Gibbous': ('🌖', 'More than half, shrinking', '#cccccc'),
                'Last Quarter': ('🌗', 'Half moon, left side lit', '#999999'),
                'Waning Crescent': ('🌘', 'Fading sliver of light', '#666666')
            }
            
            for phase in moon_counts.index:
                if phase in moon_phase_info:
                    emoji, description, color = moon_phase_info[phase]
                    count = moon_counts[phase]
                    percentage = (count / len(df)) * 100
                    
                    st.markdown(f"""
                        <div style='padding: 0.8rem; background: linear-gradient(135deg, {color}33 0%, {color}55 100%); 
                                    border-left: 5px solid {color}; border-radius: 10px; margin: 0.5rem 0;'>
                            <h4 style='color: {color}; margin: 0; filter: brightness(0.7);'>{emoji} {phase}</h4>
                            <p style='margin: 0.3rem 0 0 0; color: #2c3e50;'>
                                <strong>{count:,} occurrences</strong> ({percentage:.1f}%)
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
        
        if 'moon_illumination' in df.columns:
            st.markdown("---")
            st.markdown("### 🌕 Moon Illumination")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_illum = df['moon_illumination'].mean()
                st.metric("Avg Illumination", f"{avg_illum:.1f}%")
            with col2:
                full_moon = len(df[df['moon_illumination'] > 95])
                st.metric("Full Moon", f"{full_moon:,}")
            with col3:
                new_moon = len(df[df['moon_illumination'] < 5])
                st.metric("New Moon", f"{new_moon:,}")
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
                            fill='tozeroy',
                            fillcolor='rgba(155, 89, 182, 0.2)'
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

            # Moon Phase Calendar
            st.markdown("---")
            st.markdown("### 📅 Lunar Calendar Visualization")
            
            df_moon_phases = df[['moon_illumination']].copy()
            df_moon_phases['phase_name'] = df_moon_phases['moon_illumination'].apply(
                lambda x: 'New Moon' if x < 5 else 
                         'Waxing Crescent' if x < 25 else
                         'First Quarter' if x < 35 else
                         'Waxing Gibbous' if x < 45 else
                         'Full Moon' if x > 95 else
                         'Waning Gibbous' if x > 75 else
                         'Last Quarter' if x > 65 else
                         'Waning Crescent'
            )
            
            phase_counts = df_moon_phases['phase_name'].value_counts()
            
            fig = px.bar(
                x=phase_counts.index,
                y=phase_counts.values,
                color=phase_counts.values,
                color_continuous_scale='Purples',
                title="Distribution of Moon Phases"
            )
            fig.update_layout(
                height=350,
                xaxis_title="Moon Phase",
                yaxis_title="Frequency",
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No astronomical data found in dataset.")
        st.info("💡 Astronomical data typically includes sunrise, sunset, moon phase, and moon illumination information.")

# TAB 15: COMFORT INDEX ANALYSIS

with tab15:
    st.markdown("## 😊 Comfort Index Analysis")
    add_interpretation(
        "Weather Comfort Assessment",
        "Combines temperature, humidity, and wind to calculate overall comfort levels. Higher scores = more comfortable conditions.",
        "Comfort Index considers multiple factors: ideal temperature (18-25°C), comfortable humidity (40-60%), moderate wind (<20 kph).",
        "Score 0-100: 0-30=Poor, 30-50=Fair, 50-70=Good, 70-85=Very Good, 85-100=Excellent.",
        "Use for: (1) Activity planning, (2) Travel decisions, (3) Outdoor event scheduling, (4) Quality of life assessment."
    )
    
    if temp_col and humidity_col and wind_col:
        # Calculate Comfort Index
        def calculate_comfort_index(row):
            score = 50  # Base score
            
            # Temperature component (max 30 points)
            temp = row[temp_col]
            if 18 <= temp <= 25:
                score += 30
            elif 15 <= temp < 18 or 25 < temp <= 28:
                score += 20
            elif 10 <= temp < 15 or 28 < temp <= 32:
                score += 10
            else:
                score -= 10
            
            # Humidity component (max 25 points)
            hum = row[humidity_col]
            if 40 <= hum <= 60:
                score += 25
            elif 30 <= hum < 40 or 60 < hum <= 70:
                score += 15
            elif 20 <= hum < 30 or 70 < hum <= 80:
                score += 5
            else:
                score -= 10
            
            # Wind component (max 20 points)
            wind = row[wind_col]
            if wind < 10:
                score += 20
            elif 10 <= wind < 20:
                score += 15
            elif 20 <= wind < 30:
                score += 5
            else:
                score -= 10
            
            # Pressure bonus (if available)
            if pressure_col in row.index:
                pressure = row[pressure_col]
                if 1010 <= pressure <= 1020:
                    score += 5
            
            return max(0, min(100, score))
        
        df['comfort_index'] = df.apply(calculate_comfort_index, axis=1)
        
        # Comfort Categories
        df['comfort_category'] = pd.cut(
            df['comfort_index'],
            bins=[0, 30, 50, 70, 85, 100],
            labels=['Poor', 'Fair', 'Good', 'Very Good', 'Excellent']
        )
        
        # Overall Statistics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            avg_comfort = df['comfort_index'].mean()
            st.metric("Average Index", f"{avg_comfort:.1f}")
        with col2:
            max_comfort = df['comfort_index'].max()
            st.metric("Maximum", f"{max_comfort:.1f}")
        with col3:
            min_comfort = df['comfort_index'].min()
            st.metric("Minimum", f"{min_comfort:.1f}")
        with col4:
            excellent_days = len(df[df['comfort_category'] == 'Excellent'])
            st.metric("Excellent Days", f"{excellent_days:,}")
        with col5:
            poor_days = len(df[df['comfort_category'] == 'Poor'])
            st.metric("Poor Days", f"{poor_days:,}")
        
        st.markdown("---")
        
        # Comfort Index Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Comfort Index Distribution")
            
            fig = px.histogram(
                df,
                x='comfort_index',
                nbins=50,
                marginal="box",
                color_discrete_sequence=['#2ecc71'],
                title="Comfort Index Frequency"
            )
            fig.add_vline(x=avg_comfort, line_dash="dash", line_color="red", 
                         annotation_text=f"Mean: {avg_comfort:.1f}")
            fig.update_layout(
                height=400,
                xaxis_title="Comfort Index (0-100)",
                yaxis_title="Frequency",
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📋 Comfort Categories")
            
            comfort_cat_counts = df['comfort_category'].value_counts()
            
            fig = px.pie(
                values=comfort_cat_counts.values,
                names=comfort_cat_counts.index,
                title="Comfort Level Distribution",
                color_discrete_sequence=px.colors.diverging.RdYlGn,
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True, key="comfort_categories_pie")
        
        # Comfort Index Over Time
        if date_col:
            st.markdown("---")
            st.markdown("### 📅 Comfort Index Over Time")
            
            df_comfort = df[[date_col, 'comfort_index']].dropna()
            df_comfort = df_comfort.set_index(date_col)
            daily_comfort = df_comfort.resample('D').mean().dropna()
            
            if len(daily_comfort) > 1:
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=daily_comfort.index,
                    y=daily_comfort['comfort_index'],
                    mode='lines+markers',
                    name='Comfort Index',
                    line=dict(color='#2ecc71', width=2),
                    marker=dict(size=5),
                    fill='tozeroy',
                    fillcolor='rgba(46, 204, 113, 0.2)'
                ))
                
                # Add comfort zones
                fig.add_hrect(y0=85, y1=100, fillcolor="green", opacity=0.1, 
                             annotation_text="Excellent", annotation_position="top left")
                fig.add_hrect(y0=70, y1=85, fillcolor="lightgreen", opacity=0.1, 
                             annotation_text="Very Good", annotation_position="top left")
                fig.add_hrect(y0=50, y1=70, fillcolor="yellow", opacity=0.1, 
                             annotation_text="Good", annotation_position="top left")
                fig.add_hrect(y0=30, y1=50, fillcolor="orange", opacity=0.1, 
                             annotation_text="Fair", annotation_position="top left")
                fig.add_hrect(y0=0, y1=30, fillcolor="red", opacity=0.1, 
                             annotation_text="Poor", annotation_position="bottom left")
                
                # Add 7-day moving average
                if len(daily_comfort) >= 7:
                    ma7 = daily_comfort['comfort_index'].rolling(window=7).mean()
                    fig.add_trace(go.Scatter(
                        x=ma7.index,
                        y=ma7.values,
                        mode='lines',
                        name='7-Day MA',
                        line=dict(color='#e74c3c', width=3, dash='dash')
                    ))
                
                fig.update_layout(
                    title="Daily Comfort Index with Comfort Zones",
                    xaxis_title="Date",
                    yaxis_title="Comfort Index",
                    height=450,
                    plot_bgcolor='white',
                    paper_bgcolor='rgba(0,0,0,0)',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Comfort by Country
        if country_col:
            st.markdown("---")
            st.markdown("### 🌍 Comfort Index by Country")
            
            country_comfort = df.groupby(country_col)['comfort_index'].mean().sort_values(ascending=False).head(15)
            
            fig = px.bar(
                x=country_comfort.values,
                y=country_comfort.index,
                orientation='h',
                color=country_comfort.values,
                color_continuous_scale='RdYlGn',
                title="Top 15 Countries by Average Comfort Index"
            )
            fig.update_layout(
                height=500,
                xaxis_title="Average Comfort Index",
                yaxis_title="Country",
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed Category Breakdown
        st.markdown("---")
        st.markdown("### 📊 Comfort Category Breakdown")
        
        comfort_categories = ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent']
        
        for category in comfort_categories:
            if category in comfort_cat_counts.index:
                count = comfort_cat_counts[category]
                percentage = (count / len(df)) * 100
                
                if category == 'Excellent':
                    color = "#27ae60"
                    icon = "😄"
                    description = "Perfect weather conditions for all outdoor activities"
                    recommendation = "Ideal time for sports, hiking, and outdoor events"
                elif category == 'Very Good':
                    color = "#2ecc71"
                    icon = "😊"
                    description = "Highly comfortable conditions with minor variations"
                    recommendation = "Great for most outdoor activities"
                elif category == 'Good':
                    color = "#f39c12"
                    icon = "🙂"
                    description = "Acceptable conditions with some discomfort factors"
                    recommendation = "Suitable for outdoor activities with precautions"
                elif category == 'Fair':
                    color = "#e67e22"
                    icon = "😐"
                    description = "Uncomfortable conditions, some factors beyond ideal range"
                    recommendation = "Limit exposure, take breaks indoors"
                else:  # Poor
                    color = "#e74c3c"
                    icon = "😞"
                    description = "Very uncomfortable weather conditions"
                    recommendation = "Avoid prolonged outdoor exposure, stay indoors"
                
                st.markdown(f"""
                    <div style='padding: 1rem; background: linear-gradient(135deg, {color}22 0%, {color}44 100%); 
                                border-left: 5px solid {color}; border-radius: 10px; margin: 0.5rem 0;'>
                        <h4 style='color: {color}; margin: 0;'>{icon} {category} Comfort</h4>
                        <p style='margin: 0.5rem 0 0 0; color: #2c3e50;'>
                            <strong>{count:,} data points</strong> ({percentage:.1f}%)
                        </p>
                        <p style='margin: 0.3rem 0 0 0; color: #2c3e50;'>
                            <strong>Description:</strong> {description}
                        </p>
                        <p style='margin: 0.3rem 0 0 0; color: #2c3e50;'>
                            <strong>Recommendation:</strong> {recommendation}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
        
        # Comfort Index Components Analysis
        st.markdown("---")
        st.markdown("### 🔍 Comfort Components Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Temperature comfort distribution
            df['temp_comfort'] = df[temp_col].apply(
                lambda x: 'Ideal' if 18 <= x <= 25 else 'Good' if 15 <= x < 18 or 25 < x <= 28 else 'Fair' if 10 <= x < 15 or 28 < x <= 32 else 'Poor'
            )
            temp_comfort_counts = df['temp_comfort'].value_counts()
            
            fig = px.pie(
                values=temp_comfort_counts.values,
                names=temp_comfort_counts.index,
                title="Temperature Comfort",
                color_discrete_sequence=px.colors.sequential.Reds
            )
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Humidity comfort distribution
            df['hum_comfort'] = df[humidity_col].apply(
                lambda x: 'Ideal' if 40 <= x <= 60 else 'Good' if 30 <= x < 40 or 60 < x <= 70 else 'Fair' if 20 <= x < 30 or 70 < x <= 80 else 'Poor'
            )
            hum_comfort_counts = df['hum_comfort'].value_counts()
            
            fig = px.pie(
                values=hum_comfort_counts.values,
                names=hum_comfort_counts.index,
                title="Humidity Comfort",
                color_discrete_sequence=px.colors.sequential.Blues
            )
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Wind comfort distribution
            df['wind_comfort'] = df[wind_col].apply(
                lambda x: 'Ideal' if x < 10 else 'Good' if 10 <= x < 20 else 'Fair' if 20 <= x < 30 else 'Poor'
            )
            wind_comfort_counts = df['wind_comfort'].value_counts()
            
            fig = px.pie(
                values=wind_comfort_counts.values,
                names=wind_comfort_counts.index,
                title="Wind Comfort",
                color_discrete_sequence=px.colors.sequential.Greens
            )
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
        # 3D Comfort Visualization
        st.markdown("---")
        st.markdown("### 📐 3D Comfort Space")

        sample_3d = df[[temp_col, humidity_col, wind_col, 'comfort_index']].dropna().sample(min(2000, len(df)))

        fig = px.scatter_3d(
            sample_3d,
            x=temp_col,
            y=humidity_col,
            z=wind_col,
            color='comfort_index',
            color_continuous_scale='RdYlGn',
            opacity=0.7,
            title="Comfort Index in 3D Weather Space",
            labels={
                temp_col: 'Temperature (°C)',
                humidity_col: 'Humidity (%)',
                wind_col: 'Wind Speed (kph)',
                'comfort_index': 'Comfort Index'
            }
        )

        # Update layout with explicit scene settings
        fig.update_layout(
            height=600,
            scene=dict(
                xaxis_title='Temperature (°C)',
                yaxis_title='Humidity (%)',
                zaxis_title='Wind Speed (kph)',
                bgcolor='#0d1117',
                xaxis=dict(backgroundcolor='#161b22', gridcolor='#30363d', showbackground=True),
                yaxis=dict(backgroundcolor='#161b22', gridcolor='#30363d', showbackground=True),
                zaxis=dict(backgroundcolor='#161b22', gridcolor='#30363d', showbackground=True)
            ),
            paper_bgcolor='#0d1117',
            plot_bgcolor='#0d1117',
            font=dict(color='#e6edf3')
        )

        st.plotly_chart(fig, use_container_width=True, key="comfort_3d_unique")
        
        st.markdown("""
            <div class='interpretation-box'>
                <h4>🎯 How to Use Comfort Index</h4>
                <p><strong>Planning Activities:</strong> Choose days with Comfort Index > 70 for outdoor events</p>
                <p><strong>Travel Decisions:</strong> Target destinations with consistently high comfort scores</p>
                <p><strong>Health Considerations:</strong> Avoid prolonged exposure on days with Poor comfort</p>
                <p><strong>Seasonal Patterns:</strong> Identify best months for outdoor activities in your region</p>
            </div>
        """, unsafe_allow_html=True)
    
    else:
        st.warning("⚠️ Comfort Index requires temperature, humidity, and wind speed data.")
        st.info("💡 Please ensure your dataset contains these variables for comfort analysis.")

# --------------------------- EXPORT / DOWNLOADS ---------------------------
# Export utilities: buttons and download helpers for CSV exports. These
# controls provide quick downloads for computed statistics, regional
# aggregations, extremes, and full filtered datasets. Buttons are grouped in
# a 4-column layout for convenience.
st.markdown("---")
st.markdown("## 💾 Export Data & Reports")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 Statistics", use_container_width=True):
        stats = df.select_dtypes(include=[np.number]).describe()
        csv = stats.to_csv()
        st.download_button(
            "📥 Download Statistics", 
            csv, 
            f"statistics_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", 
            "text/csv", 
            use_container_width=True
        )

with col2:
    if st.button("🔥 Extremes", use_container_width=True):
        if 'extreme_results' in locals() and extreme_results:
            all_ext = pd.DataFrame()
            if 'Temperature' in extreme_results:
                all_ext = pd.concat([
                    extreme_results.get('Temperature', {}).get('high_data', pd.DataFrame()),
                    extreme_results.get('Temperature', {}).get('low_data', pd.DataFrame())
                ])
            if len(all_ext) > 0:
                csv = all_ext.to_csv(index=False)
                st.download_button(
                    "📥 Download Extremes", 
                    csv, 
                    f"extremes_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", 
                    "text/csv", 
                    use_container_width=True
                )
            else:
                st.info("No extreme events detected with current settings")

with col3:
    if st.button("🌍 Regional", use_container_width=True):
        if country_col and temp_col:
            agg_dict = {temp_col: ['mean', 'std', 'min', 'max', 'count']}
            if wind_col:
                agg_dict[wind_col] = ['mean', 'max']
            if humidity_col:
                agg_dict[humidity_col] = ['mean']
            
            stats = df.groupby(country_col).agg(agg_dict).reset_index()
            csv = stats.to_csv(index=False)
            st.download_button(
                "📥 Download Regional", 
                csv, 
                f"regional_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", 
                "text/csv", 
                use_container_width=True
            )

    if 'uv_index' in df.columns and 'visibility_km' in df.columns:
        if st.button("🌞 UV & Visibility", use_container_width=True):
            daily_data = df.set_index(date_col).sort_index()[['uv_index', 'visibility_km']].resample('D').mean().dropna()
            csv = daily_data.to_csv()
            st.download_button(
                "📥 Download UV & Visibility Data", 
                csv, 
                f"uv_visibility_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", 
                "text/csv", 
                use_container_width=True
            )        

with col4:
    if st.button("📋 Full Data", use_container_width=True):
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download Full Dataset", 
            csv, 
            f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", 
            "text/csv", 
            use_container_width=True
        )

    # Time Series Data Export
    if date_col:
        if st.button("⏳ Time Series", use_container_width=True):
            df_time = df.set_index(date_col).sort_index()
            csv = df_time.to_csv()
            st.download_button(
                "📥 Download Time Series Data", 
                csv, 
                f"time_series_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", 
                "text/csv", 
                use_container_width=True
            )

# --------------------------- DOCUMENTATION & HELP -------------------------

with st.expander("📚 Documentation & Help"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔑 Kaggle API Setup
        
        To enable automatic data fetching from Kaggle:
        
        1. Get your API token from kaggle.com/settings
        2. Create `~/.kaggle/kaggle.json` with your credentials
        3. Run: `chmod 600 ~/.kaggle/kaggle.json` (Linux/Mac)
        
        Format:
            {"username":"your_username","key":"your_api_key"}

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
        - **Machine learning predictions** for temperature
        - **14 comprehensive analysis tabs**
        
        ### 📊 Tab Overview
        
        1. **Dashboard** - Executive summary with KPIs
        2. **Statistics** - Descriptive stats and data quality
        3. **Distributions** - Histograms and density plots
        4. **Extremes** - Anomaly detection system
        5. **City Analysis** - Comparative city weather
        6. **Time Series** - Temporal trends and patterns
        7. **Correlations** - Variable relationships
        8. **Maps** - Geographic visualizations
        9. **Humidity** - Moisture analysis
        10. **Wind & Pressure** - Atmospheric dynamics
        11. **UV & Visibility** - Solar and clarity metrics
        12. **Cloud & Weather** - Sky conditions
        13. **Predictions** - ML-based forecasting
        14. **Astronomical** - Sun and moon data
        
        \n

        ### 🎓 Advanced Features
        
        **Filtering:**
        - Multi-country selection with search
        - Date range picker for temporal analysis
        - Slider-based numeric filters
        - Weather condition filtering
        
        **Visualizations:**
        - Interactive Plotly charts
        - Zoom, pan, and hover tooltips
        - Multiple chart types per analysis
        - Downloadable as images
        
        **Statistical Methods:**
        - Descriptive statistics
        - Correlation analysis
        - Normality testing
        - Skewness and kurtosis
        
        **Machine Learning:**
        - Feature scaling (StandardScaler)
        - Train/test split (80/20)
        - Multiple algorithms
        - Cross-validation metrics
                                
        """)
    
    with col2:
        st.markdown("""
        
        ### 📊 Understanding Metrics
        
        **Temperature Metrics:**
        - Measured in Celsius
        - Measured in Celsius (°C)
        - Global average typically 15-20°C
        - Extreme: <-20°C or >40°C
        
        **Wind Speed:**
        - Measured in kilometers per hour (kph)
        - Average ranges 10-30 kph
        - Strong wind: >50 kph
        - Storm: >89 kph
        
        **Humidity:**
        - Percentage of moisture in air (0-100%)
        - Comfortable: 40-60%
        - Dry: <30%, Humid: >70%
        
        **Pressure:**
        - Measured in millibars (mb)
        - Standard: ~1013 mb
        - Low pressure: <1000 mb (storms)
        - High pressure: >1020 mb (clear)
        
        **UV Index:**
        - Scale 0-11+ measuring solar radiation
        - Low: 0-2, Moderate: 3-5, High: 6-7
        - Very High: 8-10, Extreme: 11+
        
        **Extreme Events:**
        - Detected using statistical thresholds
        - 3σ = 99.7% confidence level
        - Adjustable sensitivity slider
        - Identifies outliers and anomalies
        
        **ML Predictions:**
        - R² score shows model accuracy (0-1)
        - RMSE shows prediction error
        - Linear Regression for interpretability
        - Random Forest for accuracy
        
        ### 💡 Pro Tips
        
        - Use **Daily aggregation** for detailed time series
        - Adjust **extreme event threshold** for sensitivity
        - Compare **multiple countries** in Regional Intelligence
        - Use **ML predictor** for scenario planning
        - **Export data** at any analysis stage
        - **Reset filters** to start fresh analysis

        
        ### 🔧 Troubleshooting
        
        **No data showing?**
        - Check if filters are too restrictive
        - Reset all filters using sidebar button
        - Verify CSV file is loaded correctly
        
        **Charts not rendering?**
        - Refresh the page
        - Check internet connection (for CDN resources)
        - Try different browser
        
        **Slow performance?**
        - Reduce date range
        - Select fewer countries
        - Use weekly/monthly aggregation
        
        **Export not working?**
        - Check browser download permissions
        - Ensure sufficient disk space
        - Try different export format
        
        ### 📖 Data Dictionary
        
        **Required Columns:**
        - `temperature_celsius` or `temp_c` - Temperature in Celsius
        - `country` - Country name
        - `location_name` or `name` - City/location name
        - `last_updated` - Timestamp of record
        
        **Optional Columns:**
        - `humidity` - Relative humidity percentage
        - `wind_kph` - Wind speed in km/h
        - `pressure_mb` - Atmospheric pressure in millibars
        - `uv_index` - UV radiation index
        - `visibility_km` - Visibility in kilometers
        - `cloud` - Cloud cover percentage
        - `condition_text` - Weather description
        - `sunrise` / `sunset` - Solar times
        - `moon_phase` / `moon_illumination` - Lunar data
        """)

st.markdown("---")

# ------------------------------- FOOTER ---------------------------------

st.markdown(f"""
    <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; color: white; box-shadow: 0 10px 20px rgba(0,0,0,0.1);'>
        <h2 style='color: white; margin: 0;'>🌍 ClimateScope</h2>
        <h4 style='color: white; margin-top: 10px;'>Advanced Weather Intelligence Platform</h4>
        <p style='margin-top: 20px;'><strong>Last Updated:</strong> {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        <p><strong>Active Data Points:</strong> {len(df):,} | <strong>Countries:</strong> {df[country_col].nunique() if country_col else 'N/A'} | <strong>Locations:</strong> {df[location_col].nunique() if location_col else 'N/A'}</p>
        <div style='margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;'>
            <p style='margin: 5px 0; font-size: 0.9em;'>✅ Real-time Analytics | 📊 Advanced Statistics | 🔥 Extreme Event Detection & Logs</p>
            <p style='margin: 5px 0; font-size: 0.9em;'>🌐 Regional Intelligence | 📅 Time Series with Wind Trends | 🗺️ Black Background Maps</p>
            <p style='margin: 5px 0; font-size: 0.9em;'>🤖 Machine Learning | 🏙️ City-Level Analysis | 🌙 Astronomical Data | 😊 Comfort Index</p>
            <p style='margin: 5px 0; font-size: 0.9em;'>📡 Radar Charts | 🔬 Scatter Analysis | 🧭 Wind Direction | 🌧️ Precipitation Analysis</p>
        </div>
        <p style='margin-top: 20px; font-size: 0.85em; opacity: 0.9;'>Powered by Streamlit • Plotly • Pandas • NumPy • Scikit-learn</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 10px; margin-top: 20px;'>
        <p style='color: #6c757d; margin: 0; font-size: 0.9em;'>
            <strong>ClimateScope</strong> | Weather Analytics Platform for Professionals & Enterprises
        </p>
        <p style='color: #adb5bd; margin: 5px 0; font-size: 0.8em;'>
            © 2025 ClimateScope | All Rights Reserved | Empowering Climate Intelligence Worldwide
        </p>
    </div>
""", unsafe_allow_html=True)

# -------------------- ADDITIONAL FEATURES & ENHANCEMENTS ------------------
# Small runtime features to improve UX: session-state history, cache
# management and performance-related controls. These are non-essential
# enhancements but help during interactive exploratory analysis.

# Add session state for advanced features
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# Add timestamp to history
st.session_state.analysis_history.append({
    'timestamp': datetime.now(),
    'records': len(df),
    'countries': df[country_col].nunique() if country_col else 0,
    'cities': df[location_col].nunique() if location_col else 0
})

# Keep only last 10 analyses
if len(st.session_state.analysis_history) > 10:
    st.session_state.analysis_history = st.session_state.analysis_history[-10:]

# PERFORMANCE OPTIMIZATION

# Cache clearing option (hidden in expander)
with st.expander("⚙️ Advanced Settings"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("Cache cleared successfully!")
            st.rerun()
    
    with col2:
        show_debug = st.checkbox("🐛 Debug Mode")
        if show_debug:
            st.write("**Session State:**")
            st.json({
                'total_records': len(df),
                'filtered_records': len(df),
                'columns': len(df.columns),
                'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
            })
    
    with col3:
        if st.button("📊 Analysis Summary", use_container_width=True):
            st.markdown(f"""
                <div class='alert-info'>
                    <h4>📈 Analysis Session Summary</h4>
                    <p><strong>Total Analyses:</strong> {len(st.session_state.analysis_history)}</p>
                    <p><strong>Current Records:</strong> {len(df):,}</p>
                    <p><strong>Data Quality:</strong> {(df.notna().sum().sum() / (len(df) * len(df.columns)) * 100):.1f}% complete</p>
                </div>
            """, unsafe_allow_html=True)

# DATA QUALITY INDICATORS

st.markdown("---")
st.markdown("### 🎯 Data Quality Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    completeness = (df.notna().sum().sum() / (len(df) * len(df.columns)) * 100)
    st.metric("Data Completeness", f"{completeness:.1f}%")

with col2:
    if temp_col:
        temp_quality = (df[temp_col].notna().sum() / len(df) * 100)
        st.metric("Temperature Data", f"{temp_quality:.1f}%")

with col3:
    if date_col:
        date_range_days = (df[date_col].max() - df[date_col].min()).days
        st.metric("Date Range", f"{date_range_days} days")

with col4:
    duplicates = df.duplicated().sum()
    st.metric("Duplicates", f"{duplicates:,}")

with col5:
    if country_col:
        coverage = df[country_col].nunique()
        st.metric("Geographic Coverage", f"{coverage} countries")

# QUICK INSIGHTS PANEL

st.markdown("---")
st.markdown("### 💡 Quick Insights")

insights = []

# Temperature insights
if temp_col:
    avg_temp = df[temp_col].mean()
    if avg_temp > 25:
        insights.append("🔥 Overall temperature is relatively high across selected regions")
    elif avg_temp < 15:
        insights.append("❄️ Overall temperature is relatively low across selected regions")
    else:
        insights.append("🌡️ Temperature levels are moderate across selected regions")

# Humidity insights
if humidity_col:
    avg_hum = df[humidity_col].mean()
    if avg_hum > 70:
        insights.append("💧 High humidity levels detected - conditions may feel uncomfortable")
    elif avg_hum < 40:
        insights.append("🏜️ Low humidity levels - dry conditions prevail")

# Wind insights
if wind_col:
    avg_wind = df[wind_col].mean()
    if avg_wind > 30:
        insights.append("💨 Strong wind conditions are common in this dataset")
    
# Data coverage insights
if country_col and location_col:
    countries = df[country_col].nunique()
    cities = df[location_col].nunique()
    if cities / countries > 10:
        insights.append(f"🌆 Rich city-level data available ({cities} cities across {countries} countries)")

# Temporal insights
if date_col:
    date_span = (df[date_col].max() - df[date_col].min()).days
    if date_span > 365:
        insights.append(f"📅 Multi-year dataset spanning {date_span} days")
    elif date_span > 90:
        insights.append(f"📆 Seasonal analysis possible with {date_span} days of data")

# Display insights
if insights:
    for insight in insights:
        st.markdown(f"""
            <div style='padding: 0.8rem; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                        border-left: 4px solid #2196f3; border-radius: 8px; margin: 0.5rem 0;'>
                <p style='margin: 0; color: #1565c0; font-weight: 500;'>{insight}</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("💡 Apply filters to generate insights about your data")

# KEYBOARD SHORTCUTS INFO

st.markdown("---")
with st.expander("⌨️ Keyboard Shortcuts & Tips"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎹 Keyboard Shortcuts
        
        - **R** - Rerun the application
        - **Ctrl/Cmd + K** - Focus search bar
        - **Esc** - Close modal/expander
        - **Tab** - Navigate between elements
        - **Shift + Tab** - Navigate backwards
        
        ### 🖱️ Mouse Interactions
        
        - **Click & Drag** - Pan charts
        - **Scroll** - Zoom in/out on charts
        - **Double Click** - Reset chart view
        - **Hover** - Show detailed tooltips
        """)
    
    with col2:
        st.markdown("""
        ### 🎨 Visualization Tips
        
        - Use **color gradients** to spot patterns
        - Look for **outliers** in scatter plots
        - Check **trend lines** for direction
        - Compare **box plots** for variability
        
        ### 📊 Analysis Tips
        
        - Start with **Dashboard** for overview
        - Use **Correlations** to find relationships
        - Check **Extremes** for unusual events
        - Validate with **Statistics** tab
        - Export findings for reports
        """)


# PERFORMANCE METRICS


st.markdown("---")

with st.expander("⚡ Performance Metrics"):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Data Points", f"{len(df):,}")
    
    with col2:
        st.metric("Variables", len(df.columns))
    
    with col3:
        memory_usage = df.memory_usage(deep=True).sum() / (1024**2)
        st.metric("Memory Usage", f"{memory_usage:.2f} MB")
    
    with col4:
        numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
        st.metric("Numeric Columns", numeric_cols)

# END OF APPLICATION

# Final status message
st.markdown("---")
st.success("✅ ClimateScope - All systems operational")

# Add a small footer note
st.markdown("""
    <div style='text-align: center; padding: 10px; color: #6c757d; font-size: 0.8em;'>
        <p>This application processes weather data in real-time using advanced analytics and machine learning.</p>
        <p>For technical support or feature requests, please contact the development team.</p>
    </div>
""", unsafe_allow_html=True)

# ADDITIONAL UTILITY FUNCTIONS (if needed for future enhancements)

def calculate_weather_score(row):
    """Calculate a composite weather comfort score"""
    score = 50  # Base score
    
    if temp_col in row.index:
        temp = row[temp_col]
        if 18 <= temp <= 25:
            score += 20
        elif 15 <= temp < 18 or 25 < temp <= 28:
            score += 10
        else:
            score -= 10
    
    if humidity_col in row.index:
        hum = row[humidity_col]
        if 40 <= hum <= 60:
            score += 20
        elif 30 <= hum < 40 or 60 < hum <= 70:
            score += 10
        else:
            score -= 10
    
    if wind_col in row.index:
        wind = row[wind_col]
        if wind < 20:
            score += 10
        elif wind > 50:
            score -= 20
    
    return max(0, min(100, score))

def generate_weather_recommendation(temp, humidity, wind):
    """Generate activity recommendations based on weather"""
    recommendations = []
    
    if 18 <= temp <= 25 and humidity < 70:
        recommendations.append("Perfect for outdoor activities")
    
    if wind < 15:
        recommendations.append("Great for cycling or walking")
    
    if temp > 30:
        recommendations.append("Stay hydrated and avoid midday sun")
    
    if temp < 10:
        recommendations.append("Dress warmly for outdoor activities")
    
    if humidity > 80:
        recommendations.append("Humid conditions - indoor activities recommended")
    
    return recommendations if recommendations else ["Monitor weather conditions"]

# SCRIPT METADATA

"""
ClimateScope - Weather Analytics Platform

Features:
- 14 comprehensive analysis tabs
- Real-time filtering and data processing
- Machine learning predictions
- Interactive visualizations
- Export functionality
- Astronomical data analysis
- Extreme event detection
- Geographic mapping
- Statistical analysis
- Correlation analysis
- Time series analysis
- Data quality reporting

Technologies:
- Python 3.8+
- Streamlit
- Pandas
- NumPy
- Plotly
- Scikit-learn
- SciPy

Author: Kunal Harsha Vinod Jadhav\n
Last Updated: 2025
"""

# End of ClimateScope