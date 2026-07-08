import unittest
from unittest.mock import MagicMock

from live.elo import (
    expected_score,
    effective_rating,
    score_outcome,
    update_elo,
)

class TestEloSystem(unittest.TestCase):

    def test_expected_score_equal_ratings(self):
        """Equal ratings must yield an expected score of exactly 0.5."""
        score = expected_score(1500.0, 1500.0)
        self.assertEqual(score, 0.5)

    def test_expected_score_higher_rating(self):
        """A higher rating must increase the expected score probability."""
        score_higher = expected_score(1600.0, 1400.0)
        score_lower = expected_score(1400.0, 1600.0)
        
        self.assertGreater(score_higher, 0.5)
        self.assertLess(score_lower, 0.5)
        self.assertAlmostEqual(score_higher + score_lower, 1.0)

    def test_effective_rating_host_advantage_applied(self):
        """Host advantage must apply only when the team is home and a designated host."""
        # Case 1: Team is host
        rating_host = effective_rating(
            team="TeamA", base_rating=1500.0, hosts=["TeamA"], host_advantage_elo=100.0
        )
        self.assertEqual(rating_host, 1600.0)

        # Case 2: Team is not host
        rating_not_host = effective_rating(
            team="TeamB", base_rating=1500.0, hosts=["TeamA"], host_advantage_elo=100.0
        )
        self.assertEqual(rating_not_host, 1500.0)

    def test_score_outcome_logic(self):
        """Outcome points must correctly assign 0.5 for draws, 1.0 for wins, and 0.0 for losses."""
        # Draws
        self.assertEqual(score_outcome(2, 2, for_home=True), 0.5)
        self.assertEqual(score_outcome(2, 2, for_home=False), 0.5)

        # Home Win
        self.assertEqual(score_outcome(3, 1, for_home=True), 1.0)
        self.assertEqual(score_outcome(3, 1, for_home=False), 0.0)

        # Away Win
        self.assertEqual(score_outcome(0, 2, for_home=True), 0.0)
        self.assertEqual(score_outcome(0, 2, for_home=False), 1.0)

    def test_update_elo_winner_increases_loser_decreases(self):
        """Elo ratings must increase for the winner and decrease for the loser."""
        # Mocking the TournamentConfig and EloConfig classes
        mock_config = MagicMock()
        mock_config.hosts = []
        mock_config.elo.k_factor = 32
        mock_config.elo.host_advantage = 0.0

        # Mocking the MatchResult where Home wins 2-0
        mock_match = MagicMock()
        mock_match.home_team = "TeamA"
        mock_match.away_team = "TeamB"
        mock_match.home_goals = 2
        mock_match.away_goals = 0

        # Setup initial state
        initial_state = {
            "teams": {
                "TeamA": {"elo": 1500.0},
                "TeamB": {"elo": 1500.0}
            }
        }

        # Execute
        final_state = update_elo(initial_state, mock_match, mock_config)

        # Assertions
        self.assertGreater(final_state["teams"]["TeamA"]["elo"], 1500.0)
        self.assertLess(final_state["teams"]["TeamB"]["elo"], 1500.0)


if __name__ == "__main__":
    unittest.main()