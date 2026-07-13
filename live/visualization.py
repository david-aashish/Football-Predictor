"""
visualization.py

visualization data utilities.

Responsibilities:
- Load an edition-specific probability timeline
- Validate snapshot data
- Select teams for visualization
- Convert probabilities from decimals to percentages
- Prepare line-chart data
- Generate top-N favorite tables for each snapshot
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd


TIMELINE_DIR = Path("predictions/timelines")
VISUALIZATION_DIR = Path("predictions/visualizations")
DEFAULT_TOP_TEAMS = 5
DEFAULT_FAVORITES_COUNT = 10
DEFAULT_FIGURE_SIZE = (12, 7)


# ==========================================================
# Timeline Loading
# ==========================================================

def get_timeline_path(edition: str) -> Path:
    """
    Return the probability timeline path for a tournament edition.
    """

    return TIMELINE_DIR / f"{edition}_probability_timeline.csv"


def load_probability_timeline(edition: str) -> pd.DataFrame:
    """
    Load and validate an edition-specific probability timeline.

    Expected structure:
        Team | Snapshot_001 | Snapshot_002 | ...

    Returns:
        Validated timeline DataFrame.
    """

    timeline_path = get_timeline_path(edition)

    if not timeline_path.exists():
        raise FileNotFoundError(
            f"Probability timeline not found: {timeline_path}. "
            f"Initialize the tournament and process predictions first."
        )

    timeline_df = pd.read_csv(timeline_path)

    if timeline_df.empty:
        raise ValueError(
            f"Probability timeline is empty: {timeline_path}"
        )

    if "Team" not in timeline_df.columns:
        raise ValueError(
            "Probability timeline must contain a 'Team' column."
        )

    snapshot_columns = get_snapshot_columns(timeline_df)

    if not snapshot_columns:
        raise ValueError(
            "Probability timeline contains no snapshot columns."
        )

    if timeline_df["Team"].duplicated().any():
        duplicated_teams = (
            timeline_df.loc[
                timeline_df["Team"].duplicated(),
                "Team"
            ]
            .unique()
            .tolist()
        )

        raise ValueError(
            f"Duplicate teams found in timeline: {duplicated_teams}"
        )

    timeline_df[snapshot_columns] = timeline_df[
        snapshot_columns
    ].apply(pd.to_numeric, errors="coerce")

    return timeline_df


# ==========================================================
# Snapshot Helpers
# ==========================================================

def extract_snapshot_number(column_name: str) -> int:
    """
    Extract the number from a snapshot column.

    Example:
        Snapshot_003 -> 3
    """

    if not column_name.startswith("Snapshot_"):
        raise ValueError(
            f"Invalid snapshot column name: {column_name}"
        )

    number_text = column_name.removeprefix("Snapshot_")

    if not number_text.isdigit():
        raise ValueError(
            f"Invalid snapshot number in column: {column_name}"
        )

    return int(number_text)


def get_snapshot_columns(timeline_df: pd.DataFrame) -> list[str]:
    """
    Return snapshot columns in numerical order.
    """

    snapshot_columns = [
        column
        for column in timeline_df.columns
        if column.startswith("Snapshot_")
    ]

    return sorted(
        snapshot_columns,
        key=extract_snapshot_number
    )


def get_latest_snapshot_column(
    timeline_df: pd.DataFrame
) -> str:
    """
    Return the latest available snapshot column.
    """

    snapshot_columns = get_snapshot_columns(timeline_df)

    if not snapshot_columns:
        raise ValueError(
            "No snapshot columns found in probability timeline."
        )

    return snapshot_columns[-1]


# ==========================================================
# Team Selection
# ==========================================================

def validate_requested_teams(
    timeline_df: pd.DataFrame,
    teams: Iterable[str],
) -> list[str]:
    """
    Validate requested teams and preserve their supplied order.
    """

    requested_teams = list(dict.fromkeys(teams))
    available_teams = set(timeline_df["Team"])

    missing_teams = [
        team
        for team in requested_teams
        if team not in available_teams
    ]

    if missing_teams:
        raise ValueError(
            f"Teams not found in probability timeline: "
            f"{missing_teams}"
        )

    return requested_teams


def select_top_teams(
    timeline_df: pd.DataFrame,
    count: int = DEFAULT_TOP_TEAMS,
    snapshot_column: str | None = None,
) -> list[str]:
    """
    Select the highest-ranked teams from a snapshot.

    By default, teams are selected using the latest snapshot.
    """

    if count <= 0:
        raise ValueError("Team count must be greater than zero.")

    if snapshot_column is None:
        snapshot_column = get_latest_snapshot_column(
            timeline_df
        )

    if snapshot_column not in timeline_df.columns:
        raise ValueError(
            f"Snapshot column not found: {snapshot_column}"
        )

    ranking_df = timeline_df[
        ["Team", snapshot_column]
    ].copy()

    ranking_df = ranking_df.dropna(
        subset=[snapshot_column]
    )

    ranking_df = ranking_df.sort_values(
        snapshot_column,
        ascending=False
    )

    return ranking_df["Team"].head(count).tolist()


def resolve_visualization_teams(
    timeline_df: pd.DataFrame,
    teams: Iterable[str] | None = None,
    default_count: int = DEFAULT_TOP_TEAMS,
) -> list[str]:
    """
    Use explicitly requested teams or automatically select
    the current top teams.
    """

    if teams:
        return validate_requested_teams(
            timeline_df,
            teams
        )

    return select_top_teams(
        timeline_df,
        count=default_count
    )


# ==========================================================
# Probability Conversion
# ==========================================================

def convert_probabilities_to_percent(
    probability_values: pd.Series
) -> pd.Series:
    """
    Convert decimal probabilities into percentage values.

    Example:
        0.2648 -> 26.48
    """

    numeric_values = pd.to_numeric(
        probability_values,
        errors="coerce"
    )

    return numeric_values * 100


# ==========================================================
# Line Chart Data
# ==========================================================

def prepare_probability_line_data(
    edition: str,
    teams: Iterable[str] | None = None,
    default_team_count: int = DEFAULT_TOP_TEAMS,
) -> pd.DataFrame:
    """
    Prepare long-format data for a champion probability
    timeline line chart.

    Output:
        Snapshot | Snapshot_Number | Team | Probability_Percent
    """

    timeline_df = load_probability_timeline(edition)

    selected_teams = resolve_visualization_teams(
        timeline_df,
        teams=teams,
        default_count=default_team_count
    )

    snapshot_columns = get_snapshot_columns(timeline_df)

    selected_df = timeline_df[
        timeline_df["Team"].isin(selected_teams)
    ][["Team", *snapshot_columns]].copy()

    line_data = selected_df.melt(
        id_vars="Team",
        value_vars=snapshot_columns,
        var_name="Snapshot",
        value_name="Probability"
    )

    line_data["Snapshot_Number"] = (
        line_data["Snapshot"]
        .map(extract_snapshot_number)
    )

    line_data["Probability_Percent"] = (
        convert_probabilities_to_percent(
            line_data["Probability"]
        )
    )

    team_order = {
        team: position
        for position, team in enumerate(selected_teams)
    }

    line_data["Team_Order"] = (
        line_data["Team"].map(team_order)
    )

    line_data = line_data.sort_values(
        ["Snapshot_Number", "Team_Order"]
    ).reset_index(drop=True)

    return line_data[
        [
            "Snapshot",
            "Snapshot_Number",
            "Team",
            "Probability_Percent",
        ]
    ]

# ==========================================================
# Probability Timeline Chart
# ==========================================================

def plot_team_probability_timeline(
    edition: str,
    teams: Iterable[str] | None = None,
    default_team_count: int = DEFAULT_TOP_TEAMS,
    output_path: Path | None = None,
) -> Path:
    """
    Plot champion probability progression over tournament snapshots.

    If teams are provided:
        Plot only those teams.

    If teams are not provided:
        Plot the latest top teams automatically.

    Output:
        predictions/visualizations/
            {edition}_probability_timeline.png
    """

    line_data = prepare_probability_line_data(
        edition=edition,
        teams=teams,
        default_team_count=default_team_count,
    )

    if line_data.empty:
        raise ValueError(
            "No probability timeline data is available to plot."
        )

    selected_teams = line_data["Team"].drop_duplicates().tolist()

    snapshot_numbers = sorted(
        line_data["Snapshot_Number"].unique()
    )

    fig, axis = plt.subplots(
        figsize=DEFAULT_FIGURE_SIZE
    )

    for team in selected_teams:
        team_data = line_data[
            line_data["Team"] == team
        ].sort_values("Snapshot_Number")

        axis.plot(
            team_data["Snapshot_Number"],
            team_data["Probability_Percent"],
            marker="o",
            linewidth=2,
            label=team,
        )

    axis.set_title(
        f"{edition.upper()} Champion Probability Timeline"
    )

    axis.set_xlabel("Prediction Snapshot")
    axis.set_ylabel("Champion Probability (%)")

    axis.set_xticks(snapshot_numbers)

    axis.set_xticklabels(
        [
            "Pre-Tournament"
            if snapshot_number == 1
            else f"Match {snapshot_number - 1}"
            for snapshot_number in snapshot_numbers
        ],
        rotation=45,
        ha="right",
    )

    axis.set_ylim(bottom=0)
    axis.grid(True, alpha=0.3)

    axis.legend(
        title="Teams",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
    )

    fig.tight_layout()

    if output_path is None:
        output_path = (
            VISUALIZATION_DIR
            / edition
            / f"{edition}_probability_timeline.png"
        )
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    return output_path


# ==========================================================
# Top Favorites
# ==========================================================

def get_top_favorites_for_snapshot(
    timeline_df: pd.DataFrame,
    snapshot_column: str,
    count: int = DEFAULT_FAVORITES_COUNT,
) -> pd.DataFrame:
    """
    Return the top teams for one snapshot.

    Output:
        Snapshot | Snapshot_Number | Rank |
        Team | Probability_Percent
    """

    if count <= 0:
        raise ValueError(
            "Favorites count must be greater than zero."
        )

    if snapshot_column not in timeline_df.columns:
        raise ValueError(
            f"Snapshot column not found: {snapshot_column}"
        )

    favorites = timeline_df[
        ["Team", snapshot_column]
    ].copy()

    favorites = favorites.dropna(
        subset=[snapshot_column]
    )

    favorites = favorites.sort_values(
        snapshot_column,
        ascending=False
    ).head(count).reset_index(drop=True)

    favorites.insert(
        0,
        "Rank",
        favorites.index + 1
    )

    favorites = favorites.rename(
        columns={
            snapshot_column: "Probability"
        }
    )

    favorites["Probability_Percent"] = (
        convert_probabilities_to_percent(
            favorites["Probability"]
        )
    )

    favorites.insert(
        0,
        "Snapshot_Number",
        extract_snapshot_number(snapshot_column)
    )

    favorites.insert(
        0,
        "Snapshot",
        snapshot_column
    )

    return favorites[
        [
            "Snapshot",
            "Snapshot_Number",
            "Rank",
            "Team",
            "Probability_Percent",
        ]
    ]


def generate_top_favorites_table(
    edition: str,
    count: int = DEFAULT_FAVORITES_COUNT,
) -> pd.DataFrame:
    """
    Generate top-N favorite rankings for every snapshot.

    Output:
        Snapshot | Snapshot_Number | Rank |
        Team | Probability_Percent
    """

    timeline_df = load_probability_timeline(edition)
    snapshot_columns = get_snapshot_columns(timeline_df)

    snapshot_tables = [
        get_top_favorites_for_snapshot(
            timeline_df,
            snapshot_column,
            count=count
        )
        for snapshot_column in snapshot_columns
    ]

    if not snapshot_tables:
        return pd.DataFrame(
            columns=[
                "Snapshot",
                "Snapshot_Number",
                "Rank",
                "Team",
                "Probability_Percent",
            ]
        )

    return pd.concat(
        snapshot_tables,
        ignore_index=True
    )

# ==========================================================
# Top Favorites Output
# ==========================================================

def generate_top_10_by_snapshot(
    edition: str,
    output_path: Path | None = None,
) -> Path:
    """
    Generate and save the top 10 champion favorites
    for every prediction snapshot.

    Output:
        predictions/visualizations/{edition}/
            {edition}_top10_by_snapshot.csv
    """

    top_10_df = generate_top_favorites_table(
        edition=edition,
        count=10,
    )

    if top_10_df.empty:
        raise ValueError(
            "No snapshot probability data is available."
        )

    if output_path is None:
        output_path = (
            VISUALIZATION_DIR
            / edition
            / f"{edition}_top10_by_snapshot.csv"
        )
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    top_10_df.to_csv(
        output_path,
        index=False,
    )

    return output_path
