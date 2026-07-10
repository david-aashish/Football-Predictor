import json
import pytest
import pandas as pd

from live.prediction import (
    load_eliminated_teams,
    add_rank,
    apply_no_elimination_rules,
    apply_elimination_rules,
)

@pytest.fixture
def sample_predictions():
    """Provides a standard baseline DataFrame for predictions."""
    return pd.DataFrame({
        "Team": ["Team A", "Team B", "Team C"],
        "Probability": [0.5, 0.3, 0.2]
    })

def test_add_rank(sample_predictions):
    """Verifies that ranking is accurately assigned starting from 1."""
    df_ranked = add_rank(sample_predictions)
    assert "Rank" in df_ranked.columns
    assert list(df_ranked["Rank"]) == [1, 2, 3]


def test_apply_no_elimination_rules(sample_predictions):
    """Verifies: No eliminated teams -> Probability stays unchanged, Status remains Active."""
    result = apply_no_elimination_rules(sample_predictions)
    
    assert "Probability" in result.columns
    assert "Status" in result.columns
    assert (result["Status"] == "Active").all()
    assert list(result["Probability"]) == [0.5, 0.3, 0.2]
    assert list(result["Rank"]) == [1, 2, 3]


def test_apply_elimination_rules(sample_predictions):
    """Verifies: Eliminated team -> probability becomes 0, Remaining normalize to 1, Status updates."""
    eliminated = ["Team C"]
    result = apply_elimination_rules(sample_predictions, eliminated)
    
    # Check column renames and additions
    assert "Model_Probability" in result.columns
    assert "Live_Probability" in result.columns
    
    # Check status assignment
    assert result.loc[result["Team"] == "Team A", "Status"].values[0] == "Active"
    assert result.loc[result["Team"] == "Team C", "Status"].values[0] == "Eliminated"
    
    # Check probability zeroed out
    assert result.loc[result["Team"] == "Team C", "Live_Probability"].values[0] == 0.0
    
    # Check normalization: Remaining active teams (0.5 and 0.3) should scale up to total 1.0
    # Expected for A: 0.5 / (0.5 + 0.3) = 0.625
    # Expected for B: 0.3 / (0.5 + 0.3) = 0.375
    team_a_prob = result.loc[result["Team"] == "Team A", "Live_Probability"].values[0]
    team_b_prob = result.loc[result["Team"] == "Team B", "Live_Probability"].values[0]
    
    assert team_a_prob == pytest.approx(0.625)
    assert team_b_prob == pytest.approx(0.375)
    assert result["Live_Probability"].sum() == pytest.approx(1.0)
