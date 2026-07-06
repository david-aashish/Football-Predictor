"""
previous_wc_finish.py

Builds previous World Cup progress feature.

Input:
    data/raw/elo.csv
    data/raw/qualified_teams.csv

Output:
    data/raw/previous_wc_finish.csv
"""

import pandas as pd
from pathlib import Path

from config import (
    PREVIOUS_WORLD_CUP,
    WORLD_CUP_WINNERS
)

# ==========================================================
# Files
# ==========================================================

ELO_FILE = Path("data/raw/elo.csv")
QUALIFIED_FILE = Path("data/raw/qualified_teams.csv")
OUTPUT_FILE = Path("data/raw/previous_wc_progress.csv")

DID_NOT_QUALIFY = -1

# ==========================================================
# Reamining Teams Mapping
# ==========================================================

REMAINING_MAPPING = {

    "group stage": None,

    "second group stage": None,
    "final round": None,

    "round of 64": 64,
    "round of 32": 32,
    "round of 16": 16,

    "quarter-final": 8,
    "quarter-finals": 8,

    "semi-final": 4,
    "semi-finals": 4,

    "third-place match": 4,

    "final": 2
}

# ==========================================================
# Load Elo
# ==========================================================

def load_elo():

    print("Loading Elo Dataset...")

    return pd.read_csv(ELO_FILE)


# ==========================================================
# Load World Cup Results
# ==========================================================

def load_world_cup_results():

    print("Loading World Cup Results...")

    return pd.read_csv(QUALIFIED_FILE)


# ==========================================================
# Initial Encoding
# ==========================================================

def encode_finish(wc):

    wc["Remaining_Teams"] = wc["performance"].map(REMAINING_MAPPING)

    return wc


# ==========================================================
# Fill Historical Formats
# ==========================================================

def adjust_stages(wc):

    years = (
        wc["tournament_name"]
        .str.extract(r"(\d{4})")
        .astype(int)[0]
        .unique()
    )

    for year in years:

        tournament_mask = (
            wc["tournament_name"]
            .str.contains(str(year))
        )

        tournament = wc[tournament_mask]

        total_teams = len(tournament)

        # -----------------------------
        # Group Stage
        # -----------------------------

        mask = (
            tournament_mask &
            (wc["performance"] == "group stage")
        )

        group = tournament[
        tournament["performance"] == "group stage"
        ]

        wc.loc[
            group.index,
            "Remaining_Teams"
        ] = total_teams

        # -----------------------------
        # Historical Formats
        # -----------------------------

        for stage in ["second group stage", "final round"]:

            stage_mask = (
                tournament_mask &
                (wc["performance"] == stage)
            )

            if stage_mask.any():

                remaining = stage_mask.sum()

                wc.loc[
                    stage_mask,
                    "Remaining_Teams"
                ] = remaining

        # -----------------------------
        # Champion / Runner-up
        # -----------------------------

        finalists = wc[
            tournament_mask &
            (wc["performance"] == "final")
        ]

        if len(finalists) == 2:

            winner = WORLD_CUP_WINNERS.get(year)

            if winner is not None:

                for idx, row in finalists.iterrows():

                    if row["team_name"] == winner:
                        wc.loc[idx, "Remaining_Teams"] = 1

                    else:
                        wc.loc[idx, "Remaining_Teams"] = 2

    return wc


# ==========================================================
# Convert Remaining Teams -> Progress
# ==========================================================

def calculate_progress(wc):

    progress = []

    for _, row in wc.iterrows():

        remaining = row["Remaining_Teams"]

        year = int(
            row["tournament_name"].split()[0]
        )

        tournament_sizes = (
            wc.groupby("tournament_name")
            .size()
            .to_dict()
        )

        tournament = row["tournament_name"]

        total_teams = tournament_sizes[tournament]

        value = 1 - (
            (remaining - 1)
            /
            (total_teams - 1)
        )

        progress.append(round(value, 4))

    wc["Progress"] = progress

    return wc


# ==========================================================
# Build Dataset
# ==========================================================

def build_dataset(elo, wc):

    rows = []

    for year in sorted(elo["Year"].unique()):

        previous = PREVIOUS_WORLD_CUP[year]

        previous_wc = wc[
            wc["tournament_name"]
            .str.contains(str(previous))
        ]

        lookup = dict(
            zip(
                previous_wc["team_name"],
                previous_wc["Progress"]
            )
        )

        qualified = elo[
            elo["Year"] == year
        ]["Team"]

        for team in qualified:

            rows.append({

                "Year": year,
                "Team": team,
                "Previous_WC_Progress":
                    lookup.get(team, DID_NOT_QUALIFY)

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
    print("Previous WC Dataset Saved!")
    print("=" * 50)
    print(f"Rows : {len(df)}")
    print(f"Saved: {OUTPUT_FILE}")


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    elo = load_elo()

    wc = load_world_cup_results()

    wc = encode_finish(wc)

    wc = adjust_stages(wc)

    # Final safety check
    unknown = wc[wc["Remaining_Teams"].isna()]

    if len(unknown):

        print("\nUnknown Stage Labels:")
        print(sorted(unknown["performance"].unique()))

    else:

        print("All stage labels successfully mapped.")

    wc = calculate_progress(wc)

    df = build_dataset(
        elo,
        wc
    )

    save_dataset(df)