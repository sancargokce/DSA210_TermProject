from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

TARGET_PATH = ROOT / "data" / "raw" / "target_teams.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "champion_profile_dataset.csv"


def build_dataset() -> pd.DataFrame:
    targets = pd.read_csv(TARGET_PATH)

    required_cols = ["league", "league_country", "season", "team"]
    missing = [c for c in required_cols if c not in targets.columns]
    if missing:
        raise ValueError(f"Missing columns in target_teams.csv: {missing}")

    df = targets[["league", "league_country", "season", "team"]].copy()

    df["coach_name"] = pd.NA
    df["coach_nationality"] = pd.NA
    df["domestic_coach"] = pd.NA
    df["dominant_formation"] = pd.NA
    df["back_four_rate"] = pd.NA
    df["avg_age"] = pd.NA
    df["source_notes"] = ""

    df = df[
        [
            "league",
            "league_country",
            "season",
            "team",
            "coach_name",
            "coach_nationality",
            "domestic_coach",
            "dominant_formation",
            "back_four_rate",
            "avg_age",
            "source_notes",
        ]
    ].sort_values(["league", "season", "team"]).reset_index(drop=True)

    return df


if __name__ == "__main__":
    df = build_dataset()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print("Champion profile dataset skeleton created:")
    print(df.head())
    print(f"\nSaved to: {OUTPUT_PATH}")
