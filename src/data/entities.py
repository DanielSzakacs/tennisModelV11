from __future__ import annotations

import unicodedata
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
from rapidfuzz import fuzz, process

from .load import load_matches

ALIASES_PATH = Path(__file__).resolve().parents[2] / 'data' / 'processed' / 'player_aliases.csv'


def _normalize(text: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c)
    ).lower()


def build_aliases(df: pd.DataFrame) -> pd.DataFrame:
    winners = df[['winner_name', 'winner_id']].dropna().drop_duplicates()
    winners = winners.rename(columns={'winner_name': 'player_name', 'winner_id': 'player_id'})
    losers = df[['loser_name', 'loser_id']].dropna().drop_duplicates()
    losers = losers.rename(columns={'loser_name': 'player_name', 'loser_id': 'player_id'})
    names = pd.concat([winners, losers]).drop_duplicates()
    names['key'] = names['player_name'].apply(_normalize)
    names.to_csv(ALIASES_PATH, index=False)
    return names


def load_aliases() -> pd.DataFrame:
    if ALIASES_PATH.exists():
        return pd.read_csv(ALIASES_PATH)
    df = load_matches()
    return build_aliases(df)


class EntityResolver:
    def __init__(self):
        self.aliases = load_aliases()
        self.alias_map: Dict[str, Tuple[str, int]] = {
            row['key']: (row['player_name'], int(row['player_id']))
            for _, row in self.aliases.iterrows()
        }

    def resolve(self, name: str) -> Tuple[str, int, float]:
        key = _normalize(name)
        if key in self.alias_map:
            canon, pid = self.alias_map[key]
            return canon, pid, 100.0
        choices = [row['player_name'] for _, row in self.aliases.iterrows()]
        match, score, _ = process.extractOne(name, choices, scorer=fuzz.WRatio)
        if score >= 90:
            row = self.aliases[self.aliases['player_name'] == match].iloc[0]
            return row['player_name'], int(row['player_id']), score
        raise ValueError(f"Unknown player name: {name}")


if __name__ == '__main__':
    resolver = EntityResolver()
    print(resolver.resolve('R. Nadal'))
