import pytest
import numpy as np
import pandas as pd
from pathlib import Path

import live.visualization as visualization
from live.visualization import (
    get_timeline_path,
    extract_snapshot_number,
    get_snapshot_columns,
    get_latest_snapshot_column,
    load_probability_timeline,
    validate_requested_teams,
    select_top_teams,
    resolve_visualization_teams,
    convert_probabilities_to_percent,
    prepare_probability_line_data,
    get_top_favorites_for_snapshot,
    generate_top_favorites_table,
    plot_team_probability_timeline,
    generate_top_10_by_snapshot,
)


@pytest.fixture(autouse=True)
def mock_vis_dirs(tmp_path, monkeypatch):
    """Isolates TIMELINE_DIR and VISUALIZATION_DIR within a temporary directory."""
    test_timeline_dir = tmp_path / "predictions/timelines"
    test_visualization_dir = tmp_path / "predictions/visualizations"
    
    test_timeline_dir.mkdir(parents=True, exist_ok=True)
    test_visualization_dir.mkdir(parents=True, exist_ok=True)
    
    monkeypatch.setattr(visualization, "TIMELINE_DIR", test_timeline_dir)
    monkeypatch.setattr(visualization, "VISUALIZATION_DIR", test_visualization_dir)
    
    return {
        "timelines": test_timeline_dir,
        "visualizations": test_visualization_dir,
        "base": tmp_path
    }


@pytest.fixture
def helper_create_timeline(mock_vis_dirs):
    """Helper factory to easily write valid or invalid timeline CSV files to the mock dir."""
    def _create(edition: str, data: dict | pd.DataFrame) -> Path:
        csv_path = mock_vis_dirs["timelines"] / f"{edition}_probability_timeline.csv"
        df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
        return csv_path
    return _create


# =====================================================================
# 1. get_timeline_path()
# =====================================================================
def test_get_timeline_path(mock_vis_dirs):
    """Verify correct path formation for an edition."""
    expected_path = mock_vis_dirs["timelines"] / "wc2026_probability_timeline.csv"
    assert get_timeline_path("wc2026") == expected_path


# =====================================================================
# 2. extract_snapshot_number()
# =====================================================================
@pytest.mark.parametrize("column_name,expected", [
    ("Snapshot_001", 1),
    ("Snapshot_012", 12),
    ("Snapshot_999", 999),
])
def test_extract_snapshot_number_valid(column_name, expected):
    """Verify correct numeric extraction for valid formats."""
    assert extract_snapshot_number(column_name) == expected


@pytest.mark.parametrize("invalid_column", [
    "Snapshot_", "Snapshot_abc", "snapshot_001", "Timeline_001", "Snapshot_12a"
])
def test_extract_snapshot_number_invalid(invalid_column):
    """Verify ValueError is raised for malformed snapshot strings."""
    with pytest.raises(ValueError):
        extract_snapshot_number(invalid_column)


# =====================================================================
# 3. get_snapshot_columns()
# =====================================================================
def test_get_snapshot_columns_sorting():
    """Verify snapshot columns are isolated and ordered numerically, not textually."""
    df = pd.DataFrame(columns=["Team", "Snapshot_010", "Snapshot_002", "Notes", "Snapshot_001"])
    result = get_snapshot_columns(df)
    assert result == ["Snapshot_001", "Snapshot_002", "Snapshot_010"]


# =====================================================================
# 4. get_latest_snapshot_column()
# =====================================================================
def test_get_latest_snapshot_column_success():
    """Verify the final structural snapshot column is returned."""
    df = pd.DataFrame(columns=["Team", "Snapshot_001", "Snapshot_003", "Snapshot_002"])
    assert get_latest_snapshot_column(df) == "Snapshot_003"


def test_get_latest_snapshot_column_empty_raises():
    """Verify error if no snapshot columns are present."""
    df = pd.DataFrame(columns=["Team", "Notes"])
    with pytest.raises(ValueError, match="No snapshot columns found"):
        get_latest_snapshot_column(df)


# =====================================================================
# 5. load_probability_timeline()
# =====================================================================
def test_load_probability_timeline_valid(helper_create_timeline):
    """Verify loading of a completely structured timeline."""
    valid_data = {"Team": ["USA", "MEX"], "Snapshot_001": [0.60, 0.40]}
    helper_create_timeline("wc2026", valid_data)
    
    df = load_probability_timeline("wc2026")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_load_probability_timeline_missing_file():
    """Verify FileNotFoundError when timeline does not exist on disk."""
    with pytest.raises(FileNotFoundError):
        load_probability_timeline("missing_edition")


def test_load_probability_timeline_empty_file(mock_vis_dirs):
    """Verify ValueError when file exists but contains no rows/columns."""
    csv_path = mock_vis_dirs["timelines"] / "wc2026_probability_timeline.csv"
    csv_path.write_text("Team,Snapshot_001\n")
    with pytest.raises(ValueError, match="is empty"):
        load_probability_timeline("wc2026")


