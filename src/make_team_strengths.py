from pathlib import Path
import pandas as pd

# Input and output paths
IN_PATH = Path("data/interim/fifa_rankings_pre_wc_2014_2014-06-05.csv")
OUT_DIR = Path("data/processed")

def main() -> None:
    """
    Converts FIFA ranking points into normalized team strength values.

    The function reads the pre-World-Cup ranking snapshot, checks that the required columns are present, and transforms the ranking points into normalized strength in the 
    range [0, 1]. These values are used as input for the Monte Carlo simulation of the FIFA World Cup 2014.
    """
    #1) Check if input file exists
    if not IN_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {IN_PATH}")
        
    #2) Create output directory if necessary
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    #3) Load snapshot CSV file
    df = pd.read_csv(IN_PATH)

    # Check required columns
    needed = {"rank", "country_full", "total_points"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # 5) Normalize ranking points to the interval[0, 1]
    # Strength = (points - min_points) / (max_points - min_points)
    pts = df["total_points"].astype(float)
    min_pts = pts.min()
    max_pts = pts.max()

    if max_pts == min_pts:
        raise ValueError("All teams have identical points. Normalization is not possible")

    df_out = pd.DataFrame({
        "team": df["country_full"],
        "rank": df["rank"].astype(int),
        "points": pts,
        "strength": (pts - min_pts) / (max_pts - min_pts)
    })

    # Optional lower bound to avoid zero strength values
    df_out["strength"] = df_out["strength"].clip(lower=0.05)
    # Save processed data
    out_path = OUT_DIR / "teams_strengths_pre_wc_2014.csv"
    df_out.to_csv(out_path, index=False)
    # Console output
    print("Team- strengths created successfully!")
    print(f"Saved to: {out_path}")
    print("Top 5 Teams by strength:")
    print(df_out.sort_values("strength", ascending=False).head(5)[["team", "rank", "points", "strength"]])

if __name__ == "__main__":
    main()
