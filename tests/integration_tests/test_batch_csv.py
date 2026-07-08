import unittest
import tempfile
import json
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock, patch

from live.adapters.batch_csv import main


class TestBatchCSVIntegration(unittest.TestCase):

    def setUp(self):
        """Set up a temporary sandbox directory for tracking CSV and JSON state updates."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.test_dir.name)

        # Paths inside our sandbox
        self.state_file_path = self.temp_path / "tournament.json"
        self.csv_file_path = self.temp_path / "matches.csv"

        # Mock standard state structure
        self.initial_state = {
            "teams": {
                "TeamA": {"elo": 1500.0},
                "TeamB": {"elo": 1500.0},
                "TeamC": {"elo": 1500.0}
            },
            "completed_matches": []
        }

        # Write initial JSON state file to sandbox
        with self.state_file_path.open("w", encoding="utf-8") as handle:
            json.dump(self.initial_state, handle)

    def tearDown(self):
        """Wipe the temporary file directory completely."""
        self.test_dir.cleanup()

    @patch("live.adapters.batch_csv.update_pipeline")
    @patch("live.adapters.batch_csv.load_tournament_config")
    @patch("live.adapters.batch_csv.resolve_config_paths")
    @patch("live.adapters.batch_csv.argparse.ArgumentParser.parse_args")
    def test_batch_csv_processing_integration(
        self, mock_args, mock_resolve, mock_load, mock_pipeline
    ):
        """Verify CSV reading, parsing of all rows, state reloading, and duplicate management flow."""
        
        # 1. Setup mock CLI inputs matching the sandbox files
        args_mock = MagicMock()
        args_mock.edition = "wc2026"
        args_mock.file = str(self.csv_file_path)
        mock_args.return_value = args_mock

        # 2. Setup mock tournament configuration paths
        mock_config = MagicMock()
        mock_config.state_file = self.state_file_path
        mock_load.return_value = mock_config
        mock_resolve.return_value = mock_config

        # 3. Create a valid match csv data file with a mix of valid records and a duplicate match
        # (Row 1 and Row 3 are matching duplicates)
        csv_data = [
            {"home_team": "TeamA", "away_team": "TeamB", "home_goals": 2, "away_goals": 1, "round": "group", "group": "A"},
            {"home_team": "TeamB", "away_team": "TeamC", "home_goals": 0, "away_goals": 0, "round": "group", "group": "A"},
            {"home_team": "TeamA", "away_team": "TeamB", "home_goals": 2, "away_goals": 1, "round": "group", "group": "A"}
        ]
        pd.DataFrame(csv_data).to_csv(self.csv_file_path, index=False)

        # 4. Simulate how the downstream pipeline handles normal processing vs duplicate handling
        # Since update_pipeline loads/saves state, we can simulate state mutation on the first two, 
        # and throw a ValueError on the third row to verify duplicate checking.
        def pipeline_side_effect(state, match, config):
            if match.home_team == "TeamA" and match.away_team == "TeamB" and len(state["completed_matches"]) > 0:
                raise ValueError("Match already processed.")
            # Simulate a valid save by modifying our sandbox state file directly
            state["completed_matches"].append(match.to_dict())
            with open(config.state_file, "w") as f:
                json.dump(state, f)
            return state

        mock_pipeline.side_effect = pipeline_side_effect

        # 5. Run the batch tool via an intentional exception capture block
        # We catch the ValueError to verify that duplicate detection actively stops the loop
        with self.assertRaises(ValueError) as context:
            main()

        # ASSERTION 1 & 3: READS CSV & DUPLICATE DETECTION WORKS
        # The fact that the script crashed on the ValueError proves it successfully processed 
        # up to row 3 and hit the pipeline's duplicate match threshold.
        self.assertEqual(str(context.exception), "Match already processed.")

        # ASSERTION 2: PROCESSES ALL ROWS (Up until the duplicate break point)
        # Verify update_pipeline was called exactly 3 times (Row 1, Row 2, and Row 3 which failed)
        self.assertEqual(mock_pipeline.call_count, 3)

        # Confirm the first match object parameters were parsed correctly into the MatchResult model instance
        first_call_match = mock_pipeline.call_args_list[0][1]["match"]
        self.assertEqual(first_call_match.home_team, "TeamA")
        self.assertEqual(first_call_match.home_goals, 2)

        # ASSERTION 4: UPDATED STATE SAVED
        # Read the file from disk to check if row 1 and row 2 changes successfully persisted to the JSON file
        with self.state_file_path.open("r", encoding="utf-8") as handle:
            saved_state = json.load(handle)

        self.assertEqual(len(saved_state["completed_matches"]), 2)
        self.assertEqual(saved_state["completed_matches"][0]["home_team"], "TeamA")
        self.assertEqual(saved_state["completed_matches"][1]["home_team"], "TeamB")


if __name__ == "__main__":
    unittest.main()