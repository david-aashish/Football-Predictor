import pytest
import pandas as pd
from pathlib import Path

import live.snapshot as snapshot
from live.snapshot import (
    get_next_snapshot_number,
    save_prediction_snapshot,
    reset_snapshots,
)


@pytest.fixture(autouse=True)
def mock_dirs(tmp_path, monkeypatch):
    """
    Redirects SNAPSHOT_DIR and VISUALIZATION_DIR and isolates the timeline folder execution.
    Forces everything into an isolated temporary directory runner safely.
    """
    test_snapshot_dir = tmp_path / "predictions/snapshots"
    test_visualization_dir = tmp_path / "predictions/visualizations"
    
    # 1. Safely mock the module level global directory constants
    monkeypatch.setattr(snapshot, "SNAPSHOT_DIR", test_snapshot_dir)
    monkeypatch.setattr(snapshot, "VISUALIZATION_DIR", test_visualization_dir)
    
    # 2. Change execution directory so relative 'predictions/timelines' routes here
    monkeypatch.chdir(tmp_path)
    
    return {
        "snapshots": test_snapshot_dir,
        "visualizations": test_visualization_dir,
        "base": tmp_path
    }


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
    snapshot_dir = mock_dirs["snapshots"]
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
    snapshot_dir = mock_dirs["snapshots"]
    
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
    snapshot_dir = mock_dirs["snapshots"]
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
    snapshot_dir = mock_dirs["snapshots"]
    edition_dir = snapshot_dir / "wc2026"
    edition_dir.mkdir(parents=True, exist_ok=True)
    
    file_to_delete = edition_dir / "snapshot_001_pre_tournament.csv"
    file_to_delete.touch()
    
    reset_snapshots("wc2026")
    assert not file_to_delete.exists()


def test_reset_snapshots_does_not_delete_other_editions(mock_dirs):
    """Test that files belonging to separate tournament editions remain untouched."""
    snapshot_dir = mock_dirs["snapshots"]
    vis_dir = mock_dirs["visualizations"]
    base_dir = mock_dirs["base"]

    # Target edition paths (wc2026)
    edition_dir = snapshot_dir / "wc2026"
    edition_dir.mkdir(parents=True, exist_ok=True)

    # Separate edition paths (wc2030)
    other_edition_dir = snapshot_dir / "wc2030"
    other_edition_dir.mkdir(parents=True, exist_ok=True)
    other_snapshot = other_edition_dir / "snapshot_001_pre_tournament.csv"
    other_snapshot.touch()

    other_vis_dir = vis_dir / "wc2030"
    other_vis_dir.mkdir(parents=True, exist_ok=True)
    other_png = other_vis_dir / "wc2030_chart.png"
    other_csv = other_vis_dir / "wc2030_top10.csv"
    other_png.touch()
    other_csv.touch()

    other_timeline = base_dir / "predictions" / "timelines" / "wc2030_probability_timeline.csv"
    other_timeline.parent.mkdir(parents=True, exist_ok=True)
    other_timeline.touch()
    
    # Execute reset on target edition
    reset_snapshots("wc2026")

    # Verify separate edition outputs are completely unchanged
    assert other_snapshot.exists()
    assert other_png.exists()
    assert other_csv.exists()
    assert other_timeline.exists()


def test_reset_snapshots_deletes_timeline_file_if_present(mock_dirs):
    """Test that the main timeline summary tracking file is wiped out during reset."""
    base_dir = mock_dirs["base"]
    
    timeline_dir = base_dir / "predictions" / "timelines"
    timeline_dir.mkdir(parents=True, exist_ok=True)
    
    timeline_file = timeline_dir / "wc2026_probability_timeline.csv"
    timeline_file.touch()
    
    reset_snapshots("wc2026")
    assert not timeline_file.exists()


def test_reset_snapshots_deletes_visualization_outputs(mock_dirs):
    """Test that target edition visualization files (PNG images and top-10 CSVs) are deleted."""
    vis_dir = mock_dirs["visualizations"]
    target_vis_dir = vis_dir / "wc2026"
    target_vis_dir.mkdir(parents=True, exist_ok=True)

    # Generate visualization artifacts matching requirements
    vis_png = target_vis_dir / "wc2026_bracket.png"
    vis_csv = target_vis_dir / "wc2026_top10.csv"
    vis_png.touch()
    vis_csv.touch()

    reset_snapshots("wc2026")

    assert not vis_png.exists()
    assert not vis_csv.exists()


def test_reset_snapshots_does_not_fail_if_files_or_directories_missing():
    """Test that the system exits cleanly without errors if files or directories do not exist."""
    try:
        reset_snapshots("wc2026")
    except Exception as e:
        pytest.fail(f"reset_snapshots threw an unexpected error when file structures were missing: {e}")
