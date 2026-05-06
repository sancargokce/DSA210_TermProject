# DSA210 Term Project  
## Profiling Championship-Winning Football Teams Across Leagues

### Project Overview
This project investigates whether championship-winning football teams across different countries share a common profile.  
Instead of comparing only champions and runners-up inside a single league, the project focuses on **league champions** from multiple countries and seasons, and asks whether these teams display recurring managerial, tactical, and squad-level patterns.

The main goal is to identify whether title-winning teams tend to:
- work with **domestic coaches**,
- prefer **back-four defensive structures**,
- and share a similar **average squad age profile**.

---

## Research Questions

### RQ1
Do championship-winning teams tend to work with domestic coaches?

- **H0:** Coach nationality is not meaningfully associated with championship-winning teams.
- **H1:** Championship-winning teams tend to work with domestic coaches.

### RQ2
Do championship-winning teams tend to prefer back-four defensive systems?

- **H0:** Defensive shape has no meaningful relationship with championship-winning teams.
- **H2:** Championship-winning teams tend to use back-four systems more frequently.

### RQ3
Is there a common age profile among championship-winning teams?

- **H0:** Average squad age does not show a meaningful pattern among champions.
- **H3:** Championship-winning teams tend to cluster around a specific age profile.

---

## Unit of Analysis
Each observation represents **one league champion in one league-season**.

---

## Dataset
The final dataset contains champion teams from the following leagues:

- Premier League
- La Liga
- Serie A
- Bundesliga
- Ligue 1
- Eredivisie
- Primeira Liga
- Süper Lig
- Belgian Pro League

The dataset includes **45 observations** in total and covers mostly the **2019–2020 to 2023–2024** seasons, with Eredivisie also including **2018–2019**. The final table includes the following columns: `league`, `league_country`, `season`, `team`, `coach_name`, `coach_nationality`, `domestic_coach`, `dominant_formation`, `back_four_rate`, `avg_age`, and `source_notes`. :contentReference[oaicite:0]{index=0}

---

## Variables

### Core variables
- **coach_name**: Head coach of the champion team
- **coach_nationality**: Nationality of the coach
- **domestic_coach**: Binary indicator showing whether the coach nationality matches the league country
- **dominant_formation**: Most frequently observed formation used by the champion team
- **back_four_rate**: Share of matches in which the team used a formation beginning with “4”
- **avg_age**: Minutes-weighted average squad age

---

## Data Sources
This project combines automated extraction and manual enrichment.

### Automated sources
- `games.csv`
  - used for coach name
  - used for dominant formation
  - used for back-four rate

- `appearances.csv` + `players.csv`
  - used to calculate minutes-weighted average age

### Manual enrichment
- `coach_nationality` was added through a manually constructed coach lookup table
- `domestic_coach` was derived by comparing coach nationality to league country

Source tracking for each variable is documented in:
- `data/raw/source_tracking.csv`

---

## Methodology

### 1. Team selection
A champion list was manually defined in `target_teams.csv`.

### 2. Data extraction
Relevant records were filtered from large football datasets using:
- competition code
- season
- champion club identity

### 3. Team matching
Because team names vary across sources, a hybrid matching strategy was used:
- fuzzy matching,
- manual club ID overrides for difficult cases,
- post-processing validation.

### 4. Variable construction
- **coach_name** was extracted from manager fields in match-level data
- **dominant_formation** was defined as the most common team-side formation
- **back_four_rate** was computed as the proportion of matches where formation starts with `4`
- **avg_age** was calculated as a minutes-weighted average based on player appearances and birth dates
- **domestic_coach** was generated after nationality merge

### 5. Exploratory analysis
Summary tables and figures were created to inspect:
- completeness of the final dataset,
- distribution of coach nationalities,
- distribution of domestic vs foreign coaches,
- dominant formation frequencies,
- average age distribution,
- back-four rate distribution.

---

## Outputs

### Tables
Located in `outputs/tables/`:
- `data_completion_report.csv`
- `profile_summary.csv`
- `coach_nationality_counts.csv`
- `dominant_formation_counts.csv`
- `domestic_coach_counts.csv`

### Figures
Located in `outputs/figures/`:
- `domestic_vs_foreign_coaches.png`
- `dominant_formations.png`
- `avg_age_distribution.png`
- `back_four_rate_distribution.png`

---

## Current Findings
At the current stage, the dataset suggests a few clear patterns:

- The final dataset contains **45 complete observations**. :contentReference[oaicite:1]{index=1}
- Among champion teams, **29** are coached by domestic managers and **16** by foreign managers. :contentReference[oaicite:2]{index=2}
- The most common dominant formations are led by **4-3-3 Attacking** and **4-2-3-1**. :contentReference[oaicite:3]{index=3}
- Back-four usage is highly concentrated near **1.0**, suggesting that many champions relied heavily on four-man defensive structures. 
- Average squad age is concentrated mostly in the **mid-to-late twenties**, rather than at very low or very high values. :contentReference[oaicite:5]{index=5}

These findings are exploratory and are intended to motivate the final interpretation rather than serve as definitive causal conclusions.

---

## Limitations
This project has several limitations:

- The dataset is relatively small (**45 observations**).
- `coach_nationality` was manually enriched rather than directly scraped from one unified source.
- Team-name inconsistencies across sources required manual matching corrections.
- Formation labels are not perfectly standardized (for example, `4-3-3 Attacking` and `4-3-3 Defending` are treated separately).
- The study is descriptive and exploratory; it does not establish causal effects.

---

## Next Steps
Possible extensions include:

- standardizing formation labels into broader tactical families,
- adding statistical hypothesis tests,
- incorporating more leagues and earlier seasons,
- comparing champions with runners-up or top-four teams,
- examining whether coach nationality, tactical shape, and age profile interact with one another.

---

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
│       └── champion_profile_dataset.csv
│
├── outputs/
│   ├── figures/
│   └── tables/
│
├── src/
│   ├── build_dataset.py
│   └── champion_profile_analysis.py
│
├── notebooks/
├── README.md
└── requirements.txt
