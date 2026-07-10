from __future__ import annotations

import argparse

from live.initialize import initialize
from live.state import load_state
from live.tournament_config import (
    load_tournament_config,
    resolve_config_paths,
)
from live.models import MatchResult
from live.pipeline import update_pipeline
from live.prediction import apply_live_probability_rules
from live.snapshot import save_prediction_snapshot, reset_snapshots
from live.timeline import build_probability_timeline
from models.predictor import predict_dataset


# ==========================================================
# Initialize Tournament
# ==========================================================

def command_init(edition: str):
    initialize(edition)

    config = resolve_config_paths(
        load_tournament_config(edition)
    )

    reset_snapshots(edition)

    run_live_prediction(config)

# ==========================================================
# Status
# ==========================================================

def command_status(config):

    state = load_state(config)

    print("=" * 60)
    print(f"Edition : {state['edition']}")
    print(f"Phase   : {state['current_phase']}")
    print(f"Matches : {len(state['completed_matches'])}")
    print(f"Eliminated Teams : {len(state['eliminated_teams'])}")
    print("=" * 60)

# ==========================================================
# Live prediction
# ==========================================================

def run_live_prediction(config):
    predictions = predict_dataset(
        config.output_features,
        model_name="xgboost"
    )

    predictions = apply_live_probability_rules(
        predictions,
        config.state_file
    )

    state = load_state(config)

    snapshot_path = save_prediction_snapshot(
        predictions,
        edition=config.edition,
        tournament_state=state
    )

    build_probability_timeline(
        edition=config.edition
    )

    return predictions, snapshot_path

# ==========================================================
# Add Result
# ==========================================================

def command_result(config, args):

    match = MatchResult(

        home_team=args.home,

        away_team=args.away,

        home_goals=args.home_goals,

        away_goals=args.away_goals,

        round=args.round,

        group=args.group,

    )

    state = load_state(config)

    update_pipeline(
        state=state,
        config=config,
        match=match,
    )

    predictions, snapshot_path = run_live_prediction(config)

    print("=" * 60)
    print("Match processed successfully.")
    print(f"Snapshot saved: {snapshot_path}")
    print("=" * 60)
    print()
    print("Top 10 Live Champion Probabilities")
    print(predictions.head(10).to_string(index=False))


# ==========================================================
# CLI
# ==========================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--edition",
        required=True,
    )

    parser.add_argument(
        "--init",
        action="store_true",
    )

    parser.add_argument(
        "--status",
        action="store_true",
    )

    parser.add_argument(
        "--result",
        action="store_true",
    )

    parser.add_argument("--home")
    parser.add_argument("--away")

    parser.add_argument(
        "--home-goals",
        type=int,
    )

    parser.add_argument(
        "--away-goals",
        type=int,
    )

    parser.add_argument(
        "--round",
        default="group",
    )

    parser.add_argument(
        "--group",
        default=None,
    )

    args = parser.parse_args()

    config = resolve_config_paths(
        load_tournament_config(args.edition)
    )

    if args.init:

        command_init(args.edition)

    elif args.status:

        command_status(config)

    elif args.result:

        command_result(config, args)

    else:

        parser.print_help()


if __name__ == "__main__":

    main()