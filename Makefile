.PHONY: venv deps features tune train_best evaluate

venv:
python -m venv .venv && echo "Run 'source .venv/bin/activate' (Unix) or '.venv\Scripts\Activate.ps1' (Windows)"

deps:
pip install -r requirements.txt

features:
python - <<'PY'
from src.data.load import load_matches
from src.features.build import build_features
feats = build_features(load_matches())
print(feats.head())
PY

tune:
python -m src.models.tune

train_best:
python -m src.models.train_best

evaluate:
python -m src.models.evaluate

