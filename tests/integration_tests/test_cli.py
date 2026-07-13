from __future__ import annotations

from unittest.mock import MagicMock, patch
import pandas as pd
import pytest

from live.adapters.cli import main, run_live_prediction


@pytest.fixture
def mock_dependencies():
    """Fixture to mock all heavy infrastructure, file, ML model, and visualization dependencies."""
    with (
        patch("live.adapters.cli.initialize") as mock_init,
        patch("live.adapters.cli.load_tournament_config") as mock_load_config,
        patch("live.adapters.cli.resolve_config_paths") as mock_resolve_paths,
        patch("live.adapters.cli.reset_snapshots") as mock_reset_snapshots,
        patch("live.adapters.cli.predict_dataset") as mock_predict,
        patch("live.adapters.cli.apply_live_probability_rules") as mock_apply_rules,
        patch("live.adapters.cli.load_state") as mock_load_state,
        patch("live.adapters.cli.save_prediction_snapshot") as mock_save_snapshot,
        patch("live.adapters.cli.build_probability_timeline") as mock_build_timeline,
        patch("live.adapters.cli.update_pipeline") as mock_update_pipeline,
        patch("live.adapters.cli.MatchResult") as mock_match_result,
        patch("live.adapters.cli.plot_team_probability_timeline") as mock_plot_timeline,
        patch("live.adapters.cli.generate_top_10_by_snapshot") as mock_gen_top10,
    ):
        # Setup configuration mock attributes
        mock_config = MagicMock()
        mock_config.edition = "wc2026"
        mock_config.state_file = "data/live/wc2026/tournament_state.json"
        mock_config.output_features = "data/processed/wc2026_updated.csv"
        mock_resolve_paths.return_value = mock_config
        mock_load_config.return_value = mock_config

        # Setup DataFrame mock for predictions data frame
        mock_df = MagicMock(spec=pd.DataFrame)
        mock_df.head.return_value = mock_df
        mock_df.to_string.return_value = "Mocked Top 10 DataFrame String Output"
        mock_predict.return_value = mock_df
        mock_apply_rules.return_value = mock_df

        # Default string path values for visualization mocks
        mock_plot_timeline.return_value = "predictions/visualizations/wc2026/wc2026_probability_timeline.png"
        mock_gen_top10.return_value = "predictions/visualizations/wc2026/wc2026_top10_by_snapshot.csv"

        yield {
            "initialize": mock_init,
            "reset_snapshots": mock_reset_snapshots,
            "predict_dataset": mock_predict,
            "apply_live_probability_rules": mock_apply_rules,
            "load_state": mock_load_state,
            "save_prediction_snapshot": mock_save_snapshot,
            "build_probability_timeline": mock_build_timeline,
            "update_pipeline": mock_update_pipeline,
            "match_result": mock_match_result,
            "plot_team_probability_timeline": mock_plot_timeline,
            "generate_top_10_by_snapshot": mock_gen_top10,
            "config": mock_config,
            "predictions_df": mock_df,
        }


# =====================================================================
# 1. CORE PIPELINE FUNCTION: run_live_prediction()
# =====================================================================

def test_run_live_prediction_returns_and_calls_stage_2c(mock_dependencies):
    """Verify run_live_prediction returns the 4 expected outputs and triggers ML/Viz functions."""
    deps = mock_dependencies
    config = deps["config"]

    # Explicit stub return paths
    deps["save_prediction_snapshot"].return_value = "snapshots/wc2026/snapshot_001.csv"
    deps["plot_team_probability_timeline"].return_value = "visualizations/wc2026/timeline.png"
    deps["generate_top_10_by_snapshot"].return_value = "visualizations/wc2026/top10.csv"

    # Execute target logic directly
    outputs = run_live_prediction(config)

    # Validate output dictionary payload requirements
    assert isinstance(outputs, dict)
    assert outputs["predictions"] == deps["predictions_df"]
    assert outputs["snapshot_path"] == "snapshots/wc2026/snapshot_001.csv"
    assert outputs["timeline_chart_path"] == "visualizations/wc2026/timeline.png"
    assert outputs["top_10_path"] == "visualizations/wc2026/top10.csv"

    # Validate orchestration triggers
    deps["predict_dataset"].assert_called_once_with(config.output_features, model_name="xgboost")
    deps["apply_live_probability_rules"].assert_called_once_with(deps["predictions_df"], config.state_file)
    deps["save_prediction_snapshot"].assert_called_once()
    deps["build_probability_timeline"].assert_called_once_with(edition="wc2026")
    deps["plot_team_probability_timeline"].assert_called_once_with(edition="wc2026")
    deps["generate_top_10_by_snapshot"].assert_called_once_with(edition="wc2026")


# =====================================================================
# 2. CLI SUB-COMMAND ROUTE: --init
# =====================================================================

