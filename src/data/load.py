"""Data loading utilities."""
from __future__ import annotations

from pathlib import Path
import pandas as pd


def load_matches(path: str | Path = "data/raw/atp_df.csv") -> pd.DataFrame:
    """Load raw ATP match data.

    Parameters
    ----------
    path: str or Path
        CSV file path.
    """
    dtype = {
        "surface": "category",
        "tourney_level": "category",
        "winner_hand": "category",
        "loser_hand": "category",
        "round": "category",
    }
    parse_dates = ["tourney_date"]
    df = pd.read_csv(path, dtype=dtype, parse_dates=parse_dates)
    return df

