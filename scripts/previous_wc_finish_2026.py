"""
previous_wc_progress_2026.py

Creates Previous_WC_Progress feature
for the 2026 prediction dataset.

Input:
    data/raw/qualified_teams.csv
    data/raw/elo_2026.csv

Output:
    data/raw/previous_wc_progress_2026.csv
"""

import pandas as pd
from pathlib import Path

# ==========================================================
# Files
# ==========================================================

SOURCE_FILE = Path("data/raw/previous_wc_progress_source.csv")
ELO_FILE = Path("data/raw/elo_2026.csv")

OUTPUT_FILE = Path(
    "data/raw/previous_wc_progress_2026.csv"
)

PREVIOUS_WORLD_CUP = 2022

WORLD_CUP_WINNER = "Argentina"

DID_NOT_QUALIFY = -1

# ==========================================================
# Remaining Teams Mapping
# ==========================================================

REMAINING_MAPPING = {

    "group stage": None,

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
# Load
# ==========================================================

def load_elo():

    print("Loading 2026 Teams...")

    return pd.read_csv(ELO_FILE)


def load_world_cup_results():

    print("Loading World Cup Results...")

    return pd.read_csv(SOURCE_FILE)


# ==========================================================
# Keep Only 2022 World Cup
# ==========================================================

def keep_previous_world_cup(wc):

    return wc[
        wc["tournament_name"]
        .str.contains(str(PREVIOUS_WORLD_CUP))
    ].copy()


# ==========================================================
# Initial Encoding
# ==========================================================

def encode_finish(wc):

    wc["Remaining_Teams"] = wc["performance"].map(
        REMAINING_MAPPING
    )

    return wc


# ==========================================================
# Adjust Stages
# ==========================================================

def adjust_stages(wc):

    total_teams = len(wc)

    # -----------------------------
    # Group Stage
    # -----------------------------

    group = wc[
        wc["performance"] == "group stage"
    ]

    wc.loc[
        group.index,
        "Remaining_Teams"
    ] = total_teams

    # -----------------------------
    # Champion / Runner-up
    # -----------------------------

    finalists = wc[
        wc["performance"] == "final"
    ]

    if len(finalists) == 2:

        for idx, row in finalists.iterrows():

            if row["team_name"] == WORLD_CUP_WINNER:

                wc.loc[idx, "Remaining_Teams"] = 1

            else:

                wc.loc[idx, "Remaining_Teams"] = 2

    return wc


# ==========================================================
# Progress Score
# ==========================================================

def calculate_progress(wc):

    total_teams = len(wc)

    wc["Previous_WC_Progress"] = (

        1

        -

        (

            (wc["Remaining_Teams"] - 1)

            /

            (total_teams - 1)

        )

    ).round(4)

    return wc


# ==========================================================
# Build Dataset
# ==========================================================

def build_dataset(elo, wc):

    lookup = dict(

        zip(

            wc["team_name"],

            wc["Previous_WC_Progress"]

        )

    )

    rows = []

    for team in elo["Team"]:

        rows.append({

            "Year": 2026,

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
    print("Previous WC Progress Saved!")
    print("=" * 50)
    print(df)
    print()
    print(f"Saved -> {OUTPUT_FILE}")


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    elo = load_elo()

    wc = load_world_cup_results()

    wc = keep_previous_world_cup(wc)

    wc = encode_finish(wc)

    wc = adjust_stages(wc)

    unknown = wc[
        wc["Remaining_Teams"].isna()
    ]

    if len(unknown):

        print("\nUnknown Stage Labels:")
        print(sorted(unknown["performance"].unique()))

    else:

        print("All stage labels successfully mapped.")

    wc = calculate_progress(wc)

    dataset = build_dataset(
        elo,
        wc
    )

    save_dataset(dataset)