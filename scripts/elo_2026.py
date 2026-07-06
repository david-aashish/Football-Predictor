"""
elo_2026.py

Downloads the starting Elo ratings for 2026 FIFA World Cup team
from eloratings.net
and creates a clean dataset.

Output:
    data/raw/elo_2026.csv
"""

import requests
import pandas as pd
from pathlib import Path

# ==========================================================
# Configuration
# ==========================================================

YEAR = 2026

BASE_URL = "https://eloratings.net/{}_World_Cup_start.tsv"
TEAMS_URL = "https://eloratings.net/en.teams.tsv"

OUTPUT_FILE = Path("data/raw/elo_2026.csv")


# ==========================================================
# Download Team Dictionary
# ==========================================================

def load_team_dictionary():
    """
    Downloads the team code -> team name mapping.
    Ignores any extra alias columns.
    """

    response = requests.get(TEAMS_URL)
    response.raise_for_status()

    rows = []

    for line in response.text.splitlines():

        parts = line.split("\t")

        if len(parts) >= 2:
            rows.append({
                "Team_Code": parts[0],
                "Team": parts[1]
            })

    teams = pd.DataFrame(rows)

    return teams


# ==========================================================
# Download Elo Ratings
# ==========================================================

def download_elo(year):
    """
    Downloads starting Elo ratings for one World Cup.
    """

    url = BASE_URL.format(year)

    print(f"Downloading {year}...")

    df = pd.read_csv(
        url,
        sep="\t",
        header=None
    )

    # Keep only Team Code and Elo Rating
    df = df[[2, 3]]

    df.columns = [
        "Team_Code",
        "Elo_Rating"
    ]

    df.insert(0, "Year", year)

    return df


# ==========================================================
# Build Complete Dataset
# ==========================================================

def build_elo_dataset():

    print("=" * 50)
    print("Building Elo Dataset")
    print("=" * 50)

    # Download team lookup
    teams = load_team_dictionary()

    # Download each World Cup
    dfs = []

    dfs.append(download_elo(YEAR))

    elo = pd.concat(
        dfs,
        ignore_index=True
    )

    # Convert Team Codes to Team Names
    elo = elo.merge(
        teams,
        on="Team_Code",
        how="left"
    )

    # Keep final columns
    elo = elo[
        [
            "Year",
            "Team",
            "Elo_Rating"
        ]
    ]

    # Create folder if missing
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save
    elo.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nDone!")
    print(f"Rows  : {len(elo)}")
    print(f"Saved : {OUTPUT_FILE}")

    return elo


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":
    build_elo_dataset()