# ClimateScope Dashboard --- Full Bug Report

#  1. Overview

This document provides a complete, in-depth bug report for the two
latest uploaded files:

-   **Analyse.py** --- Backend analytics module\
-   **Streamlit-app.py** --- Interactive dashboard UI module

------------------------------------------------------------------------

# 2. Critical Functional Bugs

## 2.1 Missing or Undefined Functions

**Files Affected:** `Analyse.py`, `Streamlit-app.py`

### **Imported in `Streamlit-app.py` but NOT defined in `Analyse.py`:**

-   `generate_insights`\
-   `analyze_correlation_insights`

### **Impact**

Dashboard breaks immediately on **Executive Summary** or **Insights**
sections.\
Errors thrown:

    ImportError: cannot import name 'generate_insights'

or

    NameError: generate_insights is not defined

###  **Fix**

Implement the missing functions in `Analyse.py` **or** remove their
usage/import.



## 2.2 Truncated Function --- `detect_anomalies`

**File:** `Analyse.py`

### **Issue**

Function ends abruptly:

``` python
'anomaly_percentage': float(len(anomalies) / len(df_clean)
```

Missing: - closing parenthesis\
- multiplication by 100\
- closing braces\
- return statement

### **Impact**

-   Code crashes with:\
    `SyntaxError: unexpected EOF`\
-   **Advanced Analytics → Anomaly Detection** fails entirely.

### **Fix**

Correct final block:

``` python
'insights': {
    'total_anomalies': len(anomalies),
    'anomaly_percentage': float(len(anomalies) / len(df_clean) * 100)
}
return anomalies, insights
```


## 2.3 Plotly / Matplotlib Mismatch

**File:** `Streamlit-app.py`

### Problematic block:

``` python
if fig:
    fig.update_layout(height=600)
    st.plotly_chart(fig, width='stretch')
else:
    fig.set_size_inches(10, 6)
    st.pyplot(fig, width='stretch')
```

### **Issues**

-   Plotly figures **do NOT support** `.set_size_inches()` (Matplotlib
    only).\
-   If `fig is None`, `.set_size_inches()` crashes.

### **Fix**

``` python
if fig is not None:
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Comparison chart unavailable for selected data.")
```


## 2.4 Filter Logic Can Produce Empty Date Range

If user selects only one date:

``` python
if selected_dates and len(selected_dates) == 2:
```

If `len != 2`, filtering breaks → inconsistent or empty results.

### **Fix**

Ensure exactly two dates are selected before filtering.

------------------------------------------------------------------------

# 3. Backend (`Analyse.py`) --- Detailed Issues

## 3.1 Possible KeyErrors in `detect_extreme_events`

Columns referenced without checks:

-   `visibility_km`\
-   `precip_mm`\
-   `wind_degree`

### Fix:

Add guards:

``` python
if 'visibility_km' in df.columns:
```



## 3.2 Repetition in 3D Plot Generators

`generate_3d_chart` and `generate_3d_surface` contain nearly identical
logic.

### Recommend:

Create helper:

``` python
def _create_3d_base(df, x, y, z):
    ...
```


## 3.3 Missing Docstrings & Type Checks

Large complex functions lack documentation → hard to maintain.

------------------------------------------------------------------------

# 4. Frontend (`Streamlit-app.py`) --- Detailed Issues

## 4.1 CSS Applies Globally

Global CSS overrides may break: - Streamlit widgets\
- Tables\
- Responsiveness

### Suggest:

Scope CSS to specific classes.


## 4.2 Heavy Use of Inline Plotly Layouts

Hardcoded colors like `#FF6B6B` break dark-mode accessibility.



## 4.3 Missing Guard Conditions

Example:

``` python
dff["feels_like_celsius"].mean()
```

If column missing → **crash**.


## 4.4 KPI Sections Can Throw Errors

When filters result in empty dataframes → `.mean()` produces NaN or
warnings.


## 4.5 Duplicate Filter Logic

Filters applied twice: - In sidebar\
- In main layout

→ causes inconsistent data and performance issues.

------------------------------------------------------------------------
