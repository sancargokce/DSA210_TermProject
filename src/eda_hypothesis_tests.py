from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "data" / "processed" / "champion_profile_dataset.csv"
TABLE_DIR = ROOT / "outputs" / "tables"
FIG_DIR = ROOT / "outputs" / "figures"


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    required_cols = [
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

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in champion_profile_dataset.csv: {missing}")

    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["domestic_coach"] = pd.to_numeric(df["domestic_coach"], errors="coerce")
    df["back_four_rate"] = pd.to_numeric(df["back_four_rate"], errors="coerce")
    df["avg_age"] = pd.to_numeric(df["avg_age"], errors="coerce")

    return df


def save_completion_report(df: pd.DataFrame) -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    completion = pd.DataFrame({
        "column": df.columns,
        "non_null_count": [df[c].notna().sum() for c in df.columns],
        "null_count": [df[c].isna().sum() for c in df.columns],
        "completion_rate": [df[c].notna().mean() for c in df.columns],
    })

    completion.to_csv(TABLE_DIR / "data_completion_report.csv", index=False)


def save_profile_summary(df: pd.DataFrame) -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    summary_rows = []

    summary_rows.append({
        "metric": "number_of_observations",
        "value": len(df)
    })

    summary_rows.append({
        "metric": "domestic_coach_known_count",
        "value": df["domestic_coach"].notna().sum()
    })

    if df["domestic_coach"].notna().any():
        summary_rows.append({
            "metric": "domestic_coach_rate",
            "value": df["domestic_coach"].dropna().mean()
        })

    summary_rows.append({
        "metric": "avg_age_known_count",
        "value": df["avg_age"].notna().sum()
    })

    if df["avg_age"].notna().any():
        summary_rows.extend([
            {"metric": "avg_age_mean", "value": df["avg_age"].mean()},
            {"metric": "avg_age_median", "value": df["avg_age"].median()},
            {"metric": "avg_age_min", "value": df["avg_age"].min()},
            {"metric": "avg_age_max", "value": df["avg_age"].max()},
        ])

    summary_rows.append({
        "metric": "back_four_rate_known_count",
        "value": df["back_four_rate"].notna().sum()
    })

    if df["back_four_rate"].notna().any():
        summary_rows.extend([
            {"metric": "back_four_rate_mean", "value": df["back_four_rate"].mean()},
            {"metric": "back_four_rate_median", "value": df["back_four_rate"].median()},
            {"metric": "back_four_rate_min", "value": df["back_four_rate"].min()},
            {"metric": "back_four_rate_max", "value": df["back_four_rate"].max()},
        ])

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(TABLE_DIR / "profile_summary.csv", index=False)


def save_categorical_tables(df: pd.DataFrame) -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    coach_nat = (
        df["coach_nationality"]
        .dropna()
        .value_counts()
        .rename_axis("coach_nationality")
        .reset_index(name="count")
    )
    coach_nat.to_csv(TABLE_DIR / "coach_nationality_counts.csv", index=False)

    formations = (
        df["dominant_formation"]
        .dropna()
        .value_counts()
        .rename_axis("dominant_formation")
        .reset_index(name="count")
    )
    formations.to_csv(TABLE_DIR / "dominant_formation_counts.csv", index=False)

    domestic = (
        df["domestic_coach"]
        .dropna()
        .map({1: "Domestic", 0: "Foreign"})
        .value_counts()
        .rename_axis("domestic_coach_label")
        .reset_index(name="count")
    )
    domestic.to_csv(TABLE_DIR / "domestic_coach_counts.csv", index=False)


def save_figures(df: pd.DataFrame) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    domestic = (
        df["domestic_coach"]
        .dropna()
        .map({1: "Domestic", 0: "Foreign"})
        .value_counts()
    )

    if not domestic.empty:
        plt.figure(figsize=(6, 4))
        domestic.plot(kind="bar")
        plt.title("Domestic vs Foreign Coaches")
        plt.ylabel("Count")
        plt.xlabel("")
        plt.tight_layout()
        plt.savefig(FIG_DIR / "domestic_vs_foreign_coaches.png")
        plt.close()

    formations = df["dominant_formation"].dropna().value_counts().head(10)
    if not formations.empty:
        plt.figure(figsize=(8, 4))
        formations.plot(kind="bar")
        plt.title("Most Common Dominant Formations")
        plt.ylabel("Count")
        plt.xlabel("")
        plt.tight_layout()
        plt.savefig(FIG_DIR / "dominant_formations.png")
        plt.close()

    avg_age = df["avg_age"].dropna()
    if not avg_age.empty:
        plt.figure(figsize=(6, 4))
        plt.hist(avg_age, bins=8)
        plt.title("Average Age Distribution")
        plt.xlabel("Average Age")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(FIG_DIR / "avg_age_distribution.png")
        plt.close()

    back_four = df["back_four_rate"].dropna()
    if not back_four.empty:
        plt.figure(figsize=(6, 4))
        plt.hist(back_four, bins=8)
        plt.title("Back-Four Rate Distribution")
        plt.xlabel("Back-Four Rate")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(FIG_DIR / "back_four_rate_distribution.png")
        plt.close()


def main() -> None:
    df = load_dataset()
    df = clean_dataset(df)

    save_completion_report(df)
    save_profile_summary(df)
    save_categorical_tables(df)
    save_figures(df)

    print("Champion profile analysis files created successfully.")
    print(f"Rows in dataset: {len(df)}")
    print(f"Output tables folder: {TABLE_DIR}")
    print(f"Output figures folder: {FIG_DIR}")


if __name__ == "__main__":
    main()
