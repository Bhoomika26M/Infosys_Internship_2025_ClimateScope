# 🌦 ClimateScope Project – Milestone 2

## 🧭 Overview
**ClimateScope** is a weather data analysis and visualization project designed to study global climate trends, compare regional weather conditions, detect extreme weather events, and build an interactive dashboard for visual insights.

---

## 📁 Project Structure

| File | Purpose |
|------|----------|
| `mile1.ipynb` | **Data Cleaning & Preprocessing** – Loads raw GlobalWeatherRepository.csv, handles missing values, removes duplicates, scales numeric data, and exports a cleaned dataset. |
| `statistical_analysis.ipynb` | **Exploratory Data Analysis (EDA)** – Generates summary statistics and visualizes data distributions using Matplotlib and Seaborn. |
| `compare_weather_conditions.ipynb` | **Regional Comparison Analysis** – Compares climate metrics (temperature, humidity, rainfall) across regions/cities using visualizations. |
| `extreme_weather_analysis.ipynb` | **Extreme Event Detection** – Identifies extreme temperature and precipitation events based on thresholds. |
| `weather_dashboard.py` | **Streamlit Dashboard** – Interactive app allowing users to explore climate trends and regional comparisons dynamically. |
| `cleaned_dataset.csv` | Cleaned dataset used for analysis and dashboard. |
| `README.md` | Project documentation file. |

---

## 🧠 Key Features

- 📊 Automated data cleaning and transformation pipeline  
- 📈 Detailed statistical and visual analysis  
- 🌎 Comparison of weather metrics across multiple regions  
- ⚠️ Detection of extreme weather patterns  
- 💻 Streamlit-based dashboard for interactive exploration  

---

## 🧰 Technologies Used

- **Python Libraries:** pandas, numpy, matplotlib, seaborn, plotly, streamlit, sklearn  
- **Tools:** Jupyter Notebook, VS Code, Git, Streamlit  
- **Dataset:** GlobalWeatherRepository → cleaned_dataset.csv  

---

## 🚀 How to Run

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/ClimateScope-project-milestone2.git
cd ClimateScope-project-milestone2
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Run Jupyter Notebooks
Execute the following in order:
1. `mile1.ipynb` → Data cleaning  
2. `statistical_analysis.ipynb` → Descriptive analysis  
3. `compare_weather_conditions.ipynb` → Regional comparison  
4. `extreme_weather_analysis.ipynb` → Extreme events  

### 4️⃣ Launch the Dashboard
```bash
streamlit run weather_dashboard.py
```

---

## 📊 Example Outputs

- Temperature and humidity distributions  
- Comparative plots for regions  
- Detection of anomalies (heatwaves, rainfall spikes)  
- Interactive charts and dashboards  

---

## 🧑‍💻 Contributors
- **Jahnavi K** – Data Cleaning, Analysis, and Dashboard Development  

---

## 📅 Milestones

| Milestone | Description |
|------------|--------------|
| **1** | Data Preprocessing & Cleaning |
| **2** | Statistical Analysis, Comparison, and Dashboard Development |

---

## ⭐ Future Enhancements
- Integration of real-time weather APIs  
- Advanced anomaly detection using ML models  
- Automated report generation in Streamlit  
