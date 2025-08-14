.PHONY: setup eda features train evaluate serve frontend predict

setup:
pip install -e .

eda:
python notebooks/01_eda.ipynb

features:
python -m src.features.build

train:
python -m src.models.train

evaluate:
python -m src.models.evaluate

serve:
uvicorn src.api.app:app --reload

frontend:
npm --prefix app start

predict:
curl -X POST http://localhost:8000/predict -H 'Content-Type: application/json' -d '{"player_a":"A","player_b":"B"}'

