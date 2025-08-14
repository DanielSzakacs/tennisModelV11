import pandas as pd
from src.data.load import load_matches
from src.features.build import player_stats


def test_player_stats_closed_left():
    df = load_matches().head(1000)
    stats = player_stats(df)
    grouped = stats.groupby('player_id')
    first_rows = grouped.head(1)
    assert first_rows['ace_pct'].isna().all()
    assert first_rows['df_pct'].isna().all()
    assert first_rows['wl_ratio'].isna().all()
