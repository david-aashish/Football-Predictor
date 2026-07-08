"""
qualification_stats_2026.py

Builds qualification statistics for
the 2026 FIFA World Cup prediction dataset.

Output:
    data/raw/qualification_stats_2026.csv
"""

import pandas as pd
from pathlib import Path
from config import TEAM_NAME_MAPPING

# ==========================================================
# Configuration
# ==========================================================

SOURCE_FILE = Path("data/raw/qualification_stats_source.csv")

ELO_FILE = Path("data/raw/elo_2026.csv")

OUTPUT_FILE = Path(
    "data/raw/qualification_stats_2026.csv"
)

# Approximate qualification campaign

START_DATE = "2023-09-07"

END_DATE = "2026-03-31"

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
# Load Qualified Teams
# ==========================================================

def load_elo():

    print("Loading 2026 Teams...")

    return pd.read_csv(ELO_FILE)


# ==========================================================
# Keep Qualification Matches
# ==========================================================

def filter_qualification_matches(results):

    qualification = results[
        results["tournament"] == "FIFA World Cup qualification"
    ].copy()

    qualification = qualification[
        (qualification["date"] >= START_DATE)
        &
        (qualification["date"] <= END_DATE)
    ]

    print(f"Qualification matches: {len(qualification)}")

    return qualification


# ==========================================================
# Initialize Statistics
# ==========================================================

def initialize_stats(elo):

    teams = elo["Team"].sort_values().tolist()

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
# Update Statistics
# ==========================================================

def update_stats(matches, stats):

    for _, match in matches.iterrows():

        home = match["home_team"]
        away = match["away_team"]

        hg = int(match["home_score"])
        ag = int(match["away_score"])

        # Home

        if home in stats:

            stats[home]["Matches"] += 1

            stats[home]["Goals_For"] += hg
            stats[home]["Goals_Against"] += ag

            if hg > ag:

                stats[home]["Wins"] += 1
                stats[home]["Points"] += 3

            elif hg == ag:

                stats[home]["Draws"] += 1
                stats[home]["Points"] += 1

            else:

                stats[home]["Losses"] += 1

        # Away

        if away in stats:

            stats[away]["Matches"] += 1

            stats[away]["Goals_For"] += ag
            stats[away]["Goals_Against"] += hg

            if ag > hg:

                stats[away]["Wins"] += 1
                stats[away]["Points"] += 3

            elif ag == hg:

                stats[away]["Draws"] += 1
                stats[away]["Points"] += 1

            else:

                stats[away]["Losses"] += 1

    return stats


# ==========================================================
# Normalize Statistics
# ==========================================================

def calculate_normalized_stats(stats):

    for team in stats:

        matches = stats[team]["Matches"]

        stats[team]["Goal_Difference"] = (

            stats[team]["Goals_For"]

            -

            stats[team]["Goals_Against"]

        )

        if matches == 0:

            stats[team]["Win_Rate"] = 0

            stats[team]["Draw_Rate"] = 0

            stats[team]["Loss_Rate"] = 0

            stats[team]["Goals_For_Per_Game"] = 0

            stats[team]["Goals_Against_Per_Game"] = 0

            stats[team]["Goal_Difference_Per_Game"] = 0

            stats[team]["Points_Per_Game"] = 0

            continue

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
# Convert to DataFrame
# ==========================================================

def stats_to_dataframe(stats):

    rows = []

    for team, values in stats.items():

        rows.append({

            "Year": 2026,

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
# Save
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

    stats = initialize_stats(elo)

    stats = update_stats(
        qualification,
        stats
    )

    stats = calculate_normalized_stats(stats)

    df = stats_to_dataframe(stats)

    save_dataset(df)