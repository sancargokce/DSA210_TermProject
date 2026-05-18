"""
Build the final champion profile dataset for the DSA 210 football project.

This script:
1. Loads raw CSV files
2. Matches target champion teams to club IDs
3. Builds coach / formation / back-four features from match-level data
4. Builds minutes-weighted average age from appearances + players
5. Merges manual coach nationality information
6. Derives the domestic_coach indicator
7. Writes the final processed dataset and source-tracking table

Expected input files in the working directory (or in --input-dir):
- target_teams.csv
- games.csv
- players.csv
- appearances.csv

Outputs (written to --output-dir):
- champion_profile_dataset.csv
- source_tracking.csv
"""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

LEAGUE_CODE_MAP = {
    "premier league": "GB1",
    "la liga": "ES1",
    "serie a": "IT1",
    "bundesliga": "L1",
    "ligue 1": "FR1",
    "eredivisie": "NL1",
    "primeira liga": "PO1",
    "super lig": "TR1",
    "süper lig": "TR1",
    "belgian pro league": "BE1",
}

# Manual club-ID fixes for teams that were difficult to match reliably
MANUAL_CLUB_IDS = {
    ("Belgian Pro League", "2019-2020", "Club Brugge"): 2282,
    ("Belgian Pro League", "2020-2021", "Club Brugge"): 2282,
    ("Belgian Pro League", "2021-2022", "Club Brugge"): 2282,
    ("Belgian Pro League", "2022-2023", "Royal Antwerp"): 1096,
    ("Belgian Pro League", "2023-2024", "Club Brugge"): 2282,
    ("Eredivisie", "2018-2019", "Ajax"): 610,
    ("Eredivisie", "2020-2021", "Ajax"): 610,
    ("Eredivisie", "2021-2022", "Ajax"): 610,
    ("Eredivisie", "2023-2024", "PSV Eindhoven"): 383,
    ("Ligue 1", "2020-2021", "Lille"): 1082,
    ("Primeira Liga", "2019-2020", "Porto"): 720,
    ("Primeira Liga", "2020-2021", "Sporting CP"): 336,
    ("Primeira Liga", "2021-2022", "Porto"): 720,
    ("Primeira Liga", "2023-2024", "Sporting CP"): 336,
    ("Serie A", "2020-2021", "Inter"): 46,
    ("Serie A", "2021-2022", "AC Milan"): 5,
    ("Serie A", "2022-2023", "Napoli"): 6195,
    ("Serie A", "2023-2024", "Inter"): 46,
}

COACH_NATIONALITY = {
    "Abdullah Avcı": "Turkish",
    "Antonio Conte": "Italian",
    "Arne Slot": "Dutch",
    "Carlo Ancelotti": "Italian",
    "Christophe Galtier": "French",
    "Diego Simeone": "Argentine",
    "Erik ten Hag": "Dutch",
    "Hansi Flick": "German",
    "Jürgen Klopp": "German",
    "Julian Nagelsmann": "German",
    "Luis Enrique": "Spanish",
    "Luciano Spalletti": "Italian",
    "Mark van Bommel": "Dutch",
    "Mauricio Pochettino": "Argentine",
    "Maurizio Sarri": "Italian",
    "Okan Buruk": "Turkish",
    "Pep Guardiola": "Spanish",
    "Peter Bosz": "Dutch",
    "Philippe Clement": "Belgian",
    "Roger Schmidt": "German",
    "Ronny Deila": "Norwegian",
    "Rúben Amorim": "Portuguese",
    "Sergen Yalçın": "Turkish",
    "Simone Inzaghi": "Italian",
    "Sérgio Conceição": "Portuguese",
    "Stefano Pioli": "Italian",
    "Thomas Tuchel": "German",
    "Xabi Alonso": "Spanish",
    "Xavi": "Spanish",
    "Zinédine Zidane": "French",
}

COUNTRY_TO_NATIONALITY = {
    "England": "English",
    "Spain": "Spanish",
    "Italy": "Italian",
    "Germany": "German",
    "France": "French",
    "Netherlands": "Dutch",
    "Portugal": "Portuguese",
    "Turkey": "Turkish",
    "Belgium": "Belgian",
}


