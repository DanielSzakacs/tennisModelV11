# TennisModelV11

This project predicts tennis match outcomes based on historical data. It follows the workflow outlined in `Agents.md`, including data preparation, model training, and a Streamlit frontend.

## Structure

- `data/raw/` – original ATP dataset.
- `data/interim/` – intermediate data.
- `data/prep/` – prepared features for modeling.
- `scripts/` – data processing and training scripts.
- `models/` – serialized models.
- `reports/` – generated figures and metrics.
- `logs/` – pipeline and training logs.

## Usage

1. Prepare dataset:
   ```bash
   python scripts/make_dataset.py
   ```
2. Train model:
   ```bash
   python scripts/train_models.py
   ```
3. Run frontend:
   ```bash
   streamlit run app.py
   ```

## Requirements

Dependencies are listed in `requirements.txt` and can be installed with:

```bash
pip install -r requirements.txt
```

