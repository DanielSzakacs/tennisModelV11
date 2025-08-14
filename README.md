# Tennis Win Probability Model

This project builds a leak-safe machine learning system predicting the probability that player A beats player B on a given date.

## Setup

### Create virtual environment and install dependencies

**Linux/macOS**
```bash
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

**Windows (PowerShell)**
```powershell
python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

### Makefile shortcuts

- `make venv` – create virtual environment and print activation hint
- `make deps` – install Python dependencies
- `make features` – generate features
- `make tune` – hyper‑parameter tuning
- `make train_best` – train model with best parameters
- `make evaluate` – evaluate on test split

## Project Structure

```
├─ data
│  ├─ raw/atp_df.csv
│  └─ processed/
├─ src
│  ├─ data
│  ├─ features
│  ├─ models
│  └─ api
├─ app  # React frontend
└─ reports
```

## Backend

Run the API locally:
```bash
uvicorn src.api.app:app --reload
```

## Frontend

```
cd app
npm install
npm run dev
```

Build production assets:
```
npm run build
```

`.env.example` contains:
```
VITE_API_URL=http://127.0.0.1:8000
```

## Example

```python
from src.api.client import predict
prob = predict("Novak Djokovic", "Rafael Nadal")
print(prob)
```

