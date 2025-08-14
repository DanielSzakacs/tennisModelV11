"""Time-based dataset splitting."""
from __future__ import annotations

import pandas as pd


SEED = 42


def time_based_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = df[df["date"] <= "2019-12-31"]
    val = df[(df["date"] >= "2020-01-01") & (df["date"] <= "2022-12-31")]
    test = df[df["date"] >= "2023-01-01"]
    for name, part in zip(["train", "val", "test"], [train, val, test]):
        if len(part) > 0:
            ratio = part["y"].mean()
        else:
            ratio = float("nan")
        print(f"{name}: {len(part)} samples, positive ratio={ratio:.3f}")
    return train, val, test