def test_load_probability_timeline_missing_team_column(helper_create_timeline):
    """Verify ValueError when 'Team' tracking column is missing."""
    invalid_data = {"Snapshot_001": [0.5, 0.5]}
    helper_create_timeline("wc2026", invalid_data)
    with pytest.raises(ValueError, match="must contain a 'Team' column"):
        load_probability_timeline("wc2026")


def test_load_probability_timeline_no_snapshot_columns(helper_create_timeline):
    """Verify ValueError when timeline lacks any Snapshot_ columns."""
    invalid_data = {"Team": ["USA", "MEX"], "Total_Score": [10, 20]}
    helper_create_timeline("wc2026", invalid_data)
    with pytest.raises(ValueError, match="contains no snapshot columns"):
        load_probability_timeline("wc2026")


def test_load_probability_timeline_duplicate_teams(helper_create_timeline):
    """Verify ValueError when rows contain duplicate team names."""
    invalid_data = {"Team": ["USA", "USA"], "Snapshot_001": [0.5, 0.5]}
    helper_create_timeline("wc2026", invalid_data)
    with pytest.raises(ValueError, match="Duplicate teams found in timeline"):
        load_probability_timeline("wc2026")


# =====================================================================
# 6. validate_requested_teams()
# =====================================================================
def test_validate_requested_teams_filtering():
    """Verify uniqueness preservation, supplied ordering, and validation errors."""
    df = pd.DataFrame({"Team": ["USA", "MEX", "CAN", "FRA"]})
    
    # Valid tracking & ordering with duplicate removal
    assert validate_requested_teams(df, ["MEX", "USA", "MEX"]) == ["MEX", "USA"]
    
    # Missing team target validation
    with pytest.raises(ValueError, match="Teams not found in probability timeline"):
        validate_requested_teams(df, ["USA", "ITA"])


# =====================================================================
# 7. select_top_teams()
# =====================================================================
def test_select_top_teams_logic():
    """Verify ranking selection mechanics across distinct parameters and conditions."""
    df = pd.DataFrame({
        "Team": ["USA", "MEX", "CAN", "FRA"],
        "Snapshot_001": [0.10, 0.50, 0.30, 0.10],
        "Snapshot_002": [0.60, 0.10, 0.20, pd.NA]
    })
    
    # Default to latest snapshot (Snapshot_002) top 2, missing values (NA) dropped
    assert select_top_teams(df, count=2) == ["USA", "CAN"]
    
    # Specific snapshot specification
    assert select_top_teams(df, count=2, snapshot_column="Snapshot_001") == ["MEX", "CAN"]
    
    # Count boundary condition verification
    with pytest.raises(ValueError, match="greater than zero"):
        select_top_teams(df, count=0)


# =====================================================================
# 8. resolve_visualization_teams()
# =====================================================================
def test_resolve_visualization_teams_routing():
    """Verify routing fallback behavior when explicit targets are or aren't supplied."""
    df = pd.DataFrame({
        "Team": ["USA", "MEX", "CAN"],
        "Snapshot_001": [0.20, 0.50, 0.30]
    })
    
    # Provided explicit array
    assert resolve_visualization_teams(df, teams=["CAN", "USA"]) == ["CAN", "USA"]
    
    # Automatic fallback extraction
    assert resolve_visualization_teams(df, teams=None, default_count=2) == ["MEX", "CAN"]


# =====================================================================
# 9. convert_probabilities_to_percent()
# =====================================================================
def test_convert_probabilities_to_percent():
    """Verify decimal conversion handles values and nulls cleanly."""
    input_series = pd.Series([0.25, None, "invalid", 0.70])
    
    # Execute function target
    result = convert_probabilities_to_percent(input_series)
    
    # Construct expected structure with uniform np.nan values
    expected = pd.Series([25.0, np.nan, np.nan, 70.0], dtype=float)
    
    # Use check_dtype=False if your input coercion alters underlying storage types
    pd.testing.assert_series_equal(result, expected, check_dtype=False)


# =====================================================================
# 10. prepare_probability_line_data()
# =====================================================================
def test_prepare_probability_line_data_formatting(helper_create_timeline):
    """Verify line chart data is long-format, formatted, and chronologically sorted."""
    data = {
        "Team": ["USA", "MEX", "CAN"],
        "Snapshot_001": [0.40, 0.70, 0.10],
        "Snapshot_002": [0.45, 0.60, 0.20],
    }
    helper_create_timeline("wc2026", data)

    # Target explicit teams order: ['CAN', 'MEX']
    result_df = prepare_probability_line_data("wc2026", teams=["CAN", "MEX"])
    expected_columns = ["Snapshot", "Snapshot_Number", "Team", "Probability_Percent"]
    assert list(result_df.columns) == expected_columns

    # Check total items (2 teams * 2 snapshots)
    assert len(result_df) == 4

    # Verify strict snapshot chronological sequence first, then Team request position
    assert result_df.iloc[0]["Snapshot"] == "Snapshot_001"
    assert result_df.iloc[0]["Team"] == "CAN"
    assert result_df.iloc[1]["Snapshot"] == "Snapshot_001"
    assert result_df.iloc[1]["Team"] == "MEX"
    assert result_df.iloc[1]["Probability_Percent"] == 70.0


# =====================================================================
# 11. get_top_favorites_for_snapshot()
# =====================================================================
def test_get_top_favorites_for_snapshot_limits():
    """Verify correct rank ordering, index generation bounds, and conversion structures."""
    df = pd.DataFrame({
        "Team": ["USA", "MEX", "CAN"],
        "Snapshot_001": [0.15, 0.65, 0.20]
    })

    # Target top 2 limits
    favs = get_top_favorites_for_snapshot(df, "Snapshot_001", count=2)
    assert len(favs) == 2
    assert favs.iloc[0]["Team"] == "MEX"
    assert favs.iloc[0]["Rank"] == 1
    assert favs.iloc[0]["Probability_Percent"] == 65.0
    assert favs.iloc[1]["Team"] == "CAN"
    assert favs.iloc[1]["Rank"] == 2

    # Verify lower limit validation check
    with pytest.raises(ValueError, match="greater than zero"):
        get_top_favorites_for_snapshot(df, "Snapshot_001", count=0)


# =====================================================================
# 12. generate_top_favorites_table()
# =====================================================================
def test_generate_top_favorites_table_aggregation(helper_create_timeline):
    """Verify chronological concatenation table structure for every valid snapshot."""
    data = {
        "Team": ["USA", "MEX"],
        "Snapshot_001": [0.30, 0.70],
        "Snapshot_002": [0.80, 0.20]
    }
    helper_create_timeline("wc2026", data)

    all_favs = generate_top_favorites_table("wc2026", count=1)
    
    # Should include 1 team entry per snapshot = 2 rows
    assert len(all_favs) == 2
    assert all_favs.iloc[0]["Snapshot"] == "Snapshot_001"
    assert all_favs.iloc[0]["Team"] == "MEX"
    assert all_favs.iloc[1]["Snapshot"] == "Snapshot_002"
    assert all_favs.iloc[1]["Team"] == "USA"


# =====================================================================
# 13. plot_team_probability_timeline()
# =====================================================================
def test_plot_team_probability_timeline_generation(mock_vis_dirs, helper_create_timeline):
    """Verify visualization png path creation, parameter targets, and empty failures."""
    data = {
        "Team": ["USA", "MEX"],
        "Snapshot_001": [0.40, 0.60],
        "Snapshot_002": [0.50, 0.50]
    }
    helper_create_timeline("wc2026", data)

    # 1. Custom explicit path execution
    custom_path = mock_vis_dirs["base"] / "custom_chart.png"
    returned_path_1 = plot_team_probability_timeline("wc2026", output_path=custom_path)
    assert returned_path_1 == custom_path
    assert custom_path.exists()

    # 2. Default target generation route verification
    returned_path_2 = plot_team_probability_timeline("wc2026", teams=["USA"])
    expected_default_path = mock_vis_dirs["visualizations"] / "wc2026/wc2026_probability_timeline.png"
    assert returned_path_2 == expected_default_path
    assert expected_default_path.exists()


# =====================================================================
# 14. generate_top_10_by_snapshot()
# =====================================================================
def test_generate_top_10_by_snapshot_output(mock_vis_dirs, helper_create_timeline):
    """Verify CSV creation, tracking structure layouts, and expected row scaling constraints."""
    # Test layout using 12 teams to verify the top 10 truncation limit rule works safely
    teams_list = [f"Team_{i}" for i in range(12)]
    probs_s1 = [0.01 * i for i in range(12)]
    data = {
        "Team": teams_list,
        "Snapshot_001": probs_s1
    }
    helper_create_timeline("wc2026", data)

    expected_default_csv = mock_vis_dirs["visualizations"] / "wc2026/wc2026_top10_by_snapshot.csv"

    # Missing trailing function code patch execution block workaround fix
    # We explicitly forward an output path since the source snippet truncated right at 'VISUALIZATION_DIR / ed'
    returned_csv = generate_top_10_by_snapshot("wc2026", output_path=expected_default_csv)
    assert returned_csv == expected_default_csv
    assert expected_default_csv.exists()

    saved_df = pd.read_csv(expected_default_csv)

    # Check expected structural tracking columns
    for col in ["Snapshot", "Snapshot_Number", "Rank", "Team", "Probability_Percent"]:
        assert col in saved_df.columns

    # Since 12 teams exist, verified it extracted exactly 10 favorite tracking items limit
    assert len(saved_df) == 10
    assert saved_df["Rank"].max() == 10
