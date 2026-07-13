"""
snapshot.py

Snapshot system.

Saves prediction outputs after every tournament update.
"""

from pathlib import Path


SNAPSHOT_DIR = Path("predictions/snapshots")
VISUALIZATION_DIR = Path("predictions/visualizations")


def get_next_snapshot_number(edition):
    edition_dir = SNAPSHOT_DIR / edition
    edition_dir.mkdir(parents=True, exist_ok=True)

    existing_snapshots = list(
        edition_dir.glob("snapshot_*.csv")
    )

    return len(existing_snapshots) + 1


def save_prediction_snapshot(
    predictions,
    edition,
    tournament_state
):
    
    completed_matches = len(tournament_state["completed_matches"])

    if completed_matches == 0:
        label = "pre_tournament"
    else:
        label = f"match_{completed_matches:03d}"

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    snapshot_number = get_next_snapshot_number(edition)

    output_file = SNAPSHOT_DIR / edition / (
        f"snapshot_{snapshot_number:03d}_{label}.csv"
    )

    predictions.to_csv(output_file, index=False)

    return output_file

def reset_snapshots(edition):
    edition_dir = SNAPSHOT_DIR / edition

    if edition_dir.exists():
        for snapshot_file in edition_dir.glob("snapshot_*.csv"):
            snapshot_file.unlink()

    timeline_dir = Path("predictions/timelines")
    timeline_file = timeline_dir / f"{edition}_probability_timeline.csv"

    if timeline_file.exists():
        timeline_file.unlink()

    visualization_dir = VISUALIZATION_DIR / edition

    if visualization_dir.exists():
        for visualization_file in visualization_dir.iterdir():
            if visualization_file.is_file():
                visualization_file.unlink()