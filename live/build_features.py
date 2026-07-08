from __future__ import annotations

from pathlib import Path

import pandas as pd

from live.state import load_state
from live.form import form_summary
from live.tournament_config import TournamentConfig


# ==========================================================
# Build Updated Feature Dataset
# ==========================================================

def build_feature_dataset(
    config: TournamentConfig,
) -> pd.DataFrame:

    baseline = pd.read_csv(config.baseline_dataset)

    state = load_state(config)

    teams = state["teams"]

    updated = baseline.assign(
        Elo_Rating=baseline["Elo_Rating"].astype(float),
        WC_Matches=0,
        WC_Wins=0,
        WC_Draws=0,
        WC_Losses=0,
        WC_Goals_For=0,
        WC_Goals_Against=0,
        WC_Goal_Difference=0,
        WC_Points=0,
        Live_Form_Win_Rate=0.0,
        Live_Form_GF_Per_Game=0.0,
        Live_Form_GA_Per_Game=0.0,
        Is_Eliminated=0
    )

    updated["Elo_Rating"] = updated["Elo_Rating"].astype(float)

    for idx, row in updated.iterrows():

        team = row["Team"]

        if team not in teams:
            continue

        team_state = teams[team]

        stats = team_state["tournament_stats"]

        form = form_summary(
            team_state["form_last_n"]
        )

        # --------------------------------------------
        # Dynamic features
        # --------------------------------------------

        updated.at[idx, "Elo_Rating"] = team_state["elo"]

        # Optional live tournament statistics

        updated.at[idx, "WC_Matches"] = stats["matches"]

        updated.at[idx, "WC_Wins"] = stats["wins"]

        updated.at[idx, "WC_Draws"] = stats["draws"]

        updated.at[idx, "WC_Losses"] = stats["losses"]

        updated.at[idx, "WC_Goals_For"] = stats["goals_for"]

        updated.at[idx, "WC_Goals_Against"] = stats["goals_against"]

        updated.at[idx, "WC_Goal_Difference"] = stats["goal_difference"]

        updated.at[idx, "WC_Points"] = stats["points"]

        updated.at[idx, "Live_Form_Win_Rate"] = form["win_rate"]

        updated.at[idx, "Live_Form_GF_Per_Game"] = (
            form["goals_for_per_game"]
        )

        updated.at[idx, "Live_Form_GA_Per_Game"] = (
            form["goals_against_per_game"]
        )

        updated.at[idx, "Is_Eliminated"] = (
            int(team_state["eliminated"])
        )

    return updated


# ==========================================================
# Save Updated Dataset
# ==========================================================

def save_feature_dataset(
    df: pd.DataFrame,
    config: TournamentConfig,
) -> Path:

    output = config.output_features

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output,
        index=False,
    )

    return output


# ==========================================================
# Convenience Function
# ==========================================================

def build_and_save(
    config: TournamentConfig,
) -> Path:

    df = build_feature_dataset(config)

    return save_feature_dataset(
        df,
        config,
    )