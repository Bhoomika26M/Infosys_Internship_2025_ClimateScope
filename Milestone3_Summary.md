# Milestone 3 — Advanced Dashboard Development & UX Enhancements

**Project:** ClimateScope — Visualizing Global Weather Trends and Extreme Events  
**Author:** Thesika S N

## Objective
Evolve the ClimateScope dashboard into a polished, multi-page analytical product with richer visualization, air quality analysis, and improved UI/UX.

## Key Tasks Completed
- Organized the dashboard into multi-tab navigation:
  - Overview, Statistical Analysis, Trends & Seasonality, Regional Map, Correlation Insights, Air Quality Index, Extreme Events, Summary.
- Added Air Quality Index (AQI) page with:
  - AQI classification table (Good → Hazardous).
  - Color-coded pie chart of average AQI by country (colors follow official AQI ranges).
- Fixed layout and visual issues (tab gradient, responsive widths).
- Enhanced Extreme Events page: separate “Hottest Days” and “Coldest Days” tables with bold headers and a wind speed distribution chart.
- Implemented a Dual-Axis Time-Series (correlation insights) to compare two variables over time.
- Ensured datetime consistency and Plotly/Streamlit compatibility (ISO-3 for choropleth, `width="stretch"` usage).

## Insights & Findings
- Regional AQI disparities are pronounced and correlate with certain temperature/pressure patterns.
- Dual-axis comparisons help reveal variable dependencies (e.g., humidity vs temperature).
- Several extreme temperature events were identified for targeted analysis.

## Deliverables
- Finalized Streamlit Dashboard: `app.py` (Milestone 3 final)
- Milestone reports and processed outputs
- `Milestone2_Summary.md` and `Milestone3_Summary.md`

---
