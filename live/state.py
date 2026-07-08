from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pandas as pd

from live.tournament_config import TournamentConfig


def empty_tournament_stats() -> dict[str, int | float]:
    return {
        "matches": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_difference": 0,
        "points": 0,
    }


def empty_team_state(elo: float) -> dict[str, Any]:
    return {
        "elo": elo,
        "baseline_elo": elo,
        "eliminated": False,
        "group": None,
        "tournament_stats": empty_tournament_stats(),
        "form_last_n": [],
    }


def load_state(config: TournamentConfig) -> dict[str, Any]:
    state_path = config.state_file
    if not state_path.exists():
        raise FileNotFoundError(
            f"Tournament state not found: {state_path}. "
            f"Run initialize first for edition {config.edition}."
        )

    with state_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def save_state(state: dict[str, Any], config: TournamentConfig) -> Path:
    config.state_dir.mkdir(parents=True, exist_ok=True)
    state_path = config.state_file

    with state_path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, ensure_ascii=False)

    return state_path


def match_already_recorded(state: dict[str, Any], match: dict[str, Any]) -> bool:
    if match.get("match_id"):
        for recorded in state["completed_matches"]:
            if recorded.get("match_id") == match["match_id"]:
                return True

    key = (
        match["home_team"],
        match["away_team"],
        match["home_goals"],
        match["away_goals"],
        match.get("round"),
        match.get("group"),
    )

    for recorded in state["completed_matches"]:
        recorded_key = (
            recorded["home_team"],
            recorded["away_team"],
            recorded["home_goals"],
            recorded["away_goals"],
            recorded.get("round"),
            recorded.get("group"),
        )
        if recorded_key == key:
            return True

    return False


def validate_teams_in_state(state: dict[str, Any], home: str, away: str) -> None:
    teams = state["teams"]
    missing = [team for team in (home, away) if team not in teams]
    if missing:
        raise ValueError(f"Unknown team(s) for this edition: {', '.join(missing)}")


def create_initial_state(config: TournamentConfig) -> dict[str, Any]:
    baseline = pd.read_csv(config.baseline_dataset)
    teams: dict[str, Any] = {}

    for _, row in baseline.iterrows():
        team = row["Team"]
        elo = float(row["Elo_Rating"])
        teams[team] = empty_team_state(elo)

    return {
        "edition": config.edition,
        "year": config.year,
        "current_phase": "pre_tournament",
        "teams": teams,
        "completed_matches": [],
        "eliminated_teams": [],
        "group_standings": {},
    }


def clone_state(state: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(state)
