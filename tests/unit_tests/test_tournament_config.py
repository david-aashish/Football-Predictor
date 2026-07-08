import unittest

from live.tournament_config import load_tournament_config, resolve_config_paths


class TestTournamentConfigSimple(unittest.TestCase):

    def test_configuration_loads_correctly(self):
        """Test 1: Verify the core metadata properties match the YAML specifications."""
        config = load_tournament_config("wc2026")

        self.assertEqual(config.year, 2026)
        self.assertEqual(config.teams, 48)

    def test_hosts_loaded(self):
        """Test 2: Verify the North American host nations are parsed accurately."""
        config = load_tournament_config("wc2026")

        self.assertIn("United States", config.hosts)
        self.assertIn("Mexico", config.hosts)
        self.assertIn("Canada", config.hosts)

    def test_paths_resolved(self):
        """Test 3: Verify path resolution maps out to files that exist on disk."""
        config = load_tournament_config("wc2026")
        config = resolve_config_paths(config)

        # Verifies the file actually exists inside your local data/ directory structure
        self.assertTrue(config.baseline_dataset.exists())


if __name__ == "__main__":
    unittest.main()
