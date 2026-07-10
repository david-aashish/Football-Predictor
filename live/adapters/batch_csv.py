from __future__ import annotations

import argparse

import pandas as pd

from live.adapters.cli import run_live_prediction
from live.models import MatchResult
from live.pipeline import update_pipeline
from live.state import load_state
from live.tournament_config import (
    load_tournament_config,
    resolve_config_paths,
)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--edition",
        required=True,
    )

    parser.add_argument(
        "--file",
        required=True,
    )

    args = parser.parse_args()

    config = resolve_config_paths(
        load_tournament_config(args.edition)
    )

    matches = pd.read_csv(args.file)

    for _, (_, row) in enumerate(
        matches.iterrows(),
        start=1
    ):
        match = MatchResult(
            home_team=row["home_team"],
            away_team=row["away_team"],
            home_goals=int(row["home_goals"]),
            away_goals=int(row["away_goals"]),
            round=row["round"],
            group=None if pd.isna(row.get("group")) else row.get("group"),
        )

        state = load_state(config)

        update_pipeline(
            state=state,
            config=config,
            match=match,
        )

        run_live_prediction(config)

    print()
    print(f"Processed {len(matches)} matches.")

if __name__ == "__main__":
    main()