import pytest
import pandas as pd
from unittest.mock import patch

import live.timeline as timeline
from live.timeline import build_probability_timeline


@pytest.fixture(autouse=True)
def mock_timeline_dirs(tmp_path):
    """
    Redirects global SNAPSHOT_DIR and TIMELINE_DIR paths to a 
    temporary directory for isolated integration testing.
    """
    test_snapshot_dir = tmp_path / "predictions/snapshots"
    test_timeline_dir = tmp_path / "predictions/timelines"
    
    test_snapshot_dir.mkdir(parents=True, exist_ok=True)
    test_timeline_dir.mkdir(parents=True, exist_ok=True)
    
    with patch.object(timeline, "SNAPSHOT_DIR", test_snapshot_dir), \
         patch.object(timeline, "TIMELINE_DIR", test_timeline_dir):
        yield test_snapshot_dir, test_timeline_dir


# =====================================================================
# INTEGRATION TESTS
# =====================================================================

def test_build_probability_timeline_end_to_end(mock_timeline_dirs):
    """
    Verifies the end-to-end integration workflow:
    1. Reads multiple snapshot files for a specific tournament edition.
    2. Reshapes data into wide format (one clean row per team).
    3. Maps correct snapshot values chronologically (Snapshot_001, Snapshot_002).
    4. Writes the finalized compiled CSV file back to disk.
    """
    snapshot_dir, timeline_dir = mock_timeline_dirs
    edition = "wc2026"

    edition_dir = snapshot_dir / edition
    edition_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Seed historical file sequence 
    snap_1 = pd.DataFrame({"Team": ["Spain", "Argentina"], "Probability": [0.15, 0.20]})
    snap_1.to_csv(edition_dir / "snapshot_001_pre_tournament.csv", index=False)
    
    snap_2 = pd.DataFrame({"Team": ["Spain", "Argentina"], "Probability": [0.18, 0.19]})
    snap_2.to_csv(edition_dir / "snapshot_002_match_001.csv", index=False)

    # 2. Trigger processing runner engine
    result_df = build_probability_timeline(edition=edition)
    
    # 3. Assert DataFrame properties and spatial layout structure
    assert list(result_df.columns) == ["Team", "Snapshot_001", "Snapshot_002"]
    assert len(result_df) == 2
    
    # Verify accurate horizontal matrix mapping per team reference group
    spain_metrics = result_df[result_df["Team"] == "Spain"].iloc[0]
    assert spain_metrics["Snapshot_001"] == 0.15
    assert spain_metrics["Snapshot_002"] == 0.18
    
    # 4. Assert disk persistence and check storage validity
    expected_output_file = timeline_dir / f"{edition}_probability_timeline.csv"
    assert expected_output_file.exists()
    
    saved_df = pd.read_csv(expected_output_file)
    pd.testing.assert_frame_equal(saved_df, result_df)


def test_build_probability_timeline_isolates_and_filters_editions(mock_timeline_dirs):
    """Verifies that processing skips snapshots from separate, untargeted editions."""
    snapshot_dir, timeline_dir = mock_timeline_dirs
    
    # Seed a targeted edition snapshot file
    target_edition_dir = snapshot_dir / "wc2026"
    target_edition_dir.mkdir(parents=True, exist_ok=True)
    target_data = pd.DataFrame({"Team": ["France"], "Probability": [0.25]})
    target_data.to_csv(target_edition_dir / "snapshot_001_pre_tournament.csv", index=False)
    
    # Seed an external edition snapshot file that should be ignored
    ignored_edition_dir = snapshot_dir / "wc2030"
    ignored_edition_dir.mkdir(parents=True, exist_ok=True)
    ignored_data = pd.DataFrame({"Team": ["France"], "Probability": [0.40]})
    ignored_data.to_csv(ignored_edition_dir / "snapshot_001_pre_tournament.csv", index=False)
    
    # Run pipeline explicitly targeting wc2026
    result_df = build_probability_timeline(edition="wc2026")
    
    # Ensure columns and values belong strictly to the targeted edition (wc2026)
    assert "Snapshot_001" in result_df.columns
    assert len(result_df) == 1
    assert result_df.loc[result_df["Team"] == "France", "Snapshot_001"].values[0] == 0.25
    
    # Verify the generated file matches the target edition name structure
    assert (timeline_dir / "wc2026_probability_timeline.csv").exists()
    assert not (timeline_dir / "wc2030_probability_timeline.csv").exists()