# ---------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------

def normalize_text(value: object) -> str:
    """Normalize text for safer matching."""
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = text.replace("’", "'").replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def similarity_score(a: str, b: str) -> float:
    """A lightweight similarity heuristic for team-name fallback matching."""
    a_tokens = set(a.split())
    b_tokens = set(b.split())

    if not a_tokens or not b_tokens:
        return 0.0

    overlap = len(a_tokens & b_tokens) / len(a_tokens | b_tokens)
    bonus = 0.0
    if a == b:
        bonus += 0.30
    elif a in b or b in a:
        bonus += 0.10
    return overlap + bonus


def mode_or_nan(series: pd.Series) -> object:
    """Return the mode of a series or NaN if empty."""
    cleaned = series.dropna().astype(str)
    if cleaned.empty:
        return np.nan
    return cleaned.mode().iloc[0]


# ---------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------

def load_inputs(input_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load required CSV inputs."""
    targets = pd.read_csv(input_dir / "target_teams.csv")
    games = pd.read_csv(input_dir / "games.csv")
    players = pd.read_csv(input_dir / "players.csv")
    appearances = pd.read_csv(input_dir / "appearances.csv")
    return targets, games, players, appearances


def prepare_targets(targets: pd.DataFrame) -> pd.DataFrame:
    """Add derived fields needed for matching targets to competition and season."""
    targets = targets.copy()
    targets["league_key"] = targets["league"].apply(normalize_text)
    targets["competition_code"] = targets["league_key"].map(LEAGUE_CODE_MAP)
    targets["season_start"] = targets["season"].astype(str).str.split("-").str[0].astype(int)
    targets["team_key"] = targets["team"].apply(normalize_text)
    return targets


def build_team_games(games: pd.DataFrame) -> pd.DataFrame:
    """Create a long team-match table from home and away records."""
    games = games.copy()
    games["season"] = pd.to_numeric(games["season"], errors="coerce")

    home = games[
        [
            "game_id",
            "competition_id",
            "season",
            "date",
            "home_club_id",
            "home_club_name",
            "home_club_manager_name",
            "home_club_formation",
        ]
    ].rename(
        columns={
            "home_club_id": "club_id",
            "home_club_name": "team_name",
            "home_club_manager_name": "coach_name",
            "home_club_formation": "formation",
        }
    )

    away = games[
        [
            "game_id",
            "competition_id",
            "season",
            "date",
            "away_club_id",
            "away_club_name",
            "away_club_manager_name",
            "away_club_formation",
        ]
    ].rename(
        columns={
            "away_club_id": "club_id",
            "away_club_name": "team_name",
            "away_club_manager_name": "coach_name",
            "away_club_formation": "formation",
        }
    )

    team_games = pd.concat([home, away], ignore_index=True)
    team_games["team_key"] = team_games["team_name"].apply(normalize_text)
    return team_games


def match_targets_to_clubs(targets: pd.DataFrame, team_games: pd.DataFrame) -> pd.DataFrame:
    """Match each target champion to a club_id."""
    matches = []

    for _, row in targets.iterrows():
        subset = team_games[
            (team_games["competition_id"] == row["competition_code"])
            & (team_games["season"] == row["season_start"])
        ][["club_id", "team_name", "team_key"]].drop_duplicates()

        key = (row["league"], row["season"], row["team"])

        if key in MANUAL_CLUB_IDS:
            club_id = MANUAL_CLUB_IDS[key]
            forced = subset[subset["club_id"] == club_id]
            if not forced.empty:
                matched_name = forced.iloc[0]["team_name"]
                match_method = "manual_club_id"
            else:
                matched_name = np.nan
                club_id = np.nan
                match_method = "manual_club_id_failed"
        else:
            best_score = -1.0
            best_row = None

            for _, candidate in subset.iterrows():
                score = similarity_score(row["team_key"], candidate["team_key"])
                if score > best_score:
                    best_score = score
                    best_row = candidate

            if best_row is not None and best_score >= 0.20:
                club_id = best_row["club_id"]
                matched_name = best_row["team_name"]
                match_method = "fuzzy"
            else:
                club_id = np.nan
                matched_name = np.nan
                match_method = "unmatched"

        matches.append(
            {
                "league": row["league"],
                "league_country": row["league_country"],
                "season": row["season"],
                "team": row["team"],
                "competition_code": row["competition_code"],
                "season_start": row["season_start"],
                "club_id": club_id,
                "matched_team_name": matched_name,
                "match_method": match_method,
            }
        )

    target_map = pd.DataFrame(matches)
    if target_map["club_id"].isna().any():
        missing = target_map[target_map["club_id"].isna()][["league", "season", "team"]]
        raise ValueError(f"Unmatched target teams remain:\n{missing.to_string(index=False)}")

    return target_map


def build_relevant_team_games(team_games: pd.DataFrame, target_map: pd.DataFrame) -> pd.DataFrame:
    """Restrict team-match table to only matched champion teams."""
    relevant = team_games.merge(
        target_map[
            ["league", "league_country", "season", "team", "competition_code", "season_start", "club_id"]
        ],
        left_on=["competition_id", "season", "club_id"],
        right_on=["competition_code", "season_start", "club_id"],
        how="inner",
    )

    relevant = relevant.rename(columns={"season_x": "season_numeric", "season_y": "season"})
    return relevant


def summarize_match_level_features(relevant_team_games: pd.DataFrame) -> pd.DataFrame:
    """Summarize coach and formation features from relevant champion matches."""
    df = relevant_team_games.copy()
    df["is_back_four"] = df["formation"].astype(str).str.startswith("4").astype(float)
    df.loc[df["formation"].isna(), "is_back_four"] = np.nan

    summary = (
        df.groupby(["league", "league_country", "season", "team"], as_index=False)
        .agg(
            coach_name=("coach_name", mode_or_nan),
            dominant_formation=("formation", mode_or_nan),
            back_four_rate=("is_back_four", "mean"),
        )
    )
    return summary


def build_avg_age_summary(
    relevant_team_games: pd.DataFrame,
    players: pd.DataFrame,
    appearances: pd.DataFrame,
) -> pd.DataFrame:
    """Compute minutes-weighted average age for each champion team-season."""
    players_sub = players[["player_id", "date_of_birth"]].drop_duplicates().copy()
    players_sub["date_of_birth"] = pd.to_datetime(players_sub["date_of_birth"], errors="coerce")

    appearances = appearances.copy()
    appearances["date"] = pd.to_datetime(appearances["date"], errors="coerce")
    appearances["minutes_played"] = pd.to_numeric(appearances["minutes_played"], errors="coerce")

    linked = appearances.merge(
        relevant_team_games[
            ["game_id", "club_id", "league", "league_country", "season", "team"]
        ].drop_duplicates(),
        left_on=["game_id", "player_club_id"],
        right_on=["game_id", "club_id"],
        how="inner",
    )

    linked = linked.merge(players_sub, on="player_id", how="left")
    linked["age_years"] = (linked["date"] - linked["date_of_birth"]).dt.days / 365.25
    linked = linked.dropna(subset=["age_years", "minutes_played"]).copy()
    linked["age_x_minutes"] = linked["age_years"] * linked["minutes_played"]

    avg_age = (
        linked.groupby(["league", "league_country", "season", "team"], as_index=False)
        .agg(total_age_minutes=("age_x_minutes", "sum"), total_minutes=("minutes_played", "sum"))
    )
    avg_age["avg_age"] = avg_age["total_age_minutes"] / avg_age["total_minutes"]

    return avg_age[["league", "league_country", "season", "team", "avg_age"]]


def merge_coach_nationality(df: pd.DataFrame) -> pd.DataFrame:
    """Add coach nationality and derive domestic coach indicator."""
    df = df.copy()
    coach_lookup = pd.DataFrame(
        {"coach_name": list(COACH_NATIONALITY.keys()), "coach_nationality": list(COACH_NATIONALITY.values())}
    )

    df = df.merge(coach_lookup, on="coach_name", how="left")
    df["expected_domestic_nationality"] = df["league_country"].map(COUNTRY_TO_NATIONALITY)
    df["domestic_coach"] = (
        df["coach_nationality"].astype(str).str.strip().str.lower()
        == df["expected_domestic_nationality"].astype(str).str.strip().str.lower()
    ).astype("Int64")
    df = df.drop(columns=["expected_domestic_nationality"])
    return df


def build_final_dataset(
    targets: pd.DataFrame,
    profile_from_games: pd.DataFrame,
    avg_age_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Combine all features into the final processed dataset."""
    final_df = targets[["league", "league_country", "season", "team"]].drop_duplicates().copy()
    final_df = final_df.merge(
        profile_from_games,
        on=["league", "league_country", "season", "team"],
        how="left",
    )
    final_df = final_df.merge(
        avg_age_summary,
        on=["league", "league_country", "season", "team"],
        how="left",
    )

    final_df = merge_coach_nationality(final_df)
    final_df["source_notes"] = (
        "coach_name, dominant_formation, back_four_rate from games.csv; "
        "avg_age from appearances.csv + players.csv; "
        "coach_nationality from manual lookup"
    )

    final_df = final_df[
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

    return final_df


def build_source_tracking(final_df: pd.DataFrame) -> pd.DataFrame:
    """Create variable-level source tracking for the final dataset."""
    rows = []

    for _, row in final_df.iterrows():
        shared = [row["league"], row["league_country"], row["season"], row["team"]]

        if pd.notna(row["coach_name"]):
            rows.append(shared + ["coach_name", "games.csv", "", "Extracted from manager fields in match-level data"])

        if pd.notna(row["coach_nationality"]):
            rows.append(shared + ["coach_nationality", "manual coach lookup", "", "Assigned from manual coach nationality lookup table"])

        if pd.notna(row["domestic_coach"]):
            rows.append(shared + ["domestic_coach", "derived from coach nationality", "", "1 if coach nationality matches league country; otherwise 0"])

        if pd.notna(row["dominant_formation"]):
            rows.append(shared + ["dominant_formation", "games.csv", "", "Most frequent team-side formation across league matches"])

        if pd.notna(row["back_four_rate"]):
            rows.append(shared + ["back_four_rate", "games.csv", "", "Share of league matches where formation starts with 4"])

        if pd.notna(row["avg_age"]):
            rows.append(shared + ["avg_age", "appearances.csv + players.csv", "", "Minutes-weighted average squad age"])

    source_tracking = pd.DataFrame(
        rows,
        columns=[
            "league",
            "league_country",
            "season",
            "team",
            "variable",
            "source_name",
            "source_link",
            "notes",
        ],
    )
    return source_tracking


def run_pipeline(input_dir: Path, output_dir: Path) -> None:
    """Run the full dataset-building pipeline and save outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)

    targets, games, players, appearances = load_inputs(input_dir)
    targets = prepare_targets(targets)
    team_games = build_team_games(games)
    target_map = match_targets_to_clubs(targets, team_games)
    relevant_team_games = build_relevant_team_games(team_games, target_map)

    profile_from_games = summarize_match_level_features(relevant_team_games)
    avg_age_summary = build_avg_age_summary(relevant_team_games, players, appearances)
    final_df = build_final_dataset(targets, profile_from_games, avg_age_summary)
    source_tracking = build_source_tracking(final_df)

    final_df.to_csv(output_dir / "champion_profile_dataset.csv", index=False)
    source_tracking.to_csv(output_dir / "source_tracking.csv", index=False)

    print(f"Saved dataset to: {output_dir / 'champion_profile_dataset.csv'}")
    print(f"Saved source tracking to: {output_dir / 'source_tracking.csv'}")
    print(f"Rows in final dataset: {len(final_df)}")
    print(final_df.head())


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Build the final champion profile dataset.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("."),
        help="Directory containing raw input CSV files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Directory where output CSV files will be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_pipeline(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
