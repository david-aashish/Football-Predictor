"""
initialize.py

Creates the initial tournament state for a
World Cup edition.

Example
-------
python -m live.initialize --edition wc2026
"""

from __future__ import annotations

import argparse
import json

from live.state import (
    create_initial_state,
    save_state,
)

from live.tournament_config import (
    load_tournament_config,
    resolve_config_paths,
)


# ==========================================================
# Initialize Tournament
# ==========================================================

def initialize(edition: str) -> None:

    # -----------------------------
    # Load tournament configuration
    # -----------------------------

    config = load_tournament_config(edition)
    config = resolve_config_paths(config)

    # -----------------------------
    # Create initial state
    # -----------------------------

    state = create_initial_state(config)

    save_state(
        state,
        config
    )

    # -----------------------------
    # Create empty pending queue
    # -----------------------------

    config.state_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    with config.pending_matches_file.open(
        "w",
        encoding="utf-8"
    ) as handle:

        json.dump(
            [],
            handle,
            indent=2
        )

    # -----------------------------
    # Summary
    # -----------------------------

    print()

    print("=" * 60)
    print(f"Tournament Initialized ({edition})")
    print("=" * 60)

    print(f"Edition : {config.edition}")
    print(f"Year    : {config.year}")
    print(f"Teams   : {len(state['teams'])}")

    print()

    print(f"State File")
    print(f"  {config.state_file}")

    print()

    print(f"Pending Queue")
    print(f"  {config.pending_matches_file}")

    print()

    print("=" * 60)
    print("Initialization Complete.")
    print("=" * 60)


# ==========================================================
# CLI
# ==========================================================

def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(

        "--edition",

        required=True,

        help="Tournament edition (e.g. wc2026)"

    )

    return parser.parse_args()


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    args = parse_args()

    initialize(args.edition)