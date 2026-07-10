import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch

import live.timeline as timeline
from live.timeline import (
    extract_snapshot_number,
    get_probability_column,
)

# =====================================================================
# 1. TEST CASES FOR extract_snapshot_number()
# =====================================================================

@pytest.mark.parametrize(
    "filename, expected_number",
    [
        ("wc2026_snapshot_001_pre_tournament.csv", 1),
        ("wc2026_snapshot_012_match_011.csv", 12),
    ],
)
def test_extract_snapshot_number_valid(filename, expected_number):
    """Test that numbers are correctly pulled out of valid snapshot file paths."""
    path = Path(filename)
    assert extract_snapshot_number(path) == expected_number


def test_extract_snapshot_number_invalid():
    """Test that None is returned if no digit component exists in the filename."""
    path = Path("wc2026_snapshot_abc_pre_tournament.csv")
    assert extract_snapshot_number(path) is None


# =====================================================================
# 2. TEST CASES FOR get_probability_column()
# =====================================================================

def test_get_probability_column_priority_live():
    """Test that Live_Probability is selected first if it exists."""
    df = pd.DataFrame(columns=["Live_Probability", "Probability"])
    assert get_probability_column(df) == "Live_Probability"

def test_get_probability_column_priority_base():
    """Test that Probability is selected if Live is missing."""
    df = pd.DataFrame(columns=["Probability"])
    assert get_probability_column(df) == "Probability"


def test_get_probability_column_missing_raises_error():
    """Test that a ValueError is raised if no standard probability header exists."""
    df = pd.DataFrame(columns=["Team", "Rank"])
    with pytest.raises(ValueError, match="No probability column found in snapshot."):
        get_probability_column(df)
        