"""Data preparation pipeline for TennisModelV11.

This script reads raw match data, applies cleaning rules,
computes lagged features, and writes the prepared dataset
into `data/prep/features.csv`.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

RAW_DATA_PATH = Path("data/raw/atp_df.csv")
OUTPUT_PATH = Path("data/prep/features.csv")
LOG_PATH = Path("logs/prep.log")

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def load_raw_data(path: Path) -> pd.DataFrame:
    """Load raw match data from CSV.

    Parameters
    ----------
    path: Path
        Location of the raw CSV file.

    Returns
    -------
    pd.DataFrame
        Loaded dataframe; empty if file is missing.
    """
    if not path.exists():
        logging.warning("Raw data not found at %s", path)
        return pd.DataFrame()
    return pd.read_csv(path)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply basic cleaning steps to the dataframe.

    For now this is a placeholder that simply returns the input.

    Parameters
    ----------
    df: pd.DataFrame
        Raw dataframe.

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe.
    """
    return df


def main() -> None:
    """Run the data preparation pipeline."""
    df = load_raw_data(RAW_DATA_PATH)
    if df.empty:
        logging.info("No data to process. Exiting.")
        return
    df = clean_data(df)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    logging.info("Saved prepared dataset to %s", OUTPUT_PATH)


if __name__ == "__main__":
    main()
