"""
ClimateScope - Milestone 1: Data Preparation & Initial Analysis
Dataset: Global Weather Repository
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configure if you want to use Kaggle API

from kaggle.api.kaggle_api_extended import KaggleApi

def download_kaggle_dataset():
    # Setup Kaggle API (requires kaggle.json in ~/.kaggle/)
    api = KaggleApi()
    api.authenticate()
    
    # Download dataset
    api.dataset_download_files(
        'nelgiriyewithana/global-weather-repository',
        path='./data',
        unzip=True
    )
    print("Dataset downloaded successfully!")

# STEP 1: DATA ACQUISITION

def load_dataset(file_path):
    """Load the Global Weather Repository dataset"""
    print("Loading dataset...")
    df = pd.read_csv(file_path)
    print(f"Dataset loaded successfully!")
    print(f"Shape: {df.shape}")
    return df

# STEP 2: DATA UNDERSTANDING & EXPLORATION

def explore_dataset(df):
    """Inspect dataset structure and key variables"""
    print("\n" + "="*80)
    print("DATA EXPLORATION")
    print("="*80)
    
    # Basic information
    print("\n1. Dataset Shape:")
    print(f"   Rows: {df.shape[0]:,}")
    print(f"   Columns: {df.shape[1]}")
    
    # Column names and types
    print("\n2. Column Names and Data Types:")
    print(df.dtypes)
    
    # First few rows
    print("\n3. First 5 Rows:")
    print(df.head())
    
    # Statistical summary
    print("\n4. Statistical Summary:")
    print(df.describe())
    
    # Missing values
    print("\n5. Missing Values:")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    missing_df = pd.DataFrame({
        'Missing_Count': missing,
        'Percentage': missing_pct
    })
    print(missing_df[missing_df['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False))
    
    # Unique values for categorical columns
    print("\n6. Unique Values in Key Columns:")
    for col in df.columns:
        if df[col].dtype == 'object':
            print(f"   {col}: {df[col].nunique()} unique values")
    
    # Data coverage by region
    if 'country' in df.columns:
        print("\n7. Data Coverage by Country (Top 10):")
        print(df['country'].value_counts().head(10))
    
    return missing_df

def visualize_missing_data(df):
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if len(missing) > 0:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(range(len(missing)), missing.values)
        ax.set_xticks(range(len(missing)))
        ax.set_xticklabels(missing.index, rotation=45, ha='right')
        ax.set_xlabel('Columns')
        ax.set_ylabel('Number of Missing Values')
        ax.set_title('Missing Values by Column')
        fig.tight_layout()
        fig.savefig('missing_values_analysis.png', dpi=300, bbox_inches='tight')
        print("\nMissing values visualization saved as 'missing_values_analysis.png'")
        plt.close(fig)
    else:
        print("\nNo missing values detected.")

# STEP 3: DATA CLEANING & PREPROCESSING

def clean_dataset(df):
    """Clean and preprocess the dataset"""
    print("\n" + "="*80)
    print("DATA CLEANING & PREPROCESSING")
    print("="*80)
    
    df_clean = df.copy()
    
    # 1. Handle date/time columns
    print("\n1. Processing date/time columns...")
    date_cols = [col for col in df_clean.columns if 'date' in col.lower() or 'time' in col.lower()]
    for col in date_cols:
        try:
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
            print(f"   Converted {col} to datetime")
        except:
            print(f"   Could not convert {col} to datetime")
    
    # 2. Handle missing values
    print("\n2. Handling missing values...")
    
    # For numerical columns: fill with median or interpolate
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df_clean[col].isnull().sum() > 0:
            missing_count = df_clean[col].isnull().sum()
            missing_pct = (missing_count / len(df_clean)) * 100
            
            if missing_pct < 5:
                # Interpolate for small amounts of missing data
                df_clean[col] = df_clean[col].interpolate(method='linear', limit_direction='both')
                print(f"   {col}: Interpolated {missing_count} values ({missing_pct:.2f}%)")
            elif missing_pct < 30:
                # Fill with median for moderate amounts
                median_val = df_clean[col].median()
                df_clean[col].fillna(median_val, inplace=True)
                print(f"   {col}: Filled {missing_count} values with median ({missing_pct:.2f}%)")
            else:
                print(f"   {col}: High missing rate ({missing_pct:.2f}%) - consider dropping")
    
    # For categorical columns: fill with mode or 'Unknown'
    categorical_cols = df_clean.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df_clean[col].isnull().sum() > 0:
            missing_count = df_clean[col].isnull().sum()
            mode_val = df_clean[col].mode()[0] if len(df_clean[col].mode()) > 0 else 'Unknown'
            df_clean[col].fillna(mode_val, inplace=True)
            print(f"   {col}: Filled {missing_count} values with mode/Unknown")
    
    # 3. Remove duplicates
    print("\n3. Removing duplicates...")
    initial_rows = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    removed = initial_rows - len(df_clean)
    print(f"   Removed {removed} duplicate rows")
    
    # 4. Handle outliers (optional - using IQR method)
    print("\n4. Detecting outliers...")
    for col in numeric_cols:
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR
        
        outliers = ((df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)).sum()
        if outliers > 0:
            print(f"   {col}: {outliers} potential outliers detected (not removed)")
    
    # 5. Standardize column names
    print("\n5. Standardizing column names...")
    df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_')
    print("   Column names standardized to lowercase with underscores")
    
    print(f"\nCleaned dataset shape: {df_clean.shape}")
    return df_clean

def create_aggregated_data(df):
    """Aggregate data for efficiency (e.g., daily to monthly)"""
    print("\n" + "="*80)
    print("DATA AGGREGATION")
    print("="*80)
    
    # Check if date column exists
    date_col = None
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower():
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_col = col
                break
    
    if date_col is None:
        print("No datetime column found. Skipping aggregation.")
        return None
    
    df_agg = df.copy()
    df_agg['year'] = df_agg[date_col].dt.year
    df_agg['month'] = df_agg[date_col].dt.month
    df_agg['day'] = df_agg[date_col].dt.day
    
    # Create monthly aggregations
    numeric_cols = df_agg.select_dtypes(include=[np.number]).columns
    
    # Group by location and month
    if 'country' in df_agg.columns and 'location_name' in df_agg.columns:
        monthly_agg = df_agg.groupby(['country', 'location_name', 'year', 'month'])[numeric_cols].agg(['mean', 'min', 'max', 'std'])
        monthly_agg.columns = ['_'.join(col).strip() for col in monthly_agg.columns]
        monthly_agg = monthly_agg.reset_index()
        print(f"\nMonthly aggregated data created: {monthly_agg.shape}")
        return monthly_agg
    
    return None

# STEP 4: GENERATE SUMMARY REPORT

def generate_summary_report(df_original, df_clean, missing_df):
    """Generate a summary document of data preparation"""
    print("\n" + "="*80)
    print("GENERATING SUMMARY REPORT")
    print("="*80)
    
    report = []
    report.append("="*80)
    report.append("CLIMATESCOPE - MILESTONE 1: DATA PREPARATION SUMMARY")
    report.append("="*80)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    report.append("\n\n1. DATASET OVERVIEW")
    report.append("-" * 40)
    report.append(f"Original Shape: {df_original.shape[0]:,} rows × {df_original.shape[1]} columns")
    report.append(f"Cleaned Shape: {df_clean.shape[0]:,} rows × {df_clean.shape[1]} columns")
    report.append(f"Rows Removed: {df_original.shape[0] - df_clean.shape[0]:,}")
    
    report.append("\n\n2. DATA SCHEMA")
    report.append("-" * 40)
    for col, dtype in df_clean.dtypes.items():
        report.append(f"{col}: {dtype}")
    
    report.append("\n\n3. DATA QUALITY ISSUES")
    report.append("-" * 40)
    if missing_df['Missing_Count'].sum() > 0:
        report.append("Missing Values (Original Dataset):")
        for idx, row in missing_df[missing_df['Missing_Count'] > 0].iterrows():
            report.append(f"  - {idx}: {row['Missing_Count']} ({row['Percentage']:.2f}%)")
    else:
        report.append("No missing values detected.")
    
    report.append("\n\n4. KEY VARIABLES")
    report.append("-" * 40)
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    report.append("Numerical Variables:")
    for col in numeric_cols:
        report.append(f"  - {col}")
    
    categorical_cols = df_clean.select_dtypes(include=['object']).columns
    report.append("\nCategorical Variables:")
    for col in categorical_cols:
        report.append(f"  - {col} ({df_clean[col].nunique()} unique values)")
    
    report.append("\n\n5. PREPROCESSING STEPS COMPLETED")
    report.append("-" * 40)
    report.append("✓ Missing values handled (interpolation/median/mode filling)")
    report.append("✓ Duplicate rows removed")
    report.append("✓ Column names standardized")
    report.append("✓ Data types converted appropriately")
    report.append("✓ Outliers detected and documented")
    
    report.append("\n\n6. SUCCESS CRITERIA")
    report.append("-" * 40)
    report.append("✓ Dataset successfully downloaded and loaded")
    report.append("✓ Data cleaned and transformed into usable format")
    report.append("✓ Ready for analysis in Milestone 2")
    
    report.append("\n" + "="*80)
    
    # Write to file with UTF-8 encoding to avoid UnicodeEncodeError
    with open('milestone1_summary_report.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print("\nSummary report saved as 'milestone1_summary_report.txt'")
    print('\n'.join(report))

# MAIN EXECUTION

def main():
    """Main execution function for Milestone 1"""
    
    # Step 0: Download dataset from Kaggle
    print("="*80)
    print("DOWNLOADING DATASET FROM KAGGLE API")
    print("="*80)
    
    # Create data directory if it doesn't exist
    if not os.path.exists('./data'):
        os.makedirs('./data')
        print("Created './data' directory\n")
    
    # Check if dataset already exists
    file_path = './data/GlobalWeatherRepository.csv'
    if os.path.exists(file_path):
        print(f"Dataset already exists at: {file_path}")
        user_input = input("Do you want to re-download? (y/n): ").strip().lower()
        if user_input == 'y':
            try:
                download_kaggle_dataset()
            except Exception as e:
                print(f"\nDownload failed: {e}")
                print("Using existing dataset...")
        else:
            print("Using existing dataset...")
    else:
        try:
            download_kaggle_dataset()
        except Exception as e:
            print(f"\nError downloading from Kaggle: {e}")
            print("\nPlease ensure:")
            print("1. Kaggle API credentials (kaggle.json) in ~/.kaggle/ or equivalent")
            print("2. Dataset terms accepted on Kaggle")
            print("3. Kaggle package installed (pip install kaggle)")
            print("\nDataset URL: https://www.kaggle.com/datasets/nelgiriyewithana/global-weather-repository/data")
            return
    
    # Step 1: Load the dataset
    print("\n" + "="*80)
    print("LOADING DATASET")
    print("="*80)
    
    try:
        df_original = load_dataset(file_path)
    except FileNotFoundError:
        print(f"\nError: File '{file_path}' not found!")
        print("Please make sure the dataset was downloaded successfully.")
        return
    
    # Step 2: Explore the dataset
    missing_df = explore_dataset(df_original)
    visualize_missing_data(df_original)
    
    # Step 3: Clean and preprocess
    df_clean = clean_dataset(df_original)
    
    # Step 4: Create aggregated data
    df_monthly = create_aggregated_data(df_clean)
    
    # Step 5: Save cleaned data
    print("\nSaving cleaned dataset...")
    df_clean.to_csv('global_weather_cleaned.csv', index=False)
    print("Cleaned dataset saved as 'global_weather_cleaned.csv'")
    
    if df_monthly is not None:
        df_monthly.to_csv('global_weather_monthly.csv', index=False)
        print("Monthly aggregated data saved as 'global_weather_monthly.csv'")
    
    # Step 6: Generate summary report
    generate_summary_report(df_original, df_clean, missing_df)
    
    print("\n" + "="*80)
    print("MILESTONE 1 COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\nDeliverables:")
    print("1. global_weather_cleaned.csv - Cleaned dataset")
    print("2. global_weather_monthly.csv - Monthly aggregated data")
    print("3. milestone1_summary_report.txt - Summary document")
    print("4. missing_values_analysis.png - Missing values visualization")

if __name__ == "__main__":
    main()
