  Milestone 1 – Data Preparation & Initial Analysis

## Dataset Overview
- Source: [Global Weather Repository – Kaggle](https://www.kaggle.com/datasets/nelgiriyewithana/global-weather-repository/data)  
- Rows after cleaning :98214
- Columns: 41
-File Name: `cleaned_weather.csv`

---

Data Cleaning Process

1. Missing Values Handling
   - Removed rows with missing values in critical weather fields (temperature, humidity, precipitation, wind, etc.).
   - Filled remaining missing numeric values with column means.

2. Unit Conversion
   - Converted temperature from Kelvin to Celsius f needed.

3. Normalization
   - Added a new column `temperature_norm` (0–1 scaled).

4. Aggregation
   - Converted daily data to monthly averages grouped by `year_month` and `country`.

5. Output
   - Saved the cleaned dataset to `cleaned_weather.csv`.



 Data Quality Summary

                                         
 Missing values          | All critical fields = 0     
 Invalid records         | Removed during cleaning     
 Data types              | Verified and consistent     
                   

 Deliverables

Cleaned Dataset: `processed/cleaned_weather.csv`  
Summary Document: `Milestone1_Summary.md`  
Python Script:`data_preparation.py`



 Conclusion

The dataset has been successfully:
- Downloaded from Kaggle  
- Cleaned and preprocessed  
- Transformed into a usable, analysis-ready format

This completes Milestone 1 requirements as per the project workflow. 
