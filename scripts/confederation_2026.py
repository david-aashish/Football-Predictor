"""
confederation_2026.py

Creates the confederation feature for 2026 World Cup team.

Output:
    data/raw/confederation_2026.csv
"""

import pandas as pd
from pathlib import Path
from config import CONFEDERATIONS

# ==========================================================
# Configuration
# ==========================================================

ELO_FILE = Path("data/raw/elo_2026.csv")
OUTPUT_FILE = Path("data/raw/confederation_2026.csv")

# ==========================================================
# Load Elo Dataset
# ==========================================================

def load_elo():

    print("Loading Elo Dataset...")

    elo = pd.read_csv(ELO_FILE)

    return elo


# ==========================================================
# Create Confederation Feature
# ==========================================================

def create_confederation_feature(elo):

    elo["Confederation"] = elo["Team"].map(CONFEDERATIONS)

    missing = elo[elo["Confederation"].isna()]

    if len(missing) > 0:

        print("\nMissing Confederations:")
        print(sorted(missing["Team"].unique()))

    conf_df = elo[
        [
            "Year",
            "Team",
            "Confederation"
        ]
    ]

    return conf_df


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
    print("Confederation Dataset Saved!")
    print("=" * 50)

    print(f"Rows : {len(df)}")
    print(f"Saved: {OUTPUT_FILE}")


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    elo = load_elo()

    conf_df = create_confederation_feature(elo)

    save_dataset(conf_df)