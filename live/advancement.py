from __future__ import annotations

from live.models import MatchResult
from live.tournament_config import TournamentConfig


# ==========================================================
# Knockout Elimination
# ==========================================================

def apply_elimination(
    state: dict,
    match: MatchResult,
    config: TournamentConfig,
) -> dict:

    # Group matches eliminate nobody
    if match.round.lower() not in config.format.knockout_rounds:
        return state

    loser = match.loser

    if loser is None:
        return state

    if loser not in state["eliminated_teams"]:

        state["teams"][loser]["eliminated"] = True

        state["eliminated_teams"].append(loser)

    return state


# ==========================================================
# Tournament Phase
# ==========================================================

def update_phase(
    state: dict,
    config: TournamentConfig,
) -> dict:

    completed = len(state["completed_matches"])

    # Group stage

    group_matches = (
        config.format.group_stage.groups
        * config.format.group_stage.matches_per_group
    )

    if completed < group_matches:

        state["current_phase"] = "group"

        return state

    # Number of matches in each knockout round

    knockout_sizes = {

        "r32": 16,
        "r16": 8,
        "qf": 4,
        "sf": 2,
        "third_place": 1,
        "final": 1,

    }

    played = completed - group_matches

    cumulative = 0

    for round_name in config.format.knockout_rounds:

        cumulative += knockout_sizes[round_name]

        if played < cumulative:

            state["current_phase"] = round_name

            return state

    state["current_phase"] = "finished"

    return state


# ==========================================================
# Manual Override
# ==========================================================

def mark_eliminated(
    state: dict,
    team: str,
) -> dict:

    if team not in state["eliminated_teams"]:

        state["teams"][team]["eliminated"] = True

        state["eliminated_teams"].append(team)

    return state