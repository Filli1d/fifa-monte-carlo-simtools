from pathlib import Path
import pandas as pd

IN_PATH = Path("data/interim/fifa_rankings_pre_wc_2014_2014-06-05.csv")
OUT_DIR = Path("data/processed")

def main() -> None:
    if not IN_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {IN_PATH}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(IN_PATH)

    # Wir brauchen mindestens diese Spalten:
    needed = {"rank", "country_full", "total_points"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"Fehlende Spalten: {missing}")

    # Stärke aus Punkten: Normalisieren auf 0..1
    # Stärke = (points - min) / (max - min)
    pts = df["total_points"].astype(float)
    min_pts = pts.min()
    max_pts = pts.max()

    if max_pts == min_pts:
        raise ValueError("Alle Teams haben gleiche Punkte – Normalisierung nicht möglich.")

    df_out = pd.DataFrame({
        "team": df["country_full"],
        "rank": df["rank"].astype(int),
        "points": pts,
        "strength": (pts - min_pts) / (max_pts - min_pts)
    })

    # Optional: kleine Untergrenze, damit niemand Stärke 0 hat
    # (hilft manchmal beim Simulieren)
    df_out["strength"] = df_out["strength"].clip(lower=0.05)

    out_path = OUT_DIR / "teams_strengths_pre_wc_2014.csv"
    df_out.to_csv(out_path, index=False)

    print("✅ Team-Stärken erstellt!")
    print(f"Gespeichert nach: {out_path}")
    print("Top 5 Teams (nach Stärke):")
    print(df_out.sort_values("strength", ascending=False).head(5)[["team", "rank", "points", "strength"]])

if __name__ == "__main__":
    main()
