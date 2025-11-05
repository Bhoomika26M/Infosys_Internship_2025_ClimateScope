Milestone 1 – Data Preparation & Initial Analysis


1. Objective

The  milestone1 focused on preparing the Global Weather Repository dataset for further exploration and visualization.
This included cleaning inconsistent records, filling missing values, converting temperature units, and organizing the data into a usable format for later analysis.


2. Install Required Packages

To ensure smooth data processing, the following Python libraries were used in this milestone:

- pandas – for data cleaning, transformation, and file handling
- numpy – for efficient numerical operations
- scikit-learn – for normalizing numeric data using Min-Max scaling

These can be installed collectively using:

pip install -r requirements.txt

The "requirements.txt" file is included in the project root directory for quick setup.


3. Dataset Information

- Source: Kaggle – Global Weather Repository
- File Path: "data/GlobalWeatherRepository.csv"
- Data Shape: 97,824 rows × 41 columns

The dataset contains global-level weather metrics, including temperature, wind speed, humidity, pressure, and visibility across different regions and timeframes.


4. Data Processing Summary

All preprocessing and transformation were performed through the script:

scripts/explore_data.py

Main operations performed:

- Inspected dataset structure and detected missing or invalid values.
- Replaced missing numeric values with corresponding column averages.
- Removed redundant or inconsistent columns.
- Converted temperature from Kelvin to Celsius.
- Normalized all numeric columns using Min-Max scaling (0–1).
- Aggregated daily data into monthly averages for trend analysis.
- Exported all processed datasets into the "data/" directory.


5. Results

Dataset Summary
Original Dataset:97,824 rows × 41 columns
Cleaned Dataset: Missing values imputed, redundant units removed, temperature converted, and data normalized
Aggregated Dataset: Monthly averages generated per location and country



6. Generated Files

File Description
"GlobalWeatherRepository_cleaned.csv"( Cleaned dataset with consistent numeric and date formats)
"GlobalWeatherRepository_normalized.csv"( Dataset scaled to 0–1 range for uniform analysis)
"GlobalWeatherRepository_monthly.csv"( Aggregated file with monthly mean weather statistics)
"explore_data.py"( Python script containing all preprocessing steps)
"requirements.txt"( File listing required Python dependencies)

---

7. Conclusion

This milestone successfully transformed the raw dataset into a clean and structured format.
Through systematic preprocessing, unit conversion, and normalization, the data is now ready for visualization and analytical modeling in the next phase of the project.