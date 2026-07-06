"""
target.py

Adds target variable (World Cup Winner).

Input:
    data/processed/world_cup_dataset.csv

Output:
    data/processed/world_cup_dataset.csv
"""

import pandas as pd

from pathlib import Path

from config import WORLD_CUP_WINNERS


# ==========================================================
# Files
# ==========================================================

DATASET_FILE = Path("data/processed/world_cup_dataset.csv")


# ==========================================================
# Load Dataset
# ==========================================================

def load_dataset():

    print("Loading Dataset...")

    return pd.read_csv(DATASET_FILE)


# ==========================================================
# Add Target
# ==========================================================

def add_target(df):

    df["Winner"] = 0

    for year, winner in WORLD_CUP_WINNERS.items():

        mask = (
            (df["Year"] == year) &
            (df["Team"] == winner)
        )

        df.loc[mask, "Winner"] = 1

    return df


# ==========================================================
# Validate
# ==========================================================

def validate(df):

    print()
    print("=" * 50)
    print("Target Validation")
    print("=" * 50)

    winners = df.groupby("Year")["Winner"].sum()

    print(winners)

    assert (winners == 1).all(), \
        "Each tournament must have exactly one winner."

    print("\nValidation Passed!")


# ==========================================================
# Save
# ==========================================================

def save_dataset(df):

    df.to_csv(
        DATASET_FILE,
        index=False
    )

    print()
    print("=" * 50)
    print("Dataset Saved")
    print("=" * 50)

    print(f"Saved: {DATASET_FILE}")


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    dataset = load_dataset()

    dataset = add_target(dataset)

    validate(dataset)

    save_dataset(dataset)