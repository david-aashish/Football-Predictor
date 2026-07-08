import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import pandas as pd

from live.build_features import (
    build_feature_dataset,
    save_feature_dataset,
    build_and_save,
)


class TestBuildFeatures(unittest.TestCase):

    def setUp(self):
        """Set up mock configurations, tournament states, and sample dataframes."""
        # Mocking config file properties
        self.mock_config = MagicMock()
        self.mock_config.baseline_dataset = "mock_baseline.csv"
        self.mock_config.output_features = Path("mock_output/features.csv")

        # Mocking the dictionary state structure matching empty_team_state layout
        self.mock_state = {
            "teams": {
                "TeamA": {
                    "elo": 1620.5,
                    "eliminated": False,
                    "tournament_stats": {
                        "matches": 3, "wins": 2, "draws": 1, "losses": 0,
                        "goals_for": 6, "goals_against": 2, "goal_difference": 4, "points": 7
                    },
                    "form_last_n": [{"result": "win", "goals_for": 2, "goals_against": 0}]
                },
                "TeamB": {
                    "elo": 1410.0,
                    "eliminated": True,
                    "tournament_stats": {
                        "matches": 3, "wins": 0, "draws": 1, "losses": 2,
                        "goals_for": 1, "goals_against": 5, "goal_difference": -4, "points": 1
                    },
                    "form_last_n": [{"result": "loss", "goals_for": 0, "goals_against": 2}]
                }
            }
        }

        # Creating a baseline pandas DataFrame structure
        self.mock_baseline_df = pd.DataFrame([
            {"Team": "TeamA", "Elo_Rating": "1500.0"},
            {"Team": "TeamB", "Elo_Rating": "1500.0"},
            {"Team": "TeamC", "Elo_Rating": "1200.0"}  # TeamC tests the team missing from state path
        ])

        # Expected return dictionary structure for form_summary
        self.mock_form_a = {
            "win_rate": 1.0,
            "goals_for_per_game": 2.0,
            "goals_against_per_game": 0.0
        }
        self.mock_form_b = {
            "win_rate": 0.0,
            "goals_for_per_game": 0.0,
            "goals_against_per_game": 2.0
        }

    @patch("live.build_features.form_summary")
    @patch("live.build_features.load_state")
    @patch("live.build_features.pd.read_csv")
    def test_build_feature_dataset(self, mock_read_csv, mock_load_state, mock_form_summary):
        """Verify Elo update, elimination mapping, live stats copying, and missing team handling."""
        # Inject standard returns
        mock_read_csv.return_value = self.mock_baseline_df
        mock_load_state.return_value = self.mock_state
        
        # Guide form_summary execution values for different iterations
        mock_form_summary.side_effect = [self.mock_form_a, self.mock_form_b]

        # Execute data assembly pipeline
        result_df = build_feature_dataset(self.mock_config)

        # Ensure we returned a pandas DataFrame type
        self.assertIsInstance(result_df, pd.DataFrame)

        # Set index to Team name to query cell metrics cleanly
        indexed_df = result_df.set_index("Team")

        # 1. Elo updated check
        self.assertEqual(indexed_df.loc["TeamA", "Elo_Rating"], 1620.5)
        self.assertEqual(indexed_df.loc["TeamB", "Elo_Rating"], 1410.0)

        # 2. Elimination column updated check (must be cast to int 0 or 1)
        self.assertEqual(indexed_df.loc["TeamA", "Is_Eliminated"], 0)
        self.assertEqual(indexed_df.loc["TeamB", "Is_Eliminated"], 1)

        # 3. Live tournament stats and form metrics copied check
        self.assertEqual(indexed_df.loc["TeamA", "WC_Matches"], 3)
        self.assertEqual(indexed_df.loc["TeamA", "WC_Points"], 7)
        self.assertEqual(indexed_df.loc["TeamA", "WC_Goal_Difference"], 4)
        self.assertEqual(indexed_df.loc["TeamA", "Live_Form_Win_Rate"], 1.0)

        self.assertEqual(indexed_df.loc["TeamB", "WC_Losses"], 2)
        self.assertEqual(indexed_df.loc["TeamB", "WC_Goals_Against"], 5)
        self.assertEqual(indexed_df.loc["TeamB", "Live_Form_GA_Per_Game"], 2.0)

        # 4. Edge-case safety: Missing team (TeamC) skips logic and preserves baseline data types
        self.assertEqual(indexed_df.loc["TeamC", "Elo_Rating"], 1200.0)
        self.assertNotIn("Is_Eliminated", indexed_df.columns[indexed_df.loc[["TeamC"]].isna().any()])

    @patch("live.build_features.Path.mkdir")
    @patch("live.build_features.pd.DataFrame.to_csv")
    def test_save_feature_dataset(self, mock_to_csv, mock_mkdir):
        """Verify that an updated CSV path is targeted and folder creation is requested."""
        df_sample = pd.DataFrame([{"Team": "TeamA"}])

        output_path = save_feature_dataset(df_sample, self.mock_config)

        # Verify output matches the configuration parameter destination
        self.assertEqual(output_path, self.mock_config.output_features)
        
        # Verify parent directory creation rules executed
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        
        # Verify pandas file writer was called with correct configurations
        mock_to_csv.assert_called_once_with(self.mock_config.output_features, index=False)

    @patch("live.build_features.save_feature_dataset")
    @patch("live.build_features.build_feature_dataset")
    def test_build_and_save_convenience_function(self, mock_build, mock_save):
        """Verify build_and_save coordinates the pipeline subroutines in sequential order."""
        mock_build.return_value = "mock_built_df"
        mock_save.return_value = Path("final_path.csv")

        final_path = build_and_save(self.mock_config)

        # Verify steps coordinate sequentially
        mock_build.assert_called_once_with(self.mock_config)
        mock_save.assert_called_once_with("mock_built_df", self.mock_config)
        self.assertEqual(final_path, Path("final_path.csv"))


if __name__ == "__main__":
    unittest.main()