from __future__ import annotations

from live.models import MatchResult


def _result_for_team(match: MatchResult, team: str) -> str:
    if match.is_draw:
        return "draw"

    if match.winner == team:
        return "win"
    return "loss"


def _goals_for_team(match: MatchResult, team: str) -> tuple[int, int]:
    if team == match.home_team:
        return match.home_goals, match.away_goals
    if team == match.away_team:
        return match.away_goals, match.home_goals
    raise ValueError(f"Team {team} did not play in this match")


def update_tournament_stats(state: dict, match: MatchResult) -> dict:
    teams = state["teams"]

    for team in (match.home_team, match.away_team):
        stats = teams[team]["tournament_stats"]
        goals_for, goals_against = _goals_for_team(match, team)
        result = _result_for_team(match, team)

        stats["matches"] += 1
        stats["goals_for"] += goals_for
        stats["goals_against"] += goals_against
        stats["goal_difference"] = stats["goals_for"] - stats["goals_against"]

        if result == "win":
            stats["wins"] += 1
            stats["points"] += 3
        elif result == "draw":
            stats["draws"] += 1
            stats["points"] += 1
        else:
            stats["losses"] += 1

    return state


def update_form(state: dict, match: MatchResult, form_window: int) -> dict:
    teams = state["teams"]

    for team in (match.home_team, match.away_team):
        goals_for, goals_against = _goals_for_team(match, team)
        entry = {
            "home_team": match.home_team,
            "away_team": match.away_team,
            "home_goals": match.home_goals,
            "away_goals": match.away_goals,
            "round": match.round,
            "group": match.group,
            "result": _result_for_team(match, team),
            "goals_for": goals_for,
            "goals_against": goals_against,
        }

        form = teams[team]["form_last_n"]
        form.append(entry)
        teams[team]["form_last_n"] = form[-form_window:]

    return state


def form_summary(form_entries: list[dict]) -> dict[str, float | int]:
    if not form_entries:
        return {
            "matches": 0,
            "win_rate": 0.0,
            "goals_for_per_game": 0.0,
            "goals_against_per_game": 0.0,
        }

    matches = len(form_entries)
    wins = sum(1 for entry in form_entries if entry["result"] == "win")
    goals_for = sum(entry["goals_for"] for entry in form_entries)
    goals_against = sum(entry["goals_against"] for entry in form_entries)

    return {
        "matches": matches,
        "win_rate": wins / matches,
        "goals_for_per_game": goals_for / matches,
        "goals_against_per_game": goals_against / matches,
    }
