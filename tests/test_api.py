from fastapi.testclient import TestClient

from src.api.app import app


client = TestClient(app)


def test_predict_model_missing():
    response = client.post("/predict", json={"player_a": "A", "player_b": "B"})
    assert response.status_code == 500
