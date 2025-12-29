from pathlib import Path
import pandas as pd

RAW_PATH = Path("data/raw/fifa_rankings_all_years.csv")
OUT_DIR = Path("data/interim")
WC_START = pd.Timestamp("2014-06-12")  # WM-Start Brasilien 2014

def main() -> None:
    # 1) Existiert die Datei?
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Raw file not found: {RAW_PATH}")

    # 2) Zielordner sicher anlegen
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 3) CSV laden
    df = pd.read_csv(RAW_PATH)

    # 4) Prüfen: rank_date muss existieren
    if "rank_date" not in df.columns:
        raise ValueError("Spalte 'rank_date' nicht gefunden. Bitte prüfe die CSV-Spaltennamen.")

    # 5) Datum parsen
    df["rank_date"] = pd.to_datetime(df["rank_date"], errors="coerce")

    # 6) Nur Zeilen vor WM-Start behalten
    before_wc = df[df["rank_date"] < WC_START].copy()
    if before_wc.empty:
        raise ValueError("Keine Daten vor dem WM-Start gefunden. Prüfe 'rank_date' Werte.")

    # 7) Das letzte Ranking-Datum vor WM finden
    snapshot_date = before_wc["rank_date"].max()

    # 8) Nur dieses Datum nehmen (ein Snapshot)
    snapshot = before_wc[before_wc["rank_date"] == snapshot_date].copy()
    snapshot = snapshot.sort_values(["rank"], ascending=True)

    # 9) Speichern
    out_path = OUT_DIR / f"fifa_rankings_pre_wc_2014_{snapshot_date.date()}.csv"
    snapshot.to_csv(out_path, index=False)

    # 10) Ausgabe für dich
    print("✅ Fertig!")
    print(f"WM-Start: {WC_START.date()}")
    print(f"Gewähltes Ranking-Datum: {snapshot_date.date()}")
    print(f"Zeilen (Teams): {len(snapshot)}")
    print(f"Gespeichert nach: {out_path}")

if __name__ == "__main__":
    main()
