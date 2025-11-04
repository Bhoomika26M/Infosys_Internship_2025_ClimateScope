import os
import pandas as pd

# Input folder and output summary file
RAW_DIR = "data/raw"
OUT = "summary_report.md"

def main():
    # -----------------------------
    # 1. Load dataset
    # -----------------------------
    file = os.path.join(RAW_DIR, "GlobalWeatherRepository.csv")
    df = pd.read_csv(file, low_memory=False)

    # -----------------------------
    # 2. Basic dataset info
    # -----------------------------
    n_rows, n_cols = df.shape
    print("Dataset Shape:", (n_rows, n_cols))

    dtypes = df.dtypes
    print("\nColumn Data Types:\n", dtypes)

    null_counts = df.isnull().sum()
    print("\nMissing Values (counts):\n", null_counts)

    null_pct = (null_counts / n_rows * 100).round(2)

    # -----------------------------
    # 3. Date range (if date column exists)
    # -----------------------------
    date_cols = [c for c in df.columns if "date" in c.lower()]
    date_range = None
    if date_cols:
        df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors="coerce")
        date_range = (df[date_cols[0]].min(), df[date_cols[0]].max())

    # -----------------------------
    # 4. Write summary report
    # -----------------------------
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# Dataset Summary Report\n\n")
        f.write(f"- **Shape:** {n_rows} rows × {n_cols} columns\n\n")

        f.write("## Column Data Types\n")
        f.write(dtypes.to_string())
        f.write("\n\n")

        f.write("## Missing Values (counts)\n")
        f.write(null_counts.to_string())
        f.write("\n\n")

        f.write("## Missing Values (%)\n")
        f.write(null_pct.to_string())
        f.write("\n\n")

        if date_range:
            f.write("## Date Range\n")
            f.write(f"- {date_range[0]} → {date_range[1]}\n")

    print(f"Summary written to {OUT}")

if __name__ == "__main__":
    main()
