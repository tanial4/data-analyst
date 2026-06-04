import pandas as pd
import pytest


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """A small mixed-type dataset used across the deterministic tests."""
    return pd.DataFrame(
        {
            "region": ["West", "East", "West", "East", "West", "North"],
            "product": ["A", "B", "A", "C", "B", "A"],
            "sales": [100, 200, 150, 50, 300, 250],
            "units": [10, 20, 15, 5, 30, 25],
        }
    )
