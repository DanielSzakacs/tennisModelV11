"""Feature building pipeline."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pandas as pd

from src.data.load import load_matches
from src.features.elo import compute_elo


PROCESSED_DIR = Path("data/processed")


def build_features() -> pd.DataFrame:
    df = load_matches()
    df = df.sort_values("tourney_date")
    df = compute_elo(df)
    h2h: defaultdict[tuple[str, str], int] = defaultdict(int)
    rows: list[dict[str, object]] = []
    for _, row in df.iterrows():
        a = str(row["winner_name"])
        b = str(row["loser_name"])
        date = row["tourney_date"]
        # before updating h2h
        h2h_ab = h2h[(a, b)]
        h2h_ba = h2h[(b, a)]
        rows.append(
            {
                "date": date,
                "player_a": a,
                "player_b": b,
                "elo_a": row["elo_winner"],
                "elo_b": row["elo_loser"],
                "elo_diff": row["elo_winner"] - row["elo_loser"],
                "h2h_a": h2h_ab,
                "h2h_b": h2h_ba,
                "h2h_diff": h2h_ab - h2h_ba,
                "y": 1,
            }
        )
        rows.append(
            {
                "date": date,
                "player_a": b,
                "player_b": a,
                "elo_a": row["elo_loser"],
                "elo_b": row["elo_winner"],
                "elo_diff": row["elo_loser"] - row["elo_winner"],
                "h2h_a": h2h_ba,
                "h2h_b": h2h_ab,
                "h2h_diff": h2h_ba - h2h_ab,
                "y": 0,
            }
        )
        h2h[(a, b)] += 1
    feat_df = pd.DataFrame(rows)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    feat_df.to_parquet(PROCESSED_DIR / "features_train.parquet", index=False)
    feat_df.to_parquet(PROCESSED_DIR / "features_infer.parquet", index=False)
    return feat_df


if __name__ == "__main__":
    build_features()

