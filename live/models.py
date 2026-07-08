from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class MatchResult:
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    round: str = "group"
    group: str | None = None
    match_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MatchResult:
        return cls(
            home_team=data["home_team"],
            away_team=data["away_team"],
            home_goals=int(data["home_goals"]),
            away_goals=int(data["away_goals"]),
            round=data.get("round", "group"),
            group=data.get("group"),
            match_id=data.get("match_id"),
        )

    @property
    def is_draw(self) -> bool:
        return self.home_goals == self.away_goals

    @property
    def winner(self) -> str | None:
        if self.is_draw:
            return None
        if self.home_goals > self.away_goals:
            return self.home_team
        return self.away_team

    @property
    def loser(self) -> str | None:
        if self.is_draw:
            return None
        if self.home_goals > self.away_goals:
            return self.away_team
        return self.home_team


RESULT_PATTERN = re.compile(
    r"^\s*(?P<home>.+?)\s+(?P<home_goals>\d+)\s*[-–]\s*(?P<away_goals>\d+)\s+(?P<away>.+?)\s*$"
)


def parse_result_string(
    result: str,
    round_name: str = "group",
    group: str | None = None,
    team_aliases: dict[str, str] | None = None,
) -> MatchResult:
    match = RESULT_PATTERN.match(result.strip())
    if not match:
        raise ValueError(
            f"Could not parse result: {result!r}. "
            "Expected format: 'HomeTeam 2-1 AwayTeam'"
        )

    aliases = team_aliases or {}
    home = aliases.get(match.group("home").strip(), match.group("home").strip())
    away = aliases.get(match.group("away").strip(), match.group("away").strip())

    return MatchResult(
        home_team=home,
        away_team=away,
        home_goals=int(match.group("home_goals")),
        away_goals=int(match.group("away_goals")),
        round=round_name,
        group=group,
    )
