"""
fifa_ranking.py

Downloads FIFA rankings before every World Cup.

Output:
    data/raw/fifa_ranking.csv
"""

import requests
import pandas as pd

from pathlib import Path

from config import FIFA_RANKING_IDS, FIFA_TEAM_MAPPING

ELO_FILE = Path("data/raw/elo.csv")

OUTPUT_FILE = Path("data/raw/fifa_ranking.csv")

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

        fifa_name = FIFA_TEAM_MAPPING.get(team, team)

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

    print(f"Rows : {len(df)}")

    print(f"Saved: {OUTPUT_FILE}")

if __name__ == "__main__":

    elo = load_elo()

    all_dfs = []

    for year, schedule_id in FIFA_RANKING_IDS.items():

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