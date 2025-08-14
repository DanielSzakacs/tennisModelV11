"""FastAPI inference service."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.data.entities import EntityResolver
from src.data.load import load_matches
from src.features.elo import EloCalculator

app = FastAPI()

ARTIFACT = joblib.load(Path("models/logit_model.pkl")) if Path("models/logit_model.pkl").exists() else None
resolver = EntityResolver()

# build current elo and h2h stats
matches = load_matches().sort_values("tourney_date")
elo_calc = EloCalculator()
h2h: dict[tuple[str, str], int] = {}
for _, row in matches.iterrows():
    w = str(row["winner_name"])
    loser_name = str(row["loser_name"])
    elo_calc.rate_match(w, loser_name)
    h2h[(w, loser_name)] = h2h.get((w, loser_name), 0) + 1


class PredictRequest(BaseModel):
    player_a: str
    player_b: str
    surface: Optional[str] = None
    best_of: Optional[int] = None
    date: Optional[str] = None


@app.post("/predict")
def predict(req: PredictRequest):
    if ARTIFACT is None:
        raise HTTPException(status_code=500, detail="Model not available")
    pid_a, sugg_a = resolver.resolve(req.player_a)
    pid_b, sugg_b = resolver.resolve(req.player_b)
    if pid_a is None:
        raise HTTPException(status_code=400, detail=f"Unknown player_a. Suggestions: {sugg_a}")
    if pid_b is None:
        raise HTTPException(status_code=400, detail=f"Unknown player_b. Suggestions: {sugg_b}")
    name_a = req.player_a
    name_b = req.player_b
    elo_a = elo_calc.ratings.get(name_a, 1500)
    elo_b = elo_calc.ratings.get(name_b, 1500)
    elo_diff = elo_a - elo_b
    h2h_diff = h2h.get((name_a, name_b), 0) - h2h.get((name_b, name_a), 0)
    X = pd.DataFrame([[elo_a, elo_b, elo_diff, h2h_diff]], columns=["elo_a", "elo_b", "elo_diff", "h2h_diff"])
    probs = ARTIFACT["calibrator"].predict_proba(X)[:, 1][0]
    return {
        "prob_a_wins": probs,
        "prob_b_wins": 1 - probs,
        "model": "logit",
        "top_features": [
            {"name": "elo_diff", "contribution": float(elo_diff)},
            {"name": "h2h_diff", "contribution": float(h2h_diff)},
        ],
    }

