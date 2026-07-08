import unittest
from unittest.mock import MagicMock

from live.advancement import (
    apply_elimination,
    update_phase,
    mark_eliminated,
)

class TestTournamentAdvancement(unittest.TestCase):

    def setUp(self):
        """Set up standard boilerplate dictionary state and config mocks."""
        # Initial tournament dictionary state
        self.state = {
            "teams": {
                "TeamA": {"eliminated": False},
                "TeamB": {"eliminated": False},
                "TeamC": {"eliminated": False},
            },
            "eliminated_teams": [],
            "completed_matches": []
        }

        # Mock standard configuration structures
        self.mock_config = MagicMock()
        self.mock_config.format.knockout_rounds = ["r16", "qf", "sf", "final"]
        self.mock_config.format.group_stage.groups = 4
        self.mock_config.format.group_stage.matches_per_group = 6  # 24 total group matches

    def test_group_match_eliminates_nobody(self):
        """Verify that a match in a group stage round never updates elimination state."""
        mock_match = MagicMock()
        mock_match.round = "Group A"
        mock_match.loser = "TeamB"

        updated_state = apply_elimination(self.state, mock_match, self.mock_config)

        # Team fields and elimination tracking lists must remain completely unchanged
        self.assertFalse(updated_state["teams"]["TeamB"]["eliminated"])
        self.assertNotIn("TeamB", updated_state["eliminated_teams"])

    def test_knockout_loser_eliminated(self):
        """Verify that a designated loser in a knockout round gets properly flagged as eliminated."""
        mock_match = MagicMock()
        mock_match.round = "r16"
        mock_match.loser = "TeamB"

        updated_state = apply_elimination(self.state, mock_match, self.mock_config)

        # Team field flag must trigger true and append cleanly to tracked arrays
        self.assertTrue(updated_state["teams"]["TeamB"]["eliminated"])
        self.assertIn("TeamB", updated_state["eliminated_teams"])
        self.assertEqual(len(updated_state["eliminated_teams"]), 1)

    def test_phase_updated_correctly(self):
        """Verify that current_phase transitions accurately across group and knockout structures."""
        # Case 1: Group stage boundary check (24 total group matches config)
        self.state["completed_matches"] = [MagicMock()] * 10
        state_group = update_phase(self.state, self.mock_config)
        self.assertEqual(state_group["current_phase"], "group")

        # Case 2: Shift to first knockout round (24 group games + 3 knockout games = 27)
        # 'r16' takes up to 8 matches. 27 total games means 3 played in knockout phase (< 8).
        self.state["completed_matches"] = [MagicMock()] * 27
        state_k1 = update_phase(self.state, self.mock_config)
        self.assertEqual(state_k1["current_phase"], "r16")

        # Case 3: Shift to next knockout round (24 group games + 10 knockout games = 34)
        # 'r16' cumulative is 8, 'qf' cumulative is 8 + 4 = 12 matches. 10 is between 8 and 12.
        self.state["completed_matches"] = [MagicMock()] * 34
        state_k2 = update_phase(self.state, self.mock_config)
        self.assertEqual(state_k2["current_phase"], "qf")

        # Case 4: Finished status boundary match (All rounds completely fulfilled)
        # Total matches: 24 (group) + 8 (r16) + 4 (qf) + 2 (sf) + 1 (final) = 39 total games
        self.state["completed_matches"] = [MagicMock()] * 39
        state_finished = update_phase(self.state, self.mock_config)
        self.assertEqual(state_finished["current_phase"], "finished")

    def test_manual_elimination(self):
        """Verify that an administrative manual override flag accurately tracks team states."""
        # Force individual removal
        updated_state = mark_eliminated(self.state, "TeamC")

        # System state tracking criteria check
        self.assertTrue(updated_state["teams"]["TeamC"]["eliminated"])
        self.assertIn("TeamC", updated_state["eliminated_teams"])

        # Run an idempotent check to verify duplicate additions don't corrupt arrays
        duplicate_state = mark_eliminated(updated_state, "TeamC")
        self.assertEqual(len(duplicate_state["eliminated_teams"]), 1)


if __name__ == "__main__":
    unittest.main()
