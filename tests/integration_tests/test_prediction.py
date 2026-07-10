import json
import pytest
import pandas as pd

from live.prediction import (
    apply_live_probability_rules,
    load_eliminated_teams,
)

@pytest.fixture
def sample_predictions():
    """Provides a standard baseline DataFrame for predictions."""
    return pd.DataFrame({
        "Team": ["Team A", "Team B", "Team C"],
        "Probability": [0.5, 0.3, 0.2]
    })

@pytest.fixture
def mock_state_file(tmp_path):
    """Helper fixture to dynamically create temporary state JSON files."""
    def _create_file(eliminated_teams):
        state_path = tmp_path / "state.json"
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump({"eliminated_teams": eliminated_teams}, f)
        return state_path
    return _create_file

def test_load_eliminated_teams(mock_state_file):
    """Verifies that eliminated teams are parsed correctly from the JSON state."""
    state_path = mock_state_file(["Team B", "Team C"])
    teams = load_eliminated_teams(state_path)
    assert teams == ["Team B", "Team C"]

def test_load_state_file_missing(tmp_path):
    """Verifies behavior when the state file does not exist.
    
    Expects FileNotFoundError natively raised by pathlib.open().
    """
    non_existent_path = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        load_eliminated_teams(non_existent_path)

def test_apply_live_probability_rules_integration_no_eliminations(sample_predictions, mock_state_file):
    """Tests the main orchestration pipeline when zero teams are eliminated."""
    state_path = mock_state_file([])
    result = apply_live_probability_rules(sample_predictions, state_path)
    
    assert "Probability" in result.columns
    assert "Live_Probability" not in result.columns
    assert (result["Status"] == "Active").all()


def test_apply_live_probability_rules_integration_with_eliminations(sample_predictions, mock_state_file):
    """Tests the main orchestration pipeline when teams are eliminated via state file."""
    state_path = mock_state_file(["Team B"])
    result = apply_live_probability_rules(sample_predictions, state_path)
    
    assert "Model_Probability" in result.columns
    assert "Live_Probability" in result.columns
    
    # Team B should be at the bottom now due to 0 probability sorting
    eliminated_row = result[result["Team"] == "Team B"].iloc[0]
    assert eliminated_row["Status"] == "Eliminated"
    assert eliminated_row["Live_Probability"] == 0.0
    
    # Active teams sum to 1
    assert result["Live_Probability"].sum() == pytest.approx(1.0)
