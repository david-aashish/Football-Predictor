import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from live.initialize import initialize

class TestInitializeIntegration(unittest.TestCase):

    def setUp(self):
        """Create a temporary directory scope for sandboxed file operations."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.test_dir.name)

        # Build a 48-team mockup state structure to simulate create_initial_state output
        self.mock_teams = {f"Team_{i}": {"elo": 1500.0} for i in range(1, 49)}
        self.mock_initial_state = {
            "teams": self.mock_teams,
            "completed_matches": [],
            "eliminated_teams": []
        }

    def tearDown(self):
        """Clean up the temporary directory fully after test execution."""
        self.test_dir.cleanup()

    @patch("live.initialize.create_initial_state")
    @patch("live.initialize.load_tournament_config")
    @patch("live.initialize.resolve_config_paths")
    def test_initialize_integration_workflow(self, mock_resolve, mock_load, mock_create_state):
        """Verify directories are created, files match JSON specs, and 48 teams load properly."""
        
        # 1. Setup real state destinations pointing inside our temporary directory sandbox
        state_dir_path = self.temp_path / "state"
        state_file_path = state_dir_path / "tournament.json"
        pending_file_path = state_dir_path / "pending_matches.json"

        # 2. Build a functional configuration object mock to carry our sandbox paths
        mock_config = MagicMock()
        mock_config.edition = "wc2026"
        mock_config.year = 2026
        mock_config.state_dir = state_dir_path
        mock_config.state_file = state_file_path
        mock_config.pending_matches_file = pending_file_path

        # Inject our mocks into the initialization pipeline hooks
        mock_load.return_value = mock_config
        mock_resolve.return_value = mock_config
        mock_create_state.return_value = self.mock_initial_state

        # 3. Execute the target initialization process
        initialize("wc2026")

        # ASSERTION 1: CREATES FOLDER - Check if the state directory was created on disk
        self.assertTrue(state_dir_path.exists())
        self.assertTrue(state_dir_path.is_dir())

        # ASSERTION 2: CREATES STATE FILE - Verify tournament.json exists and contains correct data
        self.assertTrue(state_file_path.exists())
        with state_file_path.open("r", encoding="utf-8") as handle:
            written_state = json.load(handle)
        
        # Verify basic key structure inside the written state file
        self.assertIn("teams", written_state)
        self.assertEqual(written_state["completed_matches"], [])

        # ASSERTION 3: 48 TEAMS LOADED - Verify all 48 teams exist in the generated tournament file
        self.assertEqual(len(written_state["teams"]), 48)
        self.assertIn("Team_1", written_state["teams"])
        self.assertIn("Team_48", written_state["teams"])

        # ASSERTION 4: CREATES PENDING QUEUE - Verify pending queue exists and initializes as an empty list
        self.assertTrue(pending_file_path.exists())
        with pending_file_path.open("r", encoding="utf-8") as handle:
            written_queue = json.load(handle)
        
        self.assertIsInstance(written_queue, list)
        self.assertEqual(len(written_queue), 0)


if __name__ == "__main__":
    unittest.main()