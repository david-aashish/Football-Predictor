import sys
import pytest
from unittest.mock import MagicMock

import live.adapters.visualize as visualize
from live.adapters.visualize import main


@pytest.fixture
def mock_viz_actions(monkeypatch):
    """
    Mock the underlying core visualization functions to check CLI orchestration
    without triggering actual file generation or Matplotlib internals.
    """
    mock_timeline = MagicMock(return_value="mocked/timeline.png")
    mock_top10 = MagicMock(return_value="mocked/top10.csv")
    
    monkeypatch.setattr(visualize, "plot_team_probability_timeline", mock_timeline)
    monkeypatch.setattr(visualize, "generate_top_10_by_snapshot", mock_top10)
    
    return {
        "plot_timeline": mock_timeline,
        "generate_top10": mock_top10,
    }


# =====================================================================
# 1. VALID CLI FLAGS EXECUTION TESTS
# =====================================================================

def test_cli_timeline_flag_only(monkeypatch, mock_viz_actions):
    """Verify --timeline creates PNG, does not request top-10, and runs successfully."""
    monkeypatch.setattr(sys, "argv", ["visualize.py", "--edition", "wc2026", "--timeline"])

    # main() finishes cleanly without exception by exiting with code 0 (implicit standard behaviour)
    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    mock_viz_actions["plot_timeline"].assert_called_once_with(edition="wc2026", teams=None)
    mock_viz_actions["generate_top10"].assert_not_called()


def test_cli_top10_flag_only(monkeypatch, mock_viz_actions):
    """Verify --top10 creates CSV, does not request timeline chart, and runs successfully."""
    monkeypatch.setattr(sys, "argv", ["visualize.py", "--edition", "wc2026", "--top10"])

    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    mock_viz_actions["generate_top10"].assert_called_once_with(edition="wc2026")
    mock_viz_actions["plot_timeline"].assert_not_called()


def test_cli_all_flag_orchestrates_both(monkeypatch, mock_viz_actions):
    """Verify --all flags trigger execution loops for both CSV tables and PNG charts."""
    monkeypatch.setattr(sys, "argv", ["visualize.py", "--edition", "wc2026", "--all"])

    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    mock_viz_actions["plot_timeline"].assert_called_once_with(edition="wc2026", teams=None)
    mock_viz_actions["generate_top10"].assert_called_once_with(edition="wc2026")


def test_cli_timeline_with_custom_teams_list(monkeypatch, mock_viz_actions):
    """Verify --teams parses input arrays properly and routes them down cleanly."""
    monkeypatch.setattr(
        sys, 
        "argv", 
        ["visualize.py", "--edition", "wc2026", "--timeline", "--teams", "Spain", "Argentina"]
    )

    try:
        main()
    except SystemExit as e:
        assert e.code == 0

    mock_viz_actions["plot_timeline"].assert_called_once_with(
        edition="wc2026", 
        teams=["Spain", "Argentina"]
    )


# =====================================================================
# 2. INVALID CLI CONSTRAINTS & PARSER ERROR TESTS
# =====================================================================

def test_cli_missing_action_flags_raises_parser_error(monkeypatch, mock_viz_actions):
    """Verify parser error if none of --timeline, --top10, or --all are supplied."""
    monkeypatch.setattr(sys, "argv", ["visualize.py", "--edition", "wc2026"])

    # Argument parser failures trigger a SystemExit code of 2 standardly
    with pytest.raises(SystemExit) as exc_info:
        main()
        
    assert exc_info.value.code == 2


def test_cli_teams_flag_without_matching_action_fails(monkeypatch, mock_viz_actions):
    """Verify parser error when adding --teams parameter without matching generation scope context."""
    monkeypatch.setattr(
        sys, 
        "argv", 
        ["visualize.py", "--edition", "wc2026", "--teams", "Spain", "Argentina"]
    )

    with pytest.raises(SystemExit) as exc_info:
        main()
        
    assert exc_info.value.code == 2
