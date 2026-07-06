"""
build_dataset.py

Merges all engineered features into one dataset.

Input:
    data/raw/elo.csv
    data/raw/host.csv
    data/raw/confederation.csv
    data/raw/previous_wc_finish.csv
    data/raw/qualification_stats.csv
    data/raw/fifa_ranking.csv

Output:
    data/processed/world_cup_dataset.csv
"""

import pandas as pd

from pathlib import Path


# ==========================================================
# Files
# ==========================================================

ELO_FILE = Path("data/raw/elo.csv")

QUALIFICATION_STATS_FILE = Path("data/raw/qualification_stats.csv")

HOST_FILE = Path("data/raw/host.csv")

CONFEDERATION_FILE = Path("data/raw/confederation.csv")

FIFA_RANKING_FILE = Path("data/raw/fifa_ranking.csv")

PREVIOUS_WC_PROGRESS_FILE = Path(
    "data/raw/previous_wc_progress.csv"
)

OUTPUT_FILE = Path(
    "data/processed/world_cup_dataset.csv"
)


# ==========================================================
# Load Dataset
# ==========================================================

def load_dataset(path):

    print(f"Loading {path.name}...")

    return pd.read_csv(path)


# ==========================================================
# Merge Features
# ==========================================================

def build_dataset():

    dataset = load_dataset(ELO_FILE)

    feature_files = [

        QUALIFICATION_STATS_FILE,

        HOST_FILE,

        CONFEDERATION_FILE,

        FIFA_RANKING_FILE,

        PREVIOUS_WC_PROGRESS_FILE,

    ]

    for file in feature_files:

        feature = load_dataset(file)

        dataset = dataset.merge(

            feature,

            on=["Year", "Team"],

            how="left"

        )

    return dataset


# ==========================================================
# Validate
# ==========================================================

def validate_dataset(df):

    print()
    print("=" * 50)
    print("Dataset Validation")
    print("=" * 50)

    print(f"Rows    : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    duplicates = df.duplicated(
        subset=["Year", "Team"]
    ).sum()

    print(f"Duplicates : {duplicates}")

    missing = df.isna().sum()

    if missing.sum() == 0:

        print("Missing Values : None")

    else:

        print("\nMissing Values")

        print(missing[missing > 0])


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
    print("Dataset Saved")
    print("=" * 50)

    print(f"Saved : {OUTPUT_FILE}")


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    dataset = build_dataset()

    validate_dataset(dataset)

    save_dataset(dataset)