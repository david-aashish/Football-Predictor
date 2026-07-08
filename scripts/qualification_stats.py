"""
qualification_stats.py

Builds qualification statistics for every World Cup team
(2006, 2010, 2014, 2018, 2022).

Output:
    data/raw/qualification_stats.csv
"""

import pandas as pd
from pathlib import Path
from config import (
    WORLD_CUPS,
    TEAM_NAME_MAPPING
)

# ==========================================================
# Configuration
# ==========================================================

SOURCE_FILE = Path("data/raw/qualification_stats_source.csv")
ELO_FILE = Path("data/raw/elo.csv")
OUTPUT_FILE = Path("data/raw/qualification_stats.csv")


# ==========================================================
# Load Results
# ==========================================================

def load_results():

    print("Loading Results Dataset...")

    results = pd.read_csv(SOURCE_FILE)

    results["date"] = pd.to_datetime(results["date"])

    results["home_team"] = (
        results["home_team"]
        .replace(TEAM_NAME_MAPPING)
    )

    results["away_team"] = (
        results["away_team"]
        .replace(TEAM_NAME_MAPPING)
    )

    return results


# ==========================================================
# Load Elo
# ==========================================================

def load_elo():

    print("Loading Elo Dataset...")

    elo = pd.read_csv(ELO_FILE)

    return elo

# ==========================================================
# Keep Qualification Matches
# ==========================================================

def filter_qualification_matches(results):

    print("Filtering Qualification Matches...")

    qualification = results[
        results["tournament"] == "FIFA World Cup qualification"
    ].copy()

    return qualification

# ==========================================================
# Calculate Qualification Stats
# ==========================================================

def calculate_stats(matches, year, start_date, end_date):

    print("=" * 50)
    print(f"Processing {year}")
    print("=" * 50)

    # Keep only matches for this qualification campaign
    matches = matches[
        (matches["date"] >= start_date) &
        (matches["date"] <= end_date)
    ].copy()

    print(f"Qualification matches: {len(matches)}")

    return matches

# ==========================================================
# Initialize Team Statistics
# ==========================================================

def initialize_stats(elo, year):

    # Only the qualified teams for this World Cup
    teams = (
        elo[elo["Year"] == year]
        ["Team"]
        .sort_values()
        .tolist()
    )

    stats = {}

    for team in teams:

        stats[team] = {
        "Matches": 0,
        "Wins": 0,
        "Draws": 0,
        "Losses": 0,
        "Goals_For": 0,
        "Goals_Against": 0,
        "Goal_Difference": 0,
        "Points": 0
    }

    print(f"Qualified Teams: {len(stats)}")

    return stats

# ==========================================================
# Update Team Statistics
# ==========================================================

def update_stats(matches, stats, year):

    # Serbia was still Serbia and Montenegro during 2006 qualification
    if year == 2006:

        matches = matches.copy()

        matches["home_team"] = matches["home_team"].replace({
            "Serbia": "Serbia and Montenegro"
        })

        matches["away_team"] = matches["away_team"].replace({
            "Serbia": "Serbia and Montenegro"
        })

    for _, match in matches.iterrows():

        home = match["home_team"]
        away = match["away_team"]

        home_goals = int(match["home_score"])
        away_goals = int(match["away_score"])

        # =====================================================
        # Update Home Team (only if qualified)
        # =====================================================

        if home in stats:

            stats[home]["Matches"] += 1
            stats[home]["Goals_For"] += home_goals
            stats[home]["Goals_Against"] += away_goals

            if home_goals > away_goals:
                stats[home]["Wins"] += 1
                stats[home]["Points"] += 3

            elif home_goals == away_goals:
                stats[home]["Draws"] += 1
                stats[home]["Points"] += 1

            else:
                stats[home]["Losses"] += 1

        # =====================================================
        # Update Away Team (only if qualified)
        # =====================================================

        if away in stats:

            stats[away]["Matches"] += 1
            stats[away]["Goals_For"] += away_goals
            stats[away]["Goals_Against"] += home_goals

            if away_goals > home_goals:
                stats[away]["Wins"] += 1
                stats[away]["Points"] += 3

            elif away_goals == home_goals:
                stats[away]["Draws"] += 1
                stats[away]["Points"] += 1

            else:
                stats[away]["Losses"] += 1

    return stats

# ==========================================================
# Calculate Normalized Statistics
# ==========================================================

def calculate_normalized_stats(stats):

    for team in stats:

        matches = stats[team]["Matches"]

        stats[team]["Goal_Difference"] = (
            stats[team]["Goals_For"]
            - stats[team]["Goals_Against"]
        )

        if matches == 0:

            stats[team]["Win_Rate"] = 0
            stats[team]["Draw_Rate"] = 0
            stats[team]["Loss_Rate"] = 0

            stats[team]["Goals_For_Per_Game"] = 0
            stats[team]["Goals_Against_Per_Game"] = 0
            stats[team]["Goal_Difference_Per_Game"] = 0

            stats[team]["Points_Per_Game"] = 0

        else:

            stats[team]["Win_Rate"] = (
                stats[team]["Wins"] / matches
            )

            stats[team]["Draw_Rate"] = (
                stats[team]["Draws"] / matches
            )

            stats[team]["Loss_Rate"] = (
                stats[team]["Losses"] / matches
            )

            stats[team]["Goals_For_Per_Game"] = (
                stats[team]["Goals_For"] / matches
            )

            stats[team]["Goals_Against_Per_Game"] = (
                stats[team]["Goals_Against"] / matches
            )

            stats[team]["Goal_Difference_Per_Game"] = (
                stats[team]["Goal_Difference"] / matches
            )

            stats[team]["Points_Per_Game"] = (
                stats[team]["Points"] / matches
            )

    return stats

# ==========================================================
# Convert Dictionary to DataFrame
# ==========================================================

def stats_to_dataframe(stats, year):

    rows = []

    for team, values in stats.items():

        rows.append({

            "Year": year,
            "Team": team,

            "Matches": values["Matches"],

            "Win_Rate": values["Win_Rate"],
            "Draw_Rate": values["Draw_Rate"],
            "Loss_Rate": values["Loss_Rate"],

            "Goals_For_Per_Game":
                values["Goals_For_Per_Game"],

            "Goals_Against_Per_Game":
                values["Goals_Against_Per_Game"],

            "Goal_Difference_Per_Game":
                values["Goal_Difference_Per_Game"],

            "Points_Per_Game":
                values["Points_Per_Game"]

        })

    return pd.DataFrame(rows)

# ==========================================================
# Save Dataset
# ==========================================================

def save_dataset(df):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("=" * 50)
    print("Qualification Dataset Saved!")
    print("=" * 50)
    print()
    print(f"Rows : {len(df)}")
    print(f"Saved: {OUTPUT_FILE}")

# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    results = load_results()

    elo = load_elo()

    qualification = filter_qualification_matches(results)

    all_dfs = []

    for year in WORLD_CUPS:

        matches = calculate_stats(
            qualification,
            year,
            WORLD_CUPS[year]["start"],
            WORLD_CUPS[year]["end"]
        )

        stats = initialize_stats(elo, year)
        stats = update_stats(matches, stats, year)
        stats = calculate_normalized_stats(stats)

        df = stats_to_dataframe(stats, year)

        all_dfs.append(df)

    final_df = pd.concat(
        all_dfs,
        ignore_index=True
    )

    save_dataset(final_df)