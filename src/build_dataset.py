from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

TARGET_PATH = ROOT / "data" / "raw" / "target_teams.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "champion_runnerup_dataset.csv"


def build_dataset() -> pd.DataFrame:
    targets = pd.read_csv(TARGET_PATH)

    required_cols = ["league", "season", "champion", "runner_up"]
    missing = [c for c in required_cols if c not in targets.columns]
    if missing:
        raise ValueError(f"Missing columns in target_teams.csv: {missing}")

    champions = (
        targets[["league", "season", "champion"]]
        .rename(columns={"champion": "team"})
        .assign(rank=1)
    )

    runner_ups = (
        targets[["league", "season", "runner_up"]]
        .rename(columns={"runner_up": "team"})
        .assign(rank=2)
    )

    df = pd.concat([champions, runner_ups], ignore_index=True)
    df = df[["league", "season", "team", "rank"]].copy()

    # Project variables
    df["wage_bill_eur_m"] = pd.NA
    df["rotation_players_900plus"] = pd.NA
    df["formation_433_rate"] = pd.NA
    df["avg_age"] = pd.NA
    df["source_notes"] = ""

    df = df.sort_values(["league", "season", "rank"]).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = build_dataset()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print("Dataset skeleton created:")
    print(df)
    print(f"\nSaved to: {OUTPUT_PATH}")
