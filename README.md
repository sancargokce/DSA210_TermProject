# DSA210_TermProject  
# Profiling Championship-Winning Football Teams Across Leagues

DSA 210 - Introduction to Data Science  
Spring 2025-2026  
Sabancı University  
Student: Sancar Tegin Gökçe

* * *

This repository contains the full technical implementation, datasets, statistical tests, exploratory analysis, and machine learning outputs for the project.  
The aim of the project is to identify whether championship-winning football teams across multiple leagues share a common managerial, tactical, and squad-level profile.

---

## Project Overview

This project investigates whether league champions across Europe and Turkey display recurring structural patterns.  
Instead of comparing only champions and runners-up within one league, the project directly focuses on **championship-winning teams** from multiple countries and seasons, and asks whether they share a broader “champion profile.”

The analysis is built around three core dimensions:

- **Managerial profile** → domestic vs foreign coach  
- **Tactical profile** → dominant formation and back-four usage  
- **Squad profile** → average age  

### Central Question
> Is there a cross-league “champion profile” in terms of coach background, tactical structure, and squad age?

* * *

## Motivation

Football analysis often focuses on team quality, individual talent, or financial strength. However, title-winning teams may also share hidden structural similarities that are not immediately visible from points tables alone.

This project was motivated by three broad questions:

1. Do champions tend to work with **domestic coaches**?
2. Do champions tend to prefer **back-four defensive systems**?
3. Do champions cluster around a specific **average age profile**?

The goal is not to claim that these factors *cause* championships on their own, but to investigate whether they repeatedly appear among title-winning teams across different leagues and seasons.

* * *

## Research Questions and Hypotheses

### H1 — Domestic Coach Hypothesis
- **H0:** Coach nationality has no meaningful association with championship-winning teams.
- **H1:** Championship-winning teams tend to work with domestic coaches.

### H2 — Back-Four Hypothesis
- **H0:** Defensive shape has no meaningful association with championship-winning teams.
- **H2:** Championship-winning teams tend to use back-four systems more frequently.

### H3 — Age Profile Hypothesis
- **H0:** Average squad age does not display a meaningful pattern among championship-winning teams.
- **H3:** Championship-winning teams tend to cluster around a common age profile.

* * *

## Main Findings (Summary)

| Hypothesis | Result | P-value / Evidence | Key Insight |
|---|---:|---:|---|
| **H1: Champions tend to work with domestic coaches** | ⚠️ Weakly Supported | Exact binomial test: **p = 0.0362** | 29 of 45 champions had domestic coaches, but the margin is not overwhelming |
| **H2: Champions tend to prefer back-four systems** | ✅ Strongly Supported | t-test: **p = 1.38e-07**; Wilcoxon: **p = 1.54e-05** | Champions overwhelmingly use back-four structures |
| **H2b: Dominant formation starts with 4** | ✅ Strongly Supported | Exact binomial test: **p = 7.69e-06** | 37 of 45 champion teams had a dominant formation beginning with 4 |
| **H3: Champions share a common age profile** | ✅ Descriptively Supported | Mean = **27.10**, 95% CI = **[26.72, 27.48]** | Champion teams cluster in a relatively narrow age band |
| **ML Stage: Unsupervised champion profiling** | ✅ Completed | K-Means + PCA + Hierarchical Clustering | Latent champion archetypes were explored through clustering |

**Overall interpretation:**  
The strongest evidence appears in the **tactical dimension**.  
The **domestic-coach hypothesis** receives some support, but not strong enough to be treated as a dominant finding.  
The **age hypothesis** is better interpreted as a descriptive concentration rather than as a sharp inferential result.

* * *

## Dataset

The final dataset contains **45 observations**, where each observation corresponds to **one champion team in one league-season**.

### Leagues included
- Premier League
- La Liga
- Serie A
- Bundesliga
- Ligue 1
- Eredivisie
- Primeira Liga
- Süper Lig
- Belgian Pro League

### Time coverage
The dataset mainly covers the **2019-2020 to 2023-2024** seasons, with Eredivisie also including **2018-2019**.

### Final variables
- `league`
- `league_country`
- `season`
- `team`
- `coach_name`
- `coach_nationality`
- `domestic_coach`
- `dominant_formation`
- `back_four_rate`
- `avg_age`
- `source_notes`

* * *

## Data Sources

The project combines automated extraction and manual enrichment.

### Automated sources
- **games.csv**
  - `coach_name`
  - `dominant_formation`
  - `back_four_rate`

- **appearances.csv + players.csv**
  - `avg_age` (minutes-weighted average age)

### Manual enrichment
- `coach_nationality` was added via a manually constructed coach lookup table
- `domestic_coach` was derived by comparing coach nationality with league country

### Data tracking
The variable-level documentation is stored in:

- `data/raw/source_tracking.csv`

* * *

## Data Collection and Processing

### 1. Champion list creation
A target champion list was first defined in `target_teams.csv`.

### 2. Team matching
Because team names differ across datasets, a hybrid matching pipeline was built using:
- competition-based filtering
- season filtering
- fuzzy matching
- manual club ID overrides
- post-processing validation

