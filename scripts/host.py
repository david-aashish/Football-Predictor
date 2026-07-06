"""
host.py

Creates the host nation feature for every World Cup team.

Output:
    data/raw/host.csv
"""

import pandas as pd
from pathlib import Path
from config import HOSTS


# ==========================================================
# Configuration
# ==========================================================

ELO_FILE = Path("data/raw/elo.csv")
OUTPUT_FILE = Path("data/raw/host.csv")

# ==========================================================
# Load Elo Dataset
# ==========================================================

def load_elo():

    print("Loading Elo Dataset...")

    elo = pd.read_csv(ELO_FILE)

    return elo


# ==========================================================
# Create Host Feature
# ==========================================================

def create_host_feature(elo):

    elo["Host"] = 0

    for year, hosts in HOSTS.items():

        mask = (
            (elo["Year"] == year) &
            (elo["Team"].isin(hosts))
        )

        elo.loc[mask, "Host"] = 1

    host_df = elo[
        [
            "Year",
            "Team",
            "Host"
        ]
    ]

    return host_df


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
    print("Host Dataset Saved!")
    print("=" * 50)

    print(f"Rows : {len(df)}")
    print(f"Saved: {OUTPUT_FILE}")


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    elo = load_elo()

    host_df = create_host_feature(elo)

    save_dataset(host_df)