from __future__ import annotations

import math

from live.models import MatchResult
from live.tournament_config import EloConfig, TournamentConfig


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + math.pow(10.0, (rating_b - rating_a) / 400.0))


def effective_rating(
    team: str,
    base_rating: float,
    hosts: list[str],
    host_advantage_elo: float,
) -> float:
    if team in hosts:
        return base_rating + host_advantage_elo
    return base_rating


def score_outcome(home_goals: int, away_goals: int, for_home: bool) -> float:
    if home_goals == away_goals:
        return 0.5
    if for_home:
        return 1.0 if home_goals > away_goals else 0.0
    return 1.0 if away_goals > home_goals else 0.0


def update_elo(
    state: dict,
    match: MatchResult,
    config: TournamentConfig,
) -> dict:
    elo_config: EloConfig = config.elo
    teams = state["teams"]

    home = match.home_team
    away = match.away_team

    home_rating = teams[home]["elo"]
    away_rating = teams[away]["elo"]

    home_effective = effective_rating(
        home,
        home_rating,
        config.hosts,
        elo_config.host_advantage,
    )
    away_effective = effective_rating(
        away,
        away_rating,
        config.hosts,
        elo_config.host_advantage,
    )

    expected_home = expected_score(home_effective, away_effective)
    expected_away = 1.0 - expected_home

    actual_home = score_outcome(match.home_goals, match.away_goals, for_home=True)
    actual_away = 1.0 - actual_home

    teams[home]["elo"] = round(
        home_rating + elo_config.k_factor * (actual_home - expected_home),
        1,
    )
    teams[away]["elo"] = round(
        away_rating + elo_config.k_factor * (actual_away - expected_away),
        1,
    )

    return state
