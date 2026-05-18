import pandas as pd
import numpy as np
from scipy import stats
uploaded = files.upload()  # champion_profile_dataset_final.csv yükle
filename = "champion_profile_dataset_final.csv"

df = pd.read_csv(filename)

# -----------------------------
# H1: Domestic coach hypothesis
# H0: p <= 0.5
# H1: p > 0.5
# -----------------------------
n = len(df)
k = int(df["domestic_coach"].sum())
prop_domestic = k / n

h1_binom = stats.binomtest(k, n, p=0.5, alternative="greater")

# -----------------------------
# H2: Back-four hypothesis
# H0: mean back_four_rate <= 0.5
# H1: mean back_four_rate > 0.5
# -----------------------------
x = df["back_four_rate"].dropna().astype(float)

mean_back4 = x.mean()
sd_back4 = x.std(ddof=1)
n_back4 = len(x)
se_back4 = sd_back4 / np.sqrt(n_back4)

t_back4 = (mean_back4 - 0.5) / se_back4
p_back4_t = stats.t.sf(t_back4, df=n_back4 - 1)

wilcoxon_back4 = stats.wilcoxon(x - 0.5, alternative="greater", zero_method="wilcox")

df["dominant_back_four"] = df["dominant_formation"].astype(str).str.startswith("4").astype(int)
k_dom_form = int(df["dominant_back_four"].sum())
prop_dom_form = k_dom_form / n
h2_binom_domform = stats.binomtest(k_dom_form, n, p=0.5, alternative="greater")

# -----------------------------
# H3: Age profile summary
# Descriptive inference
# -----------------------------
age = df["avg_age"].dropna().astype(float)

mean_age = age.mean()
sd_age = age.std(ddof=1)
median_age = age.median()
min_age = age.min()
max_age = age.max()

ci_age = stats.t.interval(
    0.95,
    df=len(age) - 1,
    loc=mean_age,
    scale=sd_age / np.sqrt(len(age))
)

# Optional benchmark test against 27
t_age_27 = (mean_age - 27.0) / (sd_age / np.sqrt(len(age)))
p_age_27 = 2 * stats.t.sf(abs(t_age_27), df=len(age) - 1)

# -----------------------------
# Results table
# -----------------------------
results = pd.DataFrame([
    {
        "hypothesis": "H1 Domestic coach",
        "test": "Exact binomial test",
        "statistic": f"{k}/{n} = {prop_domestic:.4f}",
        "p_value": h1_binom.pvalue,
        "decision_0_05": "Reject H0" if h1_binom.pvalue < 0.05 else "Fail to reject H0"
    },
    {
        "hypothesis": "H2 Back-four rate",
        "test": "One-sample t-test vs 0.5",
        "statistic": f"t({n_back4 - 1}) = {t_back4:.4f}",
        "p_value": p_back4_t,
        "decision_0_05": "Reject H0" if p_back4_t < 0.05 else "Fail to reject H0"
    },
    {
        "hypothesis": "H2 Back-four rate",
        "test": "Wilcoxon signed-rank vs 0.5",
        "statistic": f"W = {wilcoxon_back4.statistic}",
        "p_value": wilcoxon_back4.pvalue,
        "decision_0_05": "Reject H0" if wilcoxon_back4.pvalue < 0.05 else "Fail to reject H0"
    },
    {
        "hypothesis": "H2 Dominant formation starts with 4",
        "test": "Exact binomial test",
        "statistic": f"{k_dom_form}/{n} = {prop_dom_form:.4f}",
        "p_value": h2_binom_domform.pvalue,
        "decision_0_05": "Reject H0" if h2_binom_domform.pvalue < 0.05 else "Fail to reject H0"
    },
    {
        "hypothesis": "H3 Age profile",
        "test": "Descriptive summary + 95% CI",
        "statistic": f"mean={mean_age:.4f}, sd={sd_age:.4f}, CI=[{ci_age[0]:.4f}, {ci_age[1]:.4f}]",
        "p_value": np.nan,
        "decision_0_05": "Use descriptive inference"
    },
    {
        "hypothesis": "H3 Optional benchmark",
        "test": "One-sample t-test vs 27.0",
        "statistic": f"t({len(age)-1}) = {t_age_27:.4f}",
        "p_value": p_age_27,
        "decision_0_05": "Reject H0" if p_age_27 < 0.05 else "Fail to reject H0"
    }
])

print("RESULTS TABLE")
display(results)

print("\nQuick summary")
print(f"H1 domestic coach proportion: {prop_domestic:.4f} ({k}/{n}), p={h1_binom.pvalue:.6f}")
print(f"H2 mean back_four_rate: {mean_back4:.4f}, t={t_back4:.4f}, p={p_back4_t:.10f}")
print(f"H2 Wilcoxon: W={wilcoxon_back4.statistic}, p={wilcoxon_back4.pvalue:.10f}")
print(f"H2 dominant formation starts with 4: {prop_dom_form:.4f} ({k_dom_form}/{n}), p={h2_binom_domform.pvalue:.10f}")
print(f"H3 avg_age mean={mean_age:.4f}, sd={sd_age:.4f}, median={median_age:.4f}, range=[{min_age:.4f}, {max_age:.4f}]")
print(f"H3 95% CI: [{ci_age[0]:.4f}, {ci_age[1]:.4f}]")
print(f"H3 optional benchmark vs 27.0: t={t_age_27:.4f}, p={p_age_27:.6f}")

results.to_csv("hypothesis_test_results.csv", index=False)
files.download("hypothesis_test_results.csv")