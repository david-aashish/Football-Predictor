"""
timeline.py

Builds a clean probability timeline from prediction snapshots.

Output:
    predictions/timelines/{edition}_probability_timeline.csv
"""

import argparse

from pathlib import Path
import pandas as pd


SNAPSHOT_DIR = Path("predictions/snapshots")
TIMELINE_DIR = Path("predictions/timelines")


def extract_snapshot_number(snapshot_path):
    parts = snapshot_path.stem.split("_")

    for part in parts:
        if part.isdigit():
            return int(part)

    return None


def get_probability_column(df):
    if "Live_Probability" in df.columns:
        return "Live_Probability"

    if "Probability" in df.columns:
        return "Probability"

    raise ValueError("No probability column found in snapshot.")


def build_probability_timeline(edition):
    edition_dir = SNAPSHOT_DIR / edition
    snapshot_files = sorted(
        edition_dir.glob("snapshot_*.csv"),
        key=extract_snapshot_number
    )

    timeline_rows = []

    for snapshot_file in snapshot_files:
        snapshot_number = extract_snapshot_number(snapshot_file)

        df = pd.read_csv(snapshot_file)

        probability_column = get_probability_column(df)

        for _, row in df.iterrows():
            timeline_rows.append({
                "Team": row["Team"],
                f"Snapshot_{snapshot_number:03d}": row[probability_column]
            })

    timeline_df = pd.DataFrame(timeline_rows)

    timeline_df = timeline_df.groupby("Team", as_index=False).first()

    output_file = TIMELINE_DIR / f"{edition}_probability_timeline.csv"

    output_file.parent.mkdir(parents=True, exist_ok=True)

    timeline_df.to_csv(output_file, index=False)

    return timeline_df


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--edition",
        default="wc2026",
        help="Tournament edition, example: wc2026"
    )

    args = parser.parse_args()

    build_probability_timeline(args.edition)

    output_file = TIMELINE_DIR / f"{args.edition}_probability_timeline.csv"

    print("=" * 80)
    print("PROBABILITY TIMELINE CREATED")
    print("=" * 80)

    print()
    print(f"Saved to: {output_file}")

if __name__ == "__main__":
    main()