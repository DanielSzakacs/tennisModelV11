"""Player entity normalization utilities."""
from __future__ import annotations

from pathlib import Path
import unicodedata
from typing import List, Optional, Tuple

import pandas as pd
from rapidfuzz import fuzz, process


def _strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if unicodedata.category(c) != "Mn")


def _normalize(text: str) -> str:
    return _strip_accents(text).strip().lower()


class EntityResolver:
    """Resolve player names to canonical ids."""

    def __init__(self, alias_path: str | Path = "data/processed/player_aliases.csv") -> None:
        self.alias_path = Path(alias_path)
        if self.alias_path.exists():
            self.alias_df = pd.read_csv(self.alias_path)
        else:
            self.alias_df = pd.DataFrame(columns=["alias", "player_id", "canonical_name"])

    def resolve(self, name: str) -> Tuple[Optional[str], List[str]]:
        """Resolve name to player id.

        Returns player_id and suggestions if not found.
        """
        norm = _normalize(name)
        if norm in self.alias_df["alias"].values:
            row = self.alias_df[self.alias_df["alias"] == norm].iloc[0]
            return str(row["player_id"]), []
        choices = self.alias_df["alias"].tolist()
        matches = process.extract(norm, choices, scorer=fuzz.ratio, limit=5)
        suggestions: List[str] = []
        for match, score, _ in matches:
            if score >= 90:
                canonical = self.alias_df[self.alias_df["alias"] == match]["canonical_name"].iloc[0]
                suggestions.append(canonical)
        return None, suggestions

    def build_aliases(self, df: pd.DataFrame) -> pd.DataFrame:
        """Build alias table from raw matches DataFrame."""
        names = pd.concat(
            [
                df[["winner_name", "winner_id"]].rename(columns={"winner_name": "name", "winner_id": "player_id"}),
                df[["loser_name", "loser_id"]].rename(columns={"loser_name": "name", "loser_id": "player_id"}),
            ]
        )
        names = names.dropna()
        names["alias"] = names["name"].map(_normalize)
        aliases = names.drop_duplicates("alias")[["alias", "player_id", "name"]]
        aliases = aliases.rename(columns={"name": "canonical_name"})
        aliases.to_csv(self.alias_path, index=False)
        self.alias_df = aliases
        return aliases

