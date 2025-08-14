from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import pandas as pd


@dataclass
class EloConfig:
    k: float = 32.0
    base: float = 1500.0


def compute_elo(matches: pd.DataFrame, cfg: EloConfig | None = None) -> pd.DataFrame:
    """Compute running Elo ratings for players."""
    cfg = cfg or EloConfig()
    ratings = defaultdict(lambda: cfg.base)
    surface_ratings = defaultdict(lambda: cfg.base)

    records = []
    for _, row in matches.sort_values('tourney_date').iterrows():
        w_id = row['winner_id']
        l_id = row['loser_id']
        surface = row['surface']

        w_elo = ratings[w_id]
        l_elo = ratings[l_id]
        w_surf = surface_ratings[(w_id, surface)]
        l_surf = surface_ratings[(l_id, surface)]

        exp_w = 1 / (1 + 10 ** ((l_elo - w_elo) / 400))
        exp_l = 1 - exp_w

        ratings[w_id] += cfg.k * (1 - exp_w)
        ratings[l_id] += cfg.k * (0 - exp_l)

        exp_w_s = 1 / (1 + 10 ** ((l_surf - w_surf) / 400))
        exp_l_s = 1 - exp_w_s
        surface_ratings[(w_id, surface)] += cfg.k * (1 - exp_w_s)
        surface_ratings[(l_id, surface)] += cfg.k * (0 - exp_l_s)

        records.append({
            'match_id': row.name,
            'winner_elo': w_elo,
            'loser_elo': l_elo,
            'winner_surface_elo': w_surf,
            'loser_surface_elo': l_surf,
        })

    elo_df = pd.DataFrame(records)
    return elo_df


if __name__ == '__main__':
    from src.data.load import load_matches

    df = load_matches().head(1000)
    elo = compute_elo(df)
    print(elo.head())
