import os
import pandas as pd
from scipy import stats
print("Script is running")


IN_MONTHLY = "data/processed/monthly_agg.parquet"
OUT_EXTREMES = "analysis/extremes.csv"

def main():
    print("Starting extremes detection...")

    if not os.path.exists(IN_MONTHLY):
        print("ERROR: Input file not found. Run aggregation first.")
        return
    m = pd.read_parquet(IN_MONTHLY)
    print(f"Loaded monthly data with {len(m)} rows")
    print("Sample data:")
    print(m[['country', 'temperature_celsius', 'precip_mm']].head())

    m['temp_z'] = m.groupby('country')['temperature_celsius'].transform(lambda x: stats.zscore(x, nan_policy='omit'))
    m['precip_pctile'] = m.groupby('country')['precip_mm'].transform(lambda x: x.rank(pct=True))

    # Use lower thresholds for testing
    m['extreme_temp'] = m['temp_z'].abs() > 1.5
    m['extreme_precip'] = m['precip_pctile'] >= 0.95

    print(f"Extreme temperature count: {m['extreme_temp'].sum()}")
    print(f"Extreme precipitation count: {m['extreme_precip'].sum()}")

    extremes = m[m['extreme_temp'] | m['extreme_precip']].copy()
    print(f"Total extremes found: {len(extremes)}")

    if len(extremes) == 0:
        print("No extreme events detected. Adjust thresholds or check data.")
        return

    def reason(row):
        r = []
        if row['extreme_temp']:
            r.append(f"temp_z={row['temp_z']:.2f}")
        if row['extreme_precip']:
            r.append(f"precip_pctile={row['precip_pctile']:.2f}")
        return "; ".join(r)
    extremes['reason'] = extremes.apply(reason, axis=1)

    os.makedirs("analysis", exist_ok=True)
    extremes.to_csv(OUT_EXTREMES, index=False)
    print(f"Saved extremes to {OUT_EXTREMES}, rows: {len(extremes)}")

if __name__ == "__main__":
    main()
