"""Model training script for TennisModelV11.

This module trains a simple classifier on the prepared features
and stores the trained model along with basic metrics.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

FEATURES_PATH = Path("data/prep/features.csv")
MODEL_PATH = Path("models/model.joblib")
REPORT_PATH = Path("reports/metrics/train_results.json")
LOG_PATH = Path("logs/training.log")
RANDOM_STATE = 42

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def load_features(path: Path) -> pd.DataFrame:
    """Load prepared features from CSV.

    Parameters
    ----------
    path: Path
        Location of the features CSV file.

    Returns
    -------
    pd.DataFrame
        Loaded feature dataframe; empty if file is missing.
    """
    if not path.exists():
        logging.warning("Features not found at %s", path)
        return pd.DataFrame()
    return pd.read_csv(path)


def train(df: pd.DataFrame) -> tuple[LogisticRegression, float]:
    """Train a logistic regression model.

    Parameters
    ----------
    df: pd.DataFrame
        Feature dataframe with a `label` column.

    Returns
    -------
    tuple[LogisticRegression, float]
        Trained model and accuracy on the validation split.
    """
    y = df["label"]
    X = df.drop(columns=["label"])
    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    model = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
    model.fit(X_train, y_train)
    preds = model.predict(X_valid)
    acc = accuracy_score(y_valid, preds)
    return model, acc


def main() -> None:
    """Run the training pipeline."""
    df = load_features(FEATURES_PATH)
    if df.empty or "label" not in df.columns:
        logging.info("No features with label column. Exiting.")
        return
    model, acc = train(df)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    with REPORT_PATH.open("w") as f:
        json.dump({"accuracy": acc}, f)
    logging.info("Model trained with accuracy %.3f", acc)


if __name__ == "__main__":
    main()
