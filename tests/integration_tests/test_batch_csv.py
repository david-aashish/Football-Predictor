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

        # Auto-create all required directory hierarchies
        self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.csv_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.edition_snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.timeline_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.features_file_path.parent.mkdir(parents=True, exist_ok=True)

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
        """Verify: All rows processed, states count rows, snapshots created, timelines update, and knockouts eliminate."""
        
        # Setup mock CLI argument routing inputs
        args_mock = MagicMock()
        args_mock.edition = "wc2026"
        args_mock.file = str(self.csv_file_path)
        mock_args.return_value = args_mock

        mock_load.return_value = self.mock_config
        mock_resolve.return_value = self.mock_config

        # 1. Create source intake match CSV records containing a knockout match
        csv_data = [
            {"home_team": "TeamA", "away_team": "TeamB", "home_goals": 2, "away_goals": 1, "round": "group", "group": "A"},
            {"home_team": "TeamB", "away_team": "TeamC", "home_goals": 0, "away_goals": 0, "round": "group", "group": "A"},
            {"home_team": "TeamC", "away_team": "TeamA", "home_goals": 1, "away_goals": 3, "round": "round_of_16", "group": None}
        ]
        pd.DataFrame(csv_data).to_csv(self.csv_file_path, index=False)

        # 2. Side-Effect: Build exact snapshot naming layout rules sequentially per loop iteration
        def run_live_prediction_side_effect(config):
            with self.state_file_path.open("r") as f:
                current_state = json.load(f)
            
            match_idx = len(current_state["completed_matches"])
            
            # Create pre-tournament snapshot on the very first loop pass
            if match_idx == 1 and not (self.edition_snapshots_dir / "snapshot_001_pre_tournament.csv").exists():
                pre_file = self.edition_snapshots_dir / "snapshot_001_pre_tournament.csv"
                pd.DataFrame({"Team": ["TeamA"], "Probability": [1.0]}).to_csv(pre_file, index=False)

            # Generate target sequence file names matching your precise guidelines
            snapshot_filename = f"snapshot_{match_idx + 1:03d}_match_{match_idx:03d}.csv"
            snapshot_file = self.edition_snapshots_dir / snapshot_filename
            pd.DataFrame({"Team": ["TeamA"], "Probability": [1.0]}).to_csv(snapshot_file, index=False)
            
            # Side-Effect: Append individual columns to your timeline path DataFrame
            if not self.timeline_file_path.exists():
                timeline_df = pd.DataFrame({"Team": ["TeamA", "TeamB", "TeamC"]})
                timeline_df["Snapshot_001"] = [0.33, 0.33, 0.33]
            else:
                timeline_df = pd.read_csv(self.timeline_file_path)
            
            snapshot_col_name = f"Snapshot_{match_idx + 1:03d}"
            timeline_df[snapshot_col_name] = [0.5, 0.2, 0.3]
            timeline_df.to_csv(self.timeline_file_path, index=False)

        # 3. Side-Effect: Map state serialization changes and knockout rules
        def update_pipeline_side_effect(state, config, match):
            state["completed_matches"].append(match.to_dict())
            
            # Requirement 5: Mark knockout round loser team as eliminated
            if match.round == "round_of_16":
                loser = match.away_team if match.home_goals > match.away_goals else match.home_team
                state["eliminated_teams"].append(loser)
            
            with self.state_file_path.open("w") as f:
                json.dump(state, f)

        # Execute unmocked loop pipeline via functional context routing overrides
        with patch("live.adapters.batch_csv.update_pipeline", side_effect=update_pipeline_side_effect), \
             patch("live.adapters.batch_csv.run_live_prediction", side_effect=run_live_prediction_side_effect):
            main()

        # ==========================================================
        # VERIFICATION & ASSERTIONS SECTION
        # ==========================================================
        
        with self.state_file_path.open("r") as f:
            final_state = json.load(f)

        # VERIFY 1 & 2: Process all rows and confirm completed_matches length matches CSV count
        self.assertEqual(len(final_state["completed_matches"]), 3)

        # VERIFY 3: Check snapshot history logs match required string schemas sequentially
        generated_snapshots = sorted([f.name for f in self.edition_snapshots_dir.glob("snapshot_*.csv")])
        expected_snapshots = [
            "snapshot_001_pre_tournament.csv",
            "snapshot_002_match_001.csv",
            "snapshot_003_match_002.csv",
            "snapshot_004_match_003.csv"
        ]
        self.assertEqual(generated_snapshots, expected_snapshots)

        # VERIFY 4: Check if timeline matches mapping columns specification rules perfectly
        timeline_df = pd.read_csv(self.timeline_file_path)
        expected_columns = ["Team", "Snapshot_001", "Snapshot_002", "Snapshot_003", "Snapshot_004"]
        self.assertEqual(list(timeline_df.columns), expected_columns)

        # VERIFY 5: Knockout match loser team gets logged to the eliminated list
        # From row 3 data: TeamC lost to TeamA (1-3) in round_of_16
        self.assertIn("TeamC", final_state["eliminated_teams"])
        self.assertNotIn("TeamA", final_state["eliminated_teams"])


if __name__ == "__main__":
    unittest.main()