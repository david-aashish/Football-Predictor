from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from live.config import PROJECT_ROOT, TOURNAMENTS_DIR


@dataclass
class EloConfig:
    k_factor: float = 40.0
    host_advantage: float = 100.0



@dataclass
class GroupStageConfig:
    groups: int
    teams_per_group: int
    matches_per_group: int
    advancement: list[dict[str, Any]]


@dataclass
class FormatConfig:
    group_stage: GroupStageConfig
    knockout_rounds: list[str]


@dataclass
class TournamentConfig:
    edition: str
    year: int
    teams: int
    format: FormatConfig
    hosts: list[str]
    elo: EloConfig
    form_window: int
    baseline_dataset: Path
    teams_source: Path
    output_features: Path
    state_dir: Path
    team_name_aliases: dict[str, str] = field(default_factory=dict)

    @property
    def state_file(self) -> Path:
        return self.state_dir / "tournament_state.json"

    @property
    def pending_matches_file(self) -> Path:
        return self.state_dir / "matches_pending.json"

    def resolve_path(self, path: Path) -> Path:
        if path.is_absolute():
            return path
        return PROJECT_ROOT / path

    def normalize_team(self, name: str) -> str:
        return self.team_name_aliases.get(name.strip(), name.strip())


def _parse_format(raw: dict[str, Any]) -> FormatConfig:
    group_raw = raw["group_stage"]
    group_stage = GroupStageConfig(
        groups=group_raw["groups"],
        teams_per_group=group_raw["teams_per_group"],
        matches_per_group=group_raw.get(
            "matches_per_group",
            group_raw["teams_per_group"] * (group_raw["teams_per_group"] - 1),
        ),
        advancement=group_raw.get("advancement", []),
    )
    return FormatConfig(
        group_stage=group_stage,
        knockout_rounds=list(raw.get("knockout_rounds", [])),
    )


def load_tournament_config(edition: str) -> TournamentConfig:
    config_path = TOURNAMENTS_DIR / f"{edition}.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Tournament config not found: {config_path}")

    with config_path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    baseline = Path(raw["baseline_dataset"])
    teams_source = Path(raw["teams_source"])
    output_features = Path(raw["output_features"])
    state_dir = Path(raw["state_dir"])

    return TournamentConfig(
        edition=raw["edition"],
        year=int(raw["year"]),
        teams=int(raw["teams"]),
        format=_parse_format(raw["format"]),
        hosts=list(raw.get("hosts", [])),
        elo=EloConfig(
            k_factor=float(raw.get("elo", {}).get("k_factor", 40)),
            host_advantage=float(raw.get("host_advantage", 0))
            ),
        form_window=int(raw.get("form_window", 5)),
        baseline_dataset=baseline,
        teams_source=teams_source,
        output_features=output_features,
        state_dir=state_dir,
        team_name_aliases=dict(raw.get("team_name_aliases", {})),
    )


def resolve_config_paths(config: TournamentConfig) -> TournamentConfig:
    config.baseline_dataset = config.resolve_path(config.baseline_dataset)
    config.teams_source = config.resolve_path(config.teams_source)
    config.output_features = config.resolve_path(config.output_features)
    config.state_dir = config.resolve_path(config.state_dir)
    return config
