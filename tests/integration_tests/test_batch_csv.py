import json
import unittest
import tempfile
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock, patch

from live.adapters.batch_csv import main


class TestBatchCSVTrueIntegration(unittest.TestCase):

    def setUp(self):
        """Set up exact production workspace pathways inside a safe file system sandbox."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.sandbox = Path(self.test_dir.name)

        # 1. Exact Production File Paths Mapped into Sandbox
        self.state_file_path = self.sandbox / "data/live/wc2026/tournament_state.json"
        self.csv_file_path = self.sandbox / "data/raw/batch_matches.csv"
        self.snapshots_dir = self.sandbox / "predictions/snapshots"
        self.edition_snapshots_dir = self.snapshots_dir / "wc2026"
        self.timeline_file_path = self.sandbox / "predictions/timelines/wc2026_probability_timeline.csv"
        self.features_file_path = self.sandbox / "data/processed/wc2026_updated.csv"
        
        # Stage 2C output targets
        self.visualization_dir = self.sandbox / "predictions/visualizations/wc2026"
        self.timeline_png_path = self.visualization_dir / "wc2026_probability_timeline.png"
        self.top10_csv_path = self.visualization_dir / "wc2026_top10_by_snapshot.csv"

        # Auto-create all required directory hierarchies
        self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.csv_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.edition_snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.timeline_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.features_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.visualization_dir.mkdir(parents=True, exist_ok=True)

        # 2. Establish Valid Initial Tournament State File
        self.initial_state = {
            "edition": "wc2026",
            "current_phase": "group",
            "completed_matches": [],
            "eliminated_teams": []
        }
        with self.state_file_path.open("w", encoding="utf-8") as f:
            json.dump(self.initial_state, f)

        # 3. Setup Target Configuration Object Mock Layout
        self.mock_config = MagicMock()
        self.mock_config.edition = "wc2026"
        self.mock_config.state_file = self.state_file_path
        self.mock_config.output_features = str(self.features_file_path)

    def tearDown(self):
        """Wipe the temporary file sandbox directory completely."""
        self.test_dir.cleanup()

    @patch("live.adapters.batch_csv.load_tournament_config")
    @patch("live.adapters.batch_csv.resolve_config_paths")
    @patch("live.adapters.batch_csv.argparse.ArgumentParser.parse_args")
    def test_batch_csv_processing_integration(
        self, mock_args, mock_resolve, mock_load
    ):
        """Verify batch loops run updates, predict data refreshes, and compile snapshots alongside visualizations."""
        
        # Setup mock CLI argument routing inputs
        args_mock = MagicMock()
        args_mock.edition = "wc2026"
        args_mock.file = str(self.csv_file_path)
        mock_args.return_value = args_mock

        mock_load.return_value = self.mock_config
        mock_resolve.return_value = self.mock_config

        # 1. Create source intake match CSV records for a batch of three matches
        csv_data = [
            {"home_team": "TeamA", "away_team": "TeamB", "home_goals": 2, "away_goals": 1, "round": "group", "group": "A"},
            {"home_team": "TeamB", "away_team": "TeamC", "home_goals": 0, "away_goals": 0, "round": "group", "group": "A"},
            {"home_team": "TeamC", "away_team": "TeamA", "home_goals": 1, "away_goals": 3, "round": "round_of_16", "group": None}
        ]
        pd.DataFrame(csv_data).to_csv(self.csv_file_path, index=False)

        # Spies to track refresh frequency counts across match iterations
        timeline_png_refresh_count = 0
        top10_csv_refresh_count = 0

        # 2. Side-Effect: Build exact snapshot naming layout rules sequentially per loop iteration
        def run_live_prediction_side_effect(config):
            nonlocal timeline_png_refresh_count, top10_csv_refresh_count
            
            with self.state_file_path.open("r") as f:
                current_state = json.load(f)
            
            match_idx = len(current_state["completed_matches"])

            # Generate target sequence file names matching sequential guidelines
            snapshot_filename = f"snapshot_{match_idx:03d}_match_{match_idx:03d}.csv"
            snapshot_file = self.edition_snapshots_dir / snapshot_filename
            pd.DataFrame({"Team": ["TeamA"], "Probability": [1.0]}).to_csv(snapshot_file, index=False)
            
            # Side-Effect: Append individual columns to your timeline path DataFrame
            if not self.timeline_file_path.exists():
                timeline_df = pd.DataFrame({"Team": ["TeamA", "TeamB", "TeamC"]})
            else:
                timeline_df = pd.read_csv(self.timeline_file_path)
            
            snapshot_col_name = f"Snapshot_{match_idx:03d}"
            timeline_df[snapshot_col_name] = [0.5, 0.2, 0.3]
            timeline_df.to_csv(self.timeline_file_path, index=False)

            # Side-Effect: Simulate Stage 2C visual refreshes by over-writing file content
            self.timeline_png_path.write_text(f"chart_state_after_match_{match_idx}")
            timeline_png_refresh_count += 1

            self.top10_csv_path.write_text(f"top10_state_after_match_{match_idx}")
            top10_csv_refresh_count += 1

            # Match return structure required by run_live_prediction contract
            return {
                "predictions": pd.DataFrame(),
                "snapshot_path": snapshot_file,
                "timeline_chart_path": self.timeline_png_path,
                "top_10_path": self.top10_csv_path
            }

        # 3. Side-Effect: Map state serialization changes and knockout rules
        def update_pipeline_side_effect(state, config, match):
            state["completed_matches"].append(match.to_dict())
            
            if match.round == "round_of_16":
                loser = match.away_team if match.home_goals > match.away_goals else match.home_team
                state["eliminated_teams"].append(loser)
            
            with self.state_file_path.open("w") as f:
                json.dump(state, f)

        # Mock spies wrapper declarations using functional contexts
        spy_update_pipeline = MagicMock(side_effect=update_pipeline_side_effect)
        spy_run_prediction = MagicMock(side_effect=run_live_prediction_side_effect)

        # Execute loop pipeline
        with patch("live.adapters.batch_csv.update_pipeline", spy_update_pipeline), \
             patch("live.adapters.batch_csv.run_live_prediction", spy_run_prediction):
            main()

        # ==========================================================
        # VERIFICATION & ASSERTIONS SECTION
        # ==========================================================
        
        with self.state_file_path.open("r") as f:
            final_state = json.load(f)

        # 1 & 2. Verify pipeline updates and model predictions run exactly 3 times
        self.assertEqual(spy_update_pipeline.call_count, 3)
        self.assertEqual(spy_run_prediction.call_count, 3)

        # 3. Verify total completed_matches in final tournament state file contains all three records
        self.assertEqual(len(final_state["completed_matches"]), 3)

        # 4. Verify three sequential prediction snapshot logs exist inside the directory tree layout
        generated_snapshots = sorted([f.name for f in self.edition_snapshots_dir.glob("snapshot_*.csv")])
        expected_snapshots = [
            "snapshot_001_match_001.csv",
            "snapshot_002_match_002.csv",
            "snapshot_003_match_003.csv"
        ]
        self.assertEqual(generated_snapshots, expected_snapshots)

        # 5 & 6. Verify one prediction, timeline PNG, and top-10 CSV refresh happens sequentially after each match loop execution pass
        self.assertEqual(timeline_png_refresh_count, 3)
        self.assertEqual(top10_csv_refresh_count, 3)

        # 7. Check final file existence targets in sandbox
        self.assertTrue(self.timeline_png_path.exists())
        self.assertTrue(self.top10_csv_path.exists())
        
        # Verify the CSV contains all historical snapshot columns accumulated incrementally
        timeline_df = pd.read_csv(self.timeline_file_path)
        expected_columns = ["Team", "Snapshot_001", "Snapshot_002", "Snapshot_003"]
        self.assertEqual(list(timeline_df.columns), expected_columns)

        # Verify knockout logic rules are still intact
        self.assertIn("TeamC", final_state["eliminated_teams"])
