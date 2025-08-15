"""Streamlit frontend for TennisModelV11.

Users can select two players and receive the predicted
probability of player A winning the match.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

MODEL_PATH = Path("models/model.joblib")
FEATURES_PATH = Path("data/prep/features.csv")


def load_resources() -> tuple[pd.DataFrame, object]:
    """Load feature table and trained model if available."""
    features = pd.read_csv(FEATURES_PATH) if FEATURES_PATH.exists() else pd.DataFrame()
    model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
    return features, model


def main() -> None:
    """Render the Streamlit application."""
    st.title("Tennis Match Predictor")
    features, model = load_resources()
    if features.empty or model is None:
        st.warning("Model or features not available. Please run the pipeline first.")
        return
    players = sorted(set(features["player_a"]).union(features["player_b"]))
    player_a = st.selectbox("Player A", players)
    player_b = st.selectbox("Player B", players)
    if player_a == player_b:
        st.error("Please select two different players.")
        return
    if st.button("Predict"):
        latest = features[(features["player_a"] == player_a) & (features["player_b"] == player_b)]
        if latest.empty:
            st.info("No recent data for this matchup.")
            return
        X = latest.drop(columns=["label"])
        proba = model.predict_proba(X)[0, 1]
        st.success(f"Win probability for {player_a}: {proba:.2%}")


if __name__ == "__main__":
    main()
