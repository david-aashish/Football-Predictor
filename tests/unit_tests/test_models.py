import unittest

from live.models import MatchResult, parse_result_string


class TestMatchResultModel(unittest.TestCase):

    def test_winner_property(self):
        """Test 1: Verify the winner property returns the correct winning team."""
        match = MatchResult(home_team="Brazil", away_team="Norway", home_goals=2, away_goals=1)
        
        self.assertEqual(match.winner, "Brazil")
        self.assertFalse(match.is_draw)

    def test_loser_property(self):
        """Test 2: Verify the loser property returns the correct losing team."""
        match = MatchResult(home_team="Brazil", away_team="Norway", home_goals=2, away_goals=1)
        
        self.assertEqual(match.loser, "Norway")

    def test_draw_properties(self):
        """Test 3: Verify a draw returns None for both winner and loser properties."""
        match = MatchResult(home_team="Brazil", away_team="Norway", home_goals=2, away_goals=2)
        
        self.assertTrue(match.is_draw)
        self.assertIsNone(match.winner)
        self.assertIsNone(match.loser)

    def test_dictionary_serialization_roundtrip(self):
        """Test 4: Verify to_dict() and from_dict() cycle recreates an identical object."""
        original_match = MatchResult(
            home_team="Brazil",
            away_team="Norway",
            home_goals=2,
            away_goals=1,
            round="r16",
            group="A",
            match_id="m_123"
        )
        
        # Serialize down to raw data dictionary
        match_dict = original_match.to_dict()
        
        # Deserialize back up into a fresh MatchResult model instance
        reconstructed_match = MatchResult.from_dict(match_dict)
        
        # Ensure values remain completely identical across parameters
        self.assertEqual(original_match.home_team, reconstructed_match.home_team)
        self.assertEqual(original_match.away_team, reconstructed_match.away_team)
        self.assertEqual(original_match.home_goals, reconstructed_match.home_goals)
        self.assertEqual(original_match.away_goals, reconstructed_match.away_goals)
        self.assertEqual(original_match.round, reconstructed_match.round)
        self.assertEqual(original_match.group, reconstructed_match.group)
        self.assertEqual(original_match.match_id, reconstructed_match.match_id)

    def test_parse_result_string(self):
        """Test 5: Verify parse_result_string() extracts valid tokens into a standard MatchResult."""
        parsed_match = parse_result_string("Brazil 2-1 Norway", round_name="group", group="A")
        
        self.assertIsInstance(parsed_match, MatchResult)
        self.assertEqual(parsed_match.home_team, "Brazil")
        self.assertEqual(parsed_match.away_team, "Norway")
        self.assertEqual(parsed_match.home_goals, 2)
        self.assertEqual(parsed_match.away_goals, 1)
        self.assertEqual(parsed_match.round, "group")
        self.assertEqual(parsed_match.group, "A")


if __name__ == "__main__":
    unittest.main()
