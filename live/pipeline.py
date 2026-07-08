from __future__ import annotations

from live.build_features import build_and_save
from live.elo import update_elo
from live.form import (
    update_form,
    update_tournament_stats,
)
from live.advancement import (
    apply_elimination,
    update_phase,
)
from live.state import (
    match_already_recorded,
    validate_teams_in_state,
    save_state,
)
from live.tournament_config import TournamentConfig
from live.models import MatchResult


def update_pipeline(
    state: dict,
    match: MatchResult,
    config: TournamentConfig,
) -> dict:

    # ----------------------------------
    # Validate teams
    # ----------------------------------

    validate_teams_in_state(
        state,
        match.home_team,
        match.away_team,
    )

    # ----------------------------------
    # Ignore duplicate matches
    # ----------------------------------

    if match_already_recorded(state, match.to_dict()):
        raise ValueError("Match already processed.")

    # ----------------------------------
    # Dynamic Elo
    # ----------------------------------

    state = update_elo(
        state,
        match,
        config,
    )

    # ----------------------------------
    # Tournament statistics
    # ----------------------------------

    state = update_tournament_stats(
        state,
        match,
    )

    # ----------------------------------
    # Recent form
    # ----------------------------------

    state = update_form(
        state,
        match,
        config.form_window,
    )

    # ----------------------------------
    # Save match history
    # ----------------------------------

    state["completed_matches"].append(
        match.to_dict()
    )

    # ----------------------------------
    # Elimination rules
    # ----------------------------------

    state = apply_elimination(
        state,
        match,
        config,
    )

    # ----------------------------------
    # Tournament phase
    # ----------------------------------

    state = update_phase(
        state,
        config,
    )

    # ----------------------------------
    # Persist updated tournament state
    # ----------------------------------

    save_state(
        state,
        config,
    )

    # ----------------------------------
    # Regenerate updated feature dataset
    # ----------------------------------

    build_and_save(
        config,
    )

    return state