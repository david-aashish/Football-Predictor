import unittest
from unittest.mock import MagicMock

from live.form import (
    update_tournament_stats,
    update_form,
    form_summary,
)

class TestFormSystem(unittest.TestCase):

    def setUp(self):
        """Set up standard boilerplate mock objects for reuse across tests."""
        # Setup a reusable MatchResult mock where TeamA beats TeamB (2 - 1)
        self.mock_match = MagicMock()
        self.mock_match.home_team = "TeamA"
        self.mock_match.away_team = "TeamB"
        self.mock_match.home_goals = 2
        self.mock_match.away_goals = 1
        self.mock_match.is_draw = False
        self.mock_match.winner = "TeamA"
        self.mock_match.round = 1
        self.mock_match.group = "Group A"

        # Setup standard base dictionary state
        self.initial_state = {
            "teams": {
                "TeamA": {
                    "tournament_stats": {
                        "matches": 0, "goals_for": 0, "goals_against": 0,
                        "goal_difference": 0, "wins": 0, "draws": 0, "losses": 0, "points": 0
                    },
                    "form_last_n": []
                },
                "TeamB": {
                    "tournament_stats": {
                        "matches": 0, "goals_for": 0, "goals_against": 0,
                        "goal_difference": 0, "wins": 0, "draws": 0, "losses": 0, "points": 0
                    },
                    "form_last_n": []
                }
            }
        }

    def test_tournament_stats_updated_and_goals_counted(self):
        """Verify match tallies, goals for/against, and goal difference update correctly."""
        # Execute stats update on baseline match (TeamA 2 - 1 TeamB)
        updated_state = update_tournament_stats(self.initial_state, self.mock_match)
        
        team_a_stats = updated_state["teams"]["TeamA"]["tournament_stats"]
        team_b_stats = updated_state["teams"]["TeamB"]["tournament_stats"]

        # Assert correct count of total games and goals
        self.assertEqual(team_a_stats["matches"], 1)
        self.assertEqual(team_a_stats["goals_for"], 2)
        self.assertEqual(team_a_stats["goals_against"], 1)
        self.assertEqual(team_a_stats["goal_difference"], 1)

        self.assertEqual(team_b_stats["matches"], 1)
        self.assertEqual(team_b_stats["goals_for"], 1)
        self.assertEqual(team_b_stats["goals_against"], 2)
        self.assertEqual(team_b_stats["goal_difference"], -1)

    def test_points_counted_for_wins_and_draws(self):
        """Verify that wins give 3 points, draws give 1 point, and losses give 0 points."""
        # Case 1: TeamA win (from setUp state)
        state_after_win = update_tournament_stats(self.initial_state, self.mock_match)
        self.assertEqual(state_after_win["teams"]["TeamA"]["tournament_stats"]["points"], 3)
        self.assertEqual(state_after_win["teams"]["TeamA"]["tournament_stats"]["wins"], 1)
        self.assertEqual(state_after_win["teams"]["TeamB"]["tournament_stats"]["points"], 0)
        self.assertEqual(state_after_win["teams"]["TeamB"]["tournament_stats"]["losses"], 1)

        # Case 2: Draw Match (1 - 1)
        mock_draw_match = MagicMock()
        mock_draw_match.home_team = "TeamA"
        mock_draw_match.away_team = "TeamB"
        mock_draw_match.home_goals = 1
        mock_draw_match.away_goals = 1
        mock_draw_match.is_draw = True
        mock_draw_match.winner = None

        # Reset state and run draw game
        self.setUp()
        state_after_draw = update_tournament_stats(self.initial_state, mock_draw_match)
        self.assertEqual(state_after_draw["teams"]["TeamA"]["tournament_stats"]["points"], 1)
        self.assertEqual(state_after_draw["teams"]["TeamA"]["tournament_stats"]["draws"], 1)
        self.assertEqual(state_after_draw["teams"]["TeamB"]["tournament_stats"]["points"], 1)
        self.assertEqual(state_after_draw["teams"]["TeamB"]["tournament_stats"]["draws"], 1)

    def test_rolling_window_trims_correctly(self):
        """Verify the recent match form history array stays capped at form_window size."""
        window_size = 2
        
        # Populate history with 3 matches (exceeding window_size)
        state = update_form(self.initial_state, self.mock_match, window_size)
        state = update_form(state, self.mock_match, window_size)
        state = update_form(state, self.mock_match, window_size)

        team_a_form = state["teams"]["TeamA"]["form_last_n"]
        
        # Array length should be exactly capped to window size
        self.assertEqual(len(team_a_form), window_size)

    def test_form_summary_values(self):
        """Verify averages and rates calculate correctly for single, multiple, and empty histories."""
        # Case 1: Empty history bounds
        empty_summary = form_summary([])
        self.assertEqual(empty_summary["matches"], 0)
        self.assertEqual(empty_summary["win_rate"], 0.0)
        self.assertEqual(empty_summary["goals_for_per_game"], 0.0)

        # Case 2: Populated mock match list history
        mock_history = [
            {"result": "win", "goals_for": 3, "goals_against": 0},
            {"result": "loss", "goals_for": 1, "goals_against": 2},
        ]
        
        summary = form_summary(mock_history)
        
        self.assertEqual(summary["matches"], 2)
        self.assertEqual(summary["win_rate"], 0.5)               # 1 win out of 2 matches
        self.assertEqual(summary["goals_for_per_game"], 2.0)      # (3 + 1) / 2
        self.assertEqual(summary["goals_against_per_game"], 1.0)  # (0 + 2) / 2


if __name__ == "__main__":
    unittest.main()
