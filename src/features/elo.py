"""Simple Elo rating implementation."""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Tuple

import pandas as pd


class EloCalculator:
    """Compute Elo ratings over matches."""

    def __init__(self, k_factor: float = 32.0, base_rating: float = 1500.0) -> None:
        self.k = k_factor
        self.base = base_rating
        self.ratings: Dict[str, float] = defaultdict(lambda: base_rating)

    def expected(self, ra: float, rb: float) -> float:
        return 1.0 / (1 + 10 ** ((rb - ra) / 400))

    def update(self, winner: str, loser: str) -> Tuple[float, float]:
        ra = self.ratings[winner]
        rb = self.ratings[loser]
        ea = self.expected(ra, rb)
        eb = 1 - ea
        self.ratings[winner] = ra + self.k * (1 - ea)
        self.ratings[loser] = rb + self.k * (0 - eb)
        return self.ratings[winner], self.ratings[loser]

    def rate_match(self, winner: str, loser: str) -> Tuple[float, float]:
        ra = self.ratings[winner]
        rb = self.ratings[loser]
        self.update(winner, loser)
        return ra, rb


def compute_elo(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Elo ratings for each match and add columns elo_winner/elo_loser."""
    calc = EloCalculator()
    elos_w: list[float] = []
    elos_l: list[float] = []
    for _, row in df.iterrows():
        w = str(row["winner_name"])
        loser_name = str(row["loser_name"])
        rw, rl = calc.rate_match(w, loser_name)
        elos_w.append(rw)
        elos_l.append(rl)
    df = df.copy()
    df["elo_winner"] = elos_w
    df["elo_loser"] = elos_l
    return df

