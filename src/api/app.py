from datetime import date as dt_date
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.data.entities import EntityResolver
from src.data.load import load_matches
from src.features.build import player_stats
from src.models.train import FEATURES, MODEL_DIR

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

resolver = EntityResolver()
matches = load_matches()
stats = player_stats(matches)

model_path = MODEL_DIR / 'lgbm_best.joblib'
if not model_path.exists():
    model_path = MODEL_DIR / 'lgbm.joblib'
model_obj = joblib.load(model_path)


class PredictRequest(BaseModel):
    player_a: str
    player_b: str
    surface: str | None = None
    best_of: int | None = None
    date: dt_date | None = None


def player_features(pid: int, date: pd.Timestamp) -> pd.Series:
    sub = stats[(stats['player_id'] == pid) & (stats['tourney_date'] < date)]
    if sub.empty:
        raise HTTPException(status_code=404, detail=f'No history for player {pid}')
    return sub.iloc[-1][['ace_pct', 'df_pct', 'wl_ratio', 'days_since']]


@app.post('/predict')
def predict(req: PredictRequest):
    date = pd.Timestamp(req.date) if req.date else matches['tourney_date'].max() + pd.Timedelta(days=1)
    name_a, id_a, _ = resolver.resolve(req.player_a)
    name_b, id_b, _ = resolver.resolve(req.player_b)
    fa = player_features(id_a, date)
    fb = player_features(id_b, date)
    diff = fa - fb
    X = pd.DataFrame([diff.values], columns=FEATURES)
    Xp = X
    if 'scaler' in model_obj:
        Xp = model_obj['scaler'].transform(X)
    proba = model_obj['model'].predict_proba(Xp)[0, 1]
    return {'player_a': name_a, 'player_b': name_b, 'probability': float(proba)}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
