import requests

API_URL = 'http://127.0.0.1:8000'

def predict(player_a: str, player_b: str) -> float:
    resp = requests.post(f'{API_URL}/predict', json={'player_a': player_a, 'player_b': player_b})
    resp.raise_for_status()
    return resp.json()['probability']
