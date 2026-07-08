import json
from pathlib import Path
import pytest
import pandas as pd
from unittest.mock import MagicMock

from live.state import (
    create_initial_state,
    save_state,
    load_state,
    match_already_recorded,
    validate_teams_in_state,
)

@pytest.fixture
def mock_config(tmp_path):
    """Creates a mock TournamentConfig with temporary directory paths."""
    config = MagicMock()
    config.edition = "wc2026"
    config.year = 2026
    config.state_dir = tmp_path / "state"
    config.state_file = config.state_dir / "state.json"
    
    # Create a dummy CSV baseline dataset
    csv_path = tmp_path / "baseline.csv"
    df = pd.DataFrame({
        "Team": ["France", "Germany", "Italy"],
        "Elo_Rating": [1900.5, 1850.0, 1800.2]
    })
    df.to_csv(csv_path, index=False)
    config.baseline_dataset = csv_path
    
    return config

@pytest.fixture
def sample_state():
    """Returns a basic valid state structure for testing."""
    return {
        "edition": "wc2026",
        "year": 2026,
        "current_phase": "group_stage",
        "teams": {
            "France": {"elo": 1900.5, "eliminated": False},
            "Germany": {"elo": 1850.0, "eliminated": False}
        },
        "completed_matches": [],
        "eliminated_teams": [],
        "group_standings": {},
    }

# ==========================================
# TEST CASES
# ==========================================

# 1. Test create_initial_state()
def test_create_initial_state(mock_config):
    state = create_initial_state(mock_config)
    
    assert state["edition"] == "wc2026"
    assert state["year"] == 2026
    assert state["current_phase"] == "pre_tournament"
    assert "France" in state["teams"]
    assert state["teams"]["France"]["elo"] == 1900.5
    assert state["teams"]["France"]["tournament_stats"]["matches"] == 0

# 2. Test save_state()
def test_save_state(sample_state, mock_config):
    saved_path = save_state(sample_state, mock_config)
    
    assert saved_path == mock_config.state_file
    assert saved_path.exists()
    
    with saved_path.open(encoding="utf-8") as f:
        data = json.load(f)
    assert data["edition"] == "wc2026"

# 3. Test load_state()
def test_load_state_success(sample_state, mock_config):
    # Setup: save the file first
    save_state(sample_state, mock_config)
    
    loaded_data = load_state(mock_config)
    assert loaded_data["edition"] == "wc2026"
    assert "France" in loaded_data["teams"]

def test_load_state_file_not_found(mock_config):
    with pytest.raises(FileNotFoundError) as exc_info:
        load_state(mock_config)
    assert "Tournament state not found" in str(exc_info.value)

# 4. Test duplicate detection (match_already_recorded)
def test_match_already_recorded_by_id(sample_state):
    match = {"match_id": "M123", "home_team": "France", "away_team": "Germany", "home_goals": 2, "away_goals": 1}
    sample_state["completed_matches"].append(match)
    
    # Same ID
    test_match = {"match_id": "M123", "home_team": "France", "away_team": "Germany"}
    assert match_already_recorded(sample_state, test_match) is True

def test_match_already_recorded_by_surrogate_key(sample_state):
    match = {
        "home_team": "France", "away_team": "Germany", 
        "home_goals": 2, "away_goals": 1, 
        "round": "Group A", "group": "A"
    }
    sample_state["completed_matches"].append(match)
    
    # Duplicate with no ID but matching key fields
    duplicate_match = {
        "home_team": "France", "away_team": "Germany", 
        "home_goals": 2, "away_goals": 1, 
        "round": "Group A", "group": "A"
    }
    assert match_already_recorded(sample_state, duplicate_match) is True

def test_match_not_recorded(sample_state):
    match = {"home_team": "France", "away_team": "Germany", "home_goals": 2, "away_goals": 1}
    assert match_already_recorded(sample_state, match) is False

# 5. Test validate_teams_in_state()
def test_validate_teams_both_valid(sample_state):
    # Should run without raising any exceptions
    validate_teams_in_state(sample_state, "France", "Germany")

def test_validate_teams_home_missing(sample_state):
    with pytest.raises(ValueError) as exc_info:
        validate_teams_in_state(sample_state, "Spain", "Germany")
    assert "Unknown team(s) for this edition: Spain" in str(exc_info.value)

def test_validate_teams_away_missing(sample_state):
    with pytest.raises(ValueError) as exc_info:
        validate_teams_in_state(sample_state, "France", "England")
    assert "Unknown team(s) for this edition: England" in str(exc_info.value)

def test_validate_teams_both_missing(sample_state):
    with pytest.raises(ValueError) as exc_info:
        validate_teams_in_state(sample_state, "Spain", "England")
    assert "Unknown team(s) for this edition: Spain, England" in str(exc_info.value)