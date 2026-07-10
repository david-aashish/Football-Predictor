import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch

import live.snapshot as snapshot
from live.snapshot import (
    get_next_snapshot_number,
    save_prediction_snapshot,
    reset_snapshots,
)


@pytest.fixture(autouse=True)
def mock_dirs(tmp_path, monkeypatch):
    """
    Redirects SNAPSHOT_DIR and isolates the timeline folder execution.
    Forces everything into an isolated temporary directory runner safely.
    """
    test_snapshot_dir = tmp_path / "predictions/snapshots"
    
    # 1. Safely mock the module level SNAPSHOT_DIR global constant
    monkeypatch.setattr(snapshot, "SNAPSHOT_DIR", test_snapshot_dir)
    
    # 2. Change execution directory so relative 'predictions/timelines' routes here
    monkeypatch.chdir(tmp_path)
    
    return test_snapshot_dir


@pytest.fixture
def sample_predictions():
    """Provides a sample pandas DataFrame to mimic prediction data."""
    return pd.DataFrame({"team": ["USA", "MEX"], "prob": [0.6, 0.4]})


# =====================================================================
# 1. TEST CASES FOR get_next_snapshot_number()
# =====================================================================

def test_get_next_snapshot_number_no_existing():
    """Test that 1 is returned when no snapshots exist for the edition."""
    assert get_next_snapshot_number("wc2026") == 1


def test_get_next_snapshot_number_existing_two(mock_dirs):
    """Test that 3 is returned when 2 snapshots already exist."""
    snapshot_dir = mock_dirs
    edition_dir = snapshot_dir / "wc2026"
    edition_dir.mkdir(parents=True, exist_ok=True)
    
    # Create two dummy snapshot files
    (edition_dir / "snapshot_001_pre_tournament.csv").touch()
    (edition_dir / "snapshot_002_match_001.csv").touch()
    
    assert get_next_snapshot_number("wc2026") == 3


# =====================================================================
# 2. TEST CASES FOR save_prediction_snapshot()
# =====================================================================

def test_save_prediction_snapshot_creates_folder_if_missing(mock_dirs, sample_predictions):
    """Test that the snapshots folder is generated if it does not exist."""
    snapshot_dir = mock_dirs
    
    # Ensure it's deleted before the run
    if snapshot_dir.exists():
        snapshot_dir.rmdir()
        
    state = {"completed_matches": []}
    save_prediction_snapshot(sample_predictions, "wc2026", state)
    
    assert snapshot_dir.exists()


def test_save_prediction_snapshot_saves_csv_and_correct_data(sample_predictions):
    """Test that a valid CSV file is saved containing the exact input data."""
    state = {"completed_matches": []}
    output_file = save_prediction_snapshot(sample_predictions, "wc2026", state)
    
    assert output_file.exists()
    # Read back and verify the dataframe match
    saved_df = pd.read_csv(output_file)
    pd.testing.assert_frame_equal(saved_df, sample_predictions)


def test_save_prediction_snapshot_pre_tournament_naming(sample_predictions):
    """CRITICAL TEST: Verifies label is 'pre_tournament' when completed_matches is empty."""
    state = {"completed_matches": []}
    output_file = save_prediction_snapshot(sample_predictions, "wc2026", state)
    
    assert "pre_tournament" in output_file.name
    assert output_file.name == "snapshot_001_pre_tournament.csv"


def test_save_prediction_snapshot_match_indexed_naming(mock_dirs, sample_predictions):
    """CRITICAL TEST: Verifies file names use sequential match notation (match_002)."""
    snapshot_dir = mock_dirs
    edition_dir = snapshot_dir / "wc2026"
    edition_dir.mkdir(parents=True, exist_ok=True)

    (edition_dir / "snapshot_001_pre_tournament.csv").touch()
    (edition_dir / "snapshot_002_match_001.csv").touch()

    state = {"completed_matches": ["M01", "M02"]}
    output_file = save_prediction_snapshot(sample_predictions, "wc2026", state)
    
    assert "match_002" in output_file.name
    assert output_file.name == "snapshot_003_match_002.csv"


def test_save_prediction_snapshot_increments_correctly(sample_predictions):
    """CRITICAL TEST: Verifies snapshot indexing number increments chronologically."""
    state_empty = {"completed_matches": []}
    state_active = {"completed_matches": ["M01"]}
    
    file_1 = save_prediction_snapshot(sample_predictions, "wc2026", state_empty)
    file_2 = save_prediction_snapshot(sample_predictions, "wc2026", state_active)
    
    assert "snapshot_001" in file_1.name
    assert "snapshot_002" in file_2.name


# =====================================================================
# 3. TEST CASES FOR reset_snapshots()
# =====================================================================

def test_reset_snapshots_clears_old_snapshots_of_target_edition(mock_dirs):
    """CRITICAL TEST: Clears snapshots belonging explicitly to the targeted edition."""
    snapshot_dir = mock_dirs
    edition_dir = snapshot_dir / "wc2026"
    edition_dir.mkdir(parents=True, exist_ok=True)
    
    file_to_delete = edition_dir / "snapshot_001_pre_tournament.csv"
    file_to_delete.touch()
    
    reset_snapshots("wc2026")
    assert not file_to_delete.exists()


def test_reset_snapshots_does_not_delete_other_editions(mock_dirs):
    """Test that files belonging to separate tournament editions remain untouched."""
    snapshot_dir = mock_dirs
    edition_dir = snapshot_dir / "wc2026"
    edition_dir.mkdir(parents=True, exist_ok=True)

    other_edition_dir = snapshot_dir / "euro2024"
    other_edition_dir.mkdir(parents=True, exist_ok=True)
    
    other_edition_file = other_edition_dir / "snapshot_001_pre_tournament.csv"
    other_edition_file.touch()
    
    reset_snapshots("wc2026")
    assert other_edition_file.exists()


def test_reset_snapshots_deletes_timeline_file_if_present(mock_dirs, monkeypatch):
    """Test that the main timeline summary tracking file is wiped out during reset."""
    # Using monkeypatch to change your system's current working directory 
    # to the temp path, causing relative paths like Path("predictions/timelines") 
    # to naturally point inside our fake folder setup.
    base_dir = mock_dirs.parent.parent
    monkeypatch.chdir(base_dir)
    
    timeline_dir = base_dir / "predictions" / "timelines"
    timeline_dir.mkdir(parents=True, exist_ok=True)
    
    timeline_file = timeline_dir / "wc2026_probability_timeline.csv"
    timeline_file.touch()
    
    reset_snapshots("wc2026")
    assert not timeline_file.exists()