def test_cli_init_command_flow(mock_dependencies):
    """Verify --init creates/resets state, outputs pre-tournament snapshots, timelines, and Stage 2C charts."""
    deps = mock_dependencies
    
    # Configure snapshots paths behavior
    deps["save_prediction_snapshot"].return_value = "snapshots/wc2026/snapshot_001_pre_tournament.csv"
    
    # Mock behavior of building the initial timeline dataframe
    def side_effect_build_timeline(edition):
        df = pd.DataFrame(columns=["Team", "snapshot_001_pre_tournament"])
        df.to_csv(f"data/{edition}_timeline.csv", index=False)

    deps["build_probability_timeline"].side_effect = side_effect_build_timeline

    # Trigger CLI with --init flag
    test_args = ["cli.py", "--edition", "wc2026", "--init"]
    with (
        patch("sys.argv", test_args),
        patch("os.path.exists", return_value=True),
        patch("pandas.DataFrame.to_csv") as mock_to_csv
    ):
        main()

    # 1. Verify initialization lifecycle triggers and output resets
    deps["initialize"].assert_called_once_with("wc2026")
    deps["reset_snapshots"].assert_called_once_with("wc2026")

    # 2. Verify pre-tournament snapshot logic
    deps["save_prediction_snapshot"].assert_called_once()
    assert deps["save_prediction_snapshot"].return_value.endswith("snapshot_001_pre_tournament.csv")

    # 3. Verify initial timeline creation
    deps["build_probability_timeline"].assert_called_once_with(edition="wc2026")
    mock_to_csv.assert_called_once()

    # 4. Verify initial Stage 2C visualization output tracks generated
    deps["plot_team_probability_timeline"].assert_called_once_with(edition="wc2026")
    deps["generate_top_10_by_snapshot"].assert_called_once_with(edition="wc2026")


# =====================================================================
# 3. CLI SUB-COMMAND ROUTE: --result
# =====================================================================

def test_cli_result_command_flow(mock_dependencies):
    """Verify --result processes matches, produces next snapshots, updates timeline tracking, and refreshes viz outputs."""
    deps = mock_dependencies

    # Setup specific mock state simulating an incoming round of 16 knockout match
    mock_state = {
        "edition": "wc2026",
        "current_phase": "knockout",
        "completed_matches": [{"home": "TeamA", "away": "TeamB", "home_goals": 2, "away_goals": 1}],
        "eliminated_teams": ["TeamB"],
    }
    deps["load_state"].return_value = mock_state
    deps["save_prediction_snapshot"].return_value = "snapshots/wc2026/snapshot_002_match_001.csv"

    # Simulate timeline update containing the new tracking columns
    def side_effect_update_timeline(edition):
        df = pd.DataFrame({
            "Team": ["TeamA", "TeamB"],
            "snapshot_001_pre_tournament": [0.50, 0.50],
            "snapshot_002_match_001": [0.85, 0.00]
        })
        df.to_csv(f"data/{edition}_timeline.csv", index=False)

    deps["build_probability_timeline"].side_effect = side_effect_update_timeline

    # Trigger CLI with --result flag for knockout match processing
    test_args = [
        "cli.py",
        "--edition", "wc2026",
        "--result",
        "--home", "TeamA",
        "--away", "TeamB",
        "--home-goals", "2",
        "--away-goals", "1",
        "--round", "r16"
    ]
    
    with (
        patch("sys.argv", test_args),
        patch("pandas.DataFrame.to_csv") as mock_to_csv
    ):
        main()

    # 1. Verify match context compilation and processing execution
    deps["match_result"].assert_called_once_with(
        home_team="TeamA",
        away_team="TeamB",
        home_goals=2,
        away_goals=1,
        round="r16",
        group=None
    )
    deps["update_pipeline"].assert_called_once_with(
        state=mock_state,
        config=deps["config"],
        match=deps["match_result"].return_value
    )

    # 2. Verify dataset calculations re-run live predictions
    deps["predict_dataset"].assert_called_once()

    # 3. Verify the step generated the accurate chronological snapshot
    assert deps["save_prediction_snapshot"].return_value.endswith("snapshot_002_match_001.csv")

    # 4. Verify timeline file modifications for new snapshot columns
    deps["build_probability_timeline"].assert_called_once_with(edition="wc2026")
    mock_to_csv.assert_called_once()

    # 5. Verify visualization charts (PNG images) updated to capture current progression
    deps["plot_team_probability_timeline"].assert_called_once_with(edition="wc2026")

    # 6. Verify top-10 favorite tracking lists updated into output CSV files
    deps["generate_top_10_by_snapshot"].assert_called_once_with(edition="wc2026")

    # Core state data validation assertions
    assert len(mock_state["completed_matches"]) == 1
    assert "TeamB" in mock_state["eliminated_teams"]
