# Analysis Plan

## April 14 Milestone
This milestone covers:
- data collection
- exploratory data analysis
- hypothesis testing

## Unit of Analysis
For each selected league-season pair, the analysis compares:
- champion team
- runner-up team

## Variables to Collect
1. Total wage bill
2. Rotation size
3. 4-3-3 usage rate
4. Average squad age

## Hypotheses
### H1
Champions and runner-up teams do not differ significantly in total wage bill.

### H2
Champions do not use a significantly wider rotation than runner-up teams.

### H3
Champions use the 4-3-3 formation in a larger share of matches than runner-up teams.

### H4
Champions have a higher average squad age than runner-up teams.

## Planned Statistical Tests
- Paired t-test
- Wilcoxon signed-rank test (if needed)

## Output
A final dataset with one row per team-season and columns for:
- league
- season
- team
- rank
- wage_bill
- rotation_size
- formation_433_rate
- avg_age
