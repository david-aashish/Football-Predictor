"""
prediction.py

Stage 2B live prediction rules.

If no team is eliminated:
    Rank | Team | Probability | Status

If one or more teams are eliminated:
    Rank | Team | Model_Probability | Live_Probability | Status
"""

import json
from pathlib import Path


def load_eliminated_teams(state_path):
    state_path = Path(state_path)

    with state_path.open("r", encoding="utf-8") as file:
        state = json.load(file)

    return state.get("eliminated_teams", [])


def add_rank(predictions):
    predictions = predictions.copy()

    if "Rank" in predictions.columns:
        predictions = predictions.drop(columns=["Rank"])

    predictions = predictions.reset_index(drop=True)

    predictions.insert(
        0,
        "Rank",
        predictions.index + 1
    )

    return predictions


def apply_no_elimination_rules(predictions):
    predictions = predictions.copy()

    predictions["Status"] = "Active"

    predictions = predictions.sort_values(
        "Probability",
        ascending=False
    )

    predictions = add_rank(predictions)

    return predictions


def apply_elimination_rules(predictions, eliminated_teams):
    predictions = predictions.copy()

    predictions = predictions.rename(
        columns={"Probability": "Model_Probability"}
    )

    predictions["Live_Probability"] = predictions["Model_Probability"]
    predictions["Status"] = "Active"

    is_eliminated = predictions["Team"].isin(eliminated_teams)

    predictions.loc[
        is_eliminated,
        "Live_Probability"
    ] = 0

    predictions.loc[
        is_eliminated,
        "Status"
    ] = "Eliminated"

    total_probability = predictions["Live_Probability"].sum()

    if total_probability > 0:
        predictions["Live_Probability"] = (
            predictions["Live_Probability"] / total_probability
        )

    predictions = predictions.sort_values(
        "Live_Probability",
        ascending=False
    )

    predictions = add_rank(predictions)

    return predictions


def apply_live_probability_rules(predictions, state_path):
    eliminated_teams = load_eliminated_teams(state_path)

    if len(eliminated_teams) == 0:
        return apply_no_elimination_rules(predictions)

    return apply_elimination_rules(
        predictions,
        eliminated_teams
    )
    