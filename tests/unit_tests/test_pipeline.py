import unittest
from unittest.mock import MagicMock, patch

from live.pipeline import update_pipeline


class TestUpdatePipeline(unittest.TestCase):

    def setUp(self):
        """Set up mock structures for state, matches, and configurations."""
        # Baseline minimal state
        self.state = {
            "teams": {
                "TeamA": {"elo": 1500.0, "tournament_stats": {}, "form_last_n": []},
                "TeamB": {"elo": 1500.0, "tournament_stats": {}, "form_last_n": []},
            },
            "completed_matches": [],
            "eliminated_teams": [],
            "current_phase": "group"
        }

        # Mocking the configuration file
        self.mock_config = MagicMock()
        self.mock_config.form_window = 5

        # Mocking the match object data structure
        self.mock_match = MagicMock()
        self.mock_match.home_team = "TeamA"
        self.mock_match.away_team = "TeamB"
        self.mock_match.home_goals = 2
        self.mock_match.away_goals = 1
        self.mock_match.to_dict.return_value = {
            "home_team": "TeamA",
            "away_team": "TeamB",
            "home_goals": 2,
            "away_goals": 1,
            "round": "Group A",
            "group": "A"
        }

    @patch("live.pipeline.match_already_recorded", return_value=True)
    @patch("live.pipeline.validate_teams_in_state")
    def test_duplicate_match_raises_error(self, mock_validate, mock_recorded):
        """Verify that a duplicate match profile short-circuits the pipeline and triggers an exception."""
        with self.assertRaises(ValueError) as context:
            update_pipeline(self.state, self.mock_match, self.mock_config)
        
        self.assertEqual(str(context.exception), "Match already processed.")

        mock_validate.assert_called_once_with(self.state, "TeamA", "TeamB")
        mock_recorded.assert_called_once_with(self.state, self.mock_match.to_dict())

    @patch("live.pipeline.build_and_save")
    @patch("live.pipeline.save_state")
    @patch("live.pipeline.update_phase")
    @patch("live.pipeline.apply_elimination")
    @patch("live.pipeline.update_form")
    @patch("live.pipeline.update_tournament_stats")
    @patch("live.pipeline.update_elo")
    @patch("live.pipeline.match_already_recorded", return_value=False)
    @patch("live.pipeline.validate_teams_in_state")
    def test_pipeline_execution_flow(
        self, mock_validate, mock_recorded, mock_elo, mock_stats, 
        mock_form, mock_elim, mock_phase, mock_save, mock_build
    ):
        """Verify that matches append cleanly and subsequent helper modules execute in order."""
        
        # Setup specific returns for step-by-step pipeline mutation checks
        mock_elo.return_value = {"teams": "updated_elo"}
        mock_stats.return_value = {"teams": "updated_stats"}
        mock_form.return_value = {"teams": "updated_form", "completed_matches": []}
        mock_elim.return_value = {"teams": "updated_elim", "completed_matches": []}
        
        # We need a dictionary containing completed_matches for the append function to execute on
        final_mock_state = {
            "teams": "final_mock_state",
            "completed_matches": []
        }
        mock_phase.return_value = final_mock_state

        # Execute the pipeline orchestrator
        result = update_pipeline(self.state, self.mock_match, self.mock_config)

        # 1. Verification of validation functions
        mock_validate.assert_called_once_with(self.state, "TeamA", "TeamB")
        mock_recorded.assert_called_once_with(self.state, self.mock_match.to_dict())

        # 2. Verification that Elo updates are called
        mock_elo.assert_called_once_with(self.state, self.mock_match, self.mock_config)

        # 3. Verification that Tournament Stats updates are called
        mock_stats.assert_called_once_with(mock_elo.return_value, self.mock_match)

        # 4. Verification that Team Recent Form updates are called
        mock_form.assert_called_once_with(mock_stats.return_value, self.mock_match, self.mock_config.form_window)

        # 5. Verification that the completed match appends correctly into historical array logs
        # This checks the inline array logic inside update_pipeline
        self.assertIn(self.mock_match.to_dict(), mock_form.return_value["completed_matches"])

        # 6. Verification that Knockout Elimination logic runs
        mock_elim.assert_called_once_with(mock_form.return_value, self.mock_match, self.mock_config)

        # 7. Verification that Tournament Phase transitions are processed
        mock_phase.assert_called_once_with(mock_elim.return_value, self.mock_config)

        # 8. Verification that persistence and file data mutations are handled cleanly
        mock_save.assert_called_once_with(final_mock_state, self.mock_config)
        mock_build.assert_called_once_with(self.mock_config)

        # 9. Ensure the returned state matches the last stage of mutations
        self.assertEqual(result, final_mock_state)


if __name__ == "__main__":
    unittest.main()