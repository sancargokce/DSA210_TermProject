import pandas as pd
from scipy.stats import ttest_rel, wilcoxon

DATA_PATH = "data/processed/champion_runnerup_dataset.csv"

df = pd.read_csv(DATA_PATH)

print("Dataset preview:")
print(df.head())
print("\nColumns:")
print(df.columns.tolist())
print("\nShape:", df.shape)

# Basic checks
required_cols = [
    "league", "season", "team", "rank",
    "wage_bill_eur_m",
    "rotation_players_900plus",
    "formation_433_rate",
    "avg_age"
]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns: {missing}")

# Keep only champion and runner-up
df = df[df["rank"].isin([1, 2])].copy()

# Build paired tables
def paired_test(df, value_col):
    pivot = df.pivot_table(
        index=["league", "season"],
        columns="rank",
        values=value_col,
        aggfunc="first"
    ).dropna()

    if 1 not in pivot.columns or 2 not in pivot.columns:
        print(f"Skipping {value_col}: champion/runner-up pairs not complete.")
        return

    champ = pivot[1]
    runner = pivot[2]

    print(f"\n=== {value_col} ===")
    print("Champion mean:", champ.mean())
    print("Runner-up mean:", runner.mean())
    print("Mean difference (champ - runner-up):", (champ - runner).mean())

    if len(pivot) >= 2:
        t_stat, t_p = ttest_rel(champ, runner)
        print("Paired t-test:", t_stat, t_p)

        try:
            w_stat, w_p = wilcoxon(champ, runner)
            print("Wilcoxon:", w_stat, w_p)
        except:
            print("Wilcoxon could not be computed.")
    else:
        print("Not enough paired observations yet for statistical testing.")

for col in [
    "wage_bill_eur_m",
    "rotation_players_900plus",
    "formation_433_rate",
    "avg_age"
]:
    paired_test(df, col)