### 3. Variable construction
- **coach_name** was extracted from manager fields in match-level data
- **dominant_formation** was defined as the most frequent formation used by the champion team
- **back_four_rate** was computed as the proportion of league matches where the formation begins with `4`
- **avg_age** was calculated as a minutes-weighted squad age
- **coach_nationality** was added manually
- **domestic_coach** was generated as a binary indicator

### 4. Final data validation
After patching and validation, **no unmatched team remained in the final pipeline**.

* * *

## Exploratory Data Analysis (EDA)

The EDA stage focused on both data quality and distributional structure.

### Outputs produced
- data completion report
- coach nationality counts
- domestic vs foreign coach counts
- dominant formation counts
- average age distribution
- back-four rate distribution

### Descriptive observations
- The final dataset is complete for the final variables used in analysis
- **29** champions were coached by domestic managers, **16** by foreign managers
- The most common dominant formations are:
  - `4-3-3 Attacking`
  - `4-2-3-1`
  - `4-3-3 Defending`
- Average squad age is mostly concentrated between roughly **26 and 28**
- Back-four usage is heavily concentrated near **1.0**, indicating that many champions relied on four-man defensive structures

* * *

## Hypothesis Testing

### H1 — Domestic Coach Hypothesis

- **H0:** Championship-winning teams do not meaningfully favor domestic coaches  
- **H1:** Championship-winning teams tend to work with domestic coaches

#### Test used
- Exact binomial test against 0.5 benchmark

#### Result
- Domestic coach count: **29 / 45 = 0.6444**
- P-value: **0.0362**

#### Interpretation
This result suggests a tendency toward domestic coaches among champions, but the result is **not overwhelmingly strong**.  
The observed split (29 vs 16) shows an imbalance, yet not a decisive one.

> **H1 is weakly supported.**

---

### H2 — Back-Four Hypothesis

- **H0:** Championship-winning teams do not meaningfully favor back-four systems  
- **H2:** Championship-winning teams tend to prefer back-four systems

#### Tests used
- One-sample t-test vs 0.5
- Wilcoxon signed-rank test vs 0.5
- Exact binomial test for whether dominant formation starts with `4`

#### Results
- Mean `back_four_rate`: **0.8005**
- One-sample t-test: **t(44) = 6.0595**, **p = 1.38e-07**
- Wilcoxon signed-rank test: **W = 842.0**, **p = 1.54e-05**
- Dominant formation starts with `4`: **37 / 45 = 0.8222**, **p = 7.69e-06**

#### Interpretation
This is the clearest result in the project.  
Championship-winning teams overwhelmingly rely on back-four systems, both in match-level usage and in their dominant tactical identity.

> **H2 is strongly supported.**

---

### H3 — Age Profile Hypothesis

- **H0:** Championship-winning teams do not display a meaningful common age profile  
- **H3:** Championship-winning teams cluster around a common age profile

#### Analysis used
- Descriptive summary
- 95% confidence interval
- Optional benchmark t-test vs 27.0

#### Results
- Mean age: **27.0985**
- Standard deviation: **1.2643**
- 95% CI: **[26.7186, 27.4783]**
- Optional benchmark test vs 27.0: **p = 0.6040**

#### Interpretation
The benchmark test against 27.0 is not significant, which is not a problem for the project’s main interpretation.  
The more important result is that champion teams are concentrated in a **relatively narrow age range**, rather than being scattered widely across very young and very old profiles.

> **H3 is descriptively supported.**

* * *

## Machine Learning Stage

Since the dataset contains only championship-winning teams, supervised prediction was not appropriate at this stage.  
Instead, the ML component focused on **unsupervised learning** to identify hidden champion archetypes.

### Methods applied
- **K-Means Clustering**
- **Hierarchical Clustering**
- **PCA (Principal Component Analysis)**

### Features used
- `domestic_coach`
- `back_four_rate`
- `avg_age`

### Purpose
The goal of the ML stage was not to predict championships, but to see whether champions themselves form distinct internal subgroups such as:

- domestic-coach / back-four-heavy champions
- foreign-coach / tactically flexible champions
- older vs younger champion profiles

### Outputs produced
- K-Means model selection table
- cluster summary table
- PCA cluster visualization
- hierarchical clustering dendrogram

* * *

## Repository Structure

```text
DSA210_TermProject/
│
├── data/
│   ├── raw/
│   │   ├── target_teams.csv
│   │   ├── source_tracking.csv
│   │   └── transfermarkt/
│   └── processed/
│       ├── champion_profile_dataset.csv
│       └── champion_profile_dataset_with_ml.csv
│
├── outputs/
│   ├── figures/
│   │   ├── avg_age_distribution.png
│   │   ├── back_four_rate_distribution.png
│   │   ├── domestic_vs_foreign_coaches.png
│   │   ├── dominant_formations.png
│   │   ├── ml_pca_clusters.png
│   │   └── ml_dendrogram.png
│   └── tables/
│       ├── data_completion_report.csv
│       ├── profile_summary.csv
│       ├── coach_nationality_counts.csv
│       ├── dominant_formation_counts.csv
│       ├── domestic_coach_counts.csv
│       ├── hypothesis_test_results.csv
│       ├── ml_cluster_summary.csv
│       └── ml_kmeans_model_selection.csv
│
├── src/
│   ├── build_dataset.py
│   └── champion_profile_analysis.py
│
├── notebooks/
├── README.md
└── requirements.txt
