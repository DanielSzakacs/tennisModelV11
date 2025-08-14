import pandas as pd

from src.data.split import time_based_split


def test_time_split_boundaries():
    df = pd.DataFrame({"date": ["2019-06-01", "2020-06-01", "2023-06-01"], "y": [1, 0, 1]})
    train, val, test = time_based_split(df)
    assert len(train) == 1
    assert len(val) == 1
    assert len(test) == 1
