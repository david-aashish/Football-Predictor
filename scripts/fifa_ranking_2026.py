"""
fifa_ranking_2026.py

Downloads FIFA rankings before 2026 World Cup.

Output:
    data/raw/fifa_ranking_2026.csv
"""

import requests
import pandas as pd

from pathlib import Path

from config import FIFA_TEAM_MAPPING_2026

FIFA_RANKING_ID_2026 = {
    2026 : "FRS_Male_Football_20260401"
}

ELO_FILE = Path("data/raw/elo_2026.csv")

OUTPUT_FILE = Path("data/raw/fifa_ranking_2026.csv")

BASE_URL = (
    "https://api.fifa.com/api/v3/fifarankings/"
    "rankings/rankingsbyschedule"
)

def load_elo():

    print("=" * 50)
    print("Loading Elo Dataset")
    print("=" * 50)

    elo = pd.read_csv(ELO_FILE)

    print(elo.head())
    print()
    print(elo.shape)

    return elo

def download_ranking(schedule_id):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Referer": "https://inside.fifa.com/",
    }

    params = {
        "rankingScheduleId": schedule_id,
        "language": "en"
    }

    response = requests.get(
        BASE_URL,
        params=params,
        headers=headers,
        timeout=30
    )

    print(response.status_code)

    response.raise_for_status()

    return response.json()["Results"]

def build_rank_dictionary(results):

    rankings = {}

    for team in results:

        name = team["TeamName"][0]["Description"]

        rank = team["Rank"]

        rankings[name] = rank

    return rankings

def build_dataframe(rankings, elo, year):

    qualified = (
        elo[elo["Year"] == year]
        ["Team"]
        .tolist()
    )

    rows = []

    for team in qualified:

        fifa_name = FIFA_TEAM_MAPPING_2026.get(team, team)

        rows.append({

            "Year": year,
            "Team": team,
            "FIFA_Rank": rankings.get(fifa_name)

        })

    return pd.DataFrame(rows)

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
    print("FIFA Ranking Dataset Saved!")
    print("=" * 50)

    print(df.head())

    print()
    print("=" * 50)
    print("Teams with Missing/Unmatched FIFA Ranks:")
    print("=" * 50)
    
    # Filter rows where FIFA_Rank is null or blank
    missing_teams = df[df["FIFA_Rank"].isna()]
    
    if not missing_teams.empty:
        # Loop and print each unique team name from your Elo file that failed to match
        for team in missing_teams["Team"].unique():
            print(f"❌ Missing Rank for: {team}")
    else:
        print("✅ All teams successfully matched! No missing ranks.")

    print()

    print(f"Rows : {len(df)}")

    print(f"Saved: {OUTPUT_FILE}")

if __name__ == "__main__":

    elo = load_elo()

    all_dfs = []

    for year, schedule_id in FIFA_RANKING_ID_2026.items():

        print("=" * 50)
        print(year)
        print("=" * 50)

        results = download_ranking(schedule_id)

        rankings = build_rank_dictionary(results)

        df = build_dataframe(
            rankings,
            elo,
            year
        )

        all_dfs.append(df)

    final_df = pd.concat(
        all_dfs,
        ignore_index=True
    )

    missing = final_df[
        final_df["FIFA_Rank"].isna()
    ]

    if not missing.empty:

        print()
        print("=" * 50)
        print("Missing Teams")
        print("=" * 50)

        print(missing[["Year", "Team"]])

    save_dataset(final_df)