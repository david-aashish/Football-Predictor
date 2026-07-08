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


# ==========================================================
# Initialize Tournament
# ==========================================================

def command_init(edition: str):
    initialize(edition)

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

    print("=" * 60)
    print("Match processed successfully.")
    print("=" * 60)


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