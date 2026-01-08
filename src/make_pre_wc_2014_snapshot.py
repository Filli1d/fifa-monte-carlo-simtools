from pathlib import Path
import pandas as pd

RAW_PATH = Path("data/raw/fifa_rankings_all_years.csv")
OUT_DIR = Path("data/interim")
WC_START = pd.Timestamp("2014-06-12")  # WM-Start Brasilien 2014

def main() -> None:
    """
    Creates a snapshot of the FIFA World Rankings before the 2014 World Cup.

    The function loads the raw FIFA ranking dataset, checks for valid dates, and selects the most recent ranking published before the World Cup start.
    This snapshot is saved as a CSV file and serves as input for later steps such as team strength calculation and Monte Carlo simulation.
    """
    # 1) Check if raw data file exists
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Raw file not found: {RAW_PATH}")

    # 2) Create output directory if necessary
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 3) Load CSV file 
    df = pd.read_csv(RAW_PATH)

    # 4) Check if rank_date column exists
    if "rank_date" not in df.columns:
        raise ValueError("Column 'rank_date' not found. Please check the CSV file.")

    # 5) Parse dates
    df["rank_date"] = pd.to_datetime(df["rank_date"], errors="coerce")

    # 6) Keep only rankings before World Cup start
    before_wc = df[df["rank_date"] < WC_START].copy()
    if before_wc.empty:
        raise ValueError("No ranking data found before World Cup start date")

    # 7) Find the latest ranking date before the World Cup
    snapshot_date = before_wc["rank_date"].max()

    # 8) Select snapshot for this date
    snapshot = before_wc[before_wc["rank_date"] == snapshot_date].copy()
    snapshot = snapshot.sort_values(["rank"], ascending=True)

    # 9) Save snapshot
    out_path = OUT_DIR / f"fifa_rankings_pre_wc_2014_{snapshot_date.date()}.csv"
    snapshot.to_csv(out_path, index=False)

    # 10) Console output
    print("Done!")
    print(f"World Cup start date: {WC_START.date()}")
    print(f"Selected ranking date: {snapshot_date.date()}")
    print(f"Number of teams: {len(snapshot)}")
    print(f"Saved to: {out_path}")

if __name__ == "__main__":
    main()
