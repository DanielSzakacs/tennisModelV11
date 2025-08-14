import pandas as pd
from pathlib import Path

RAW_PATH = Path(__file__).resolve().parents[2] / 'data' / 'raw' / 'atp_df.csv'

def load_matches(path: Path = RAW_PATH) -> pd.DataFrame:
    """Load raw ATP matches CSV with proper dtypes and parsed dates."""
    dtypes = {
        'tourney_id': 'string',
        'tourney_name': 'string',
        'surface': 'string',
        'draw_size': 'float64',
        'tourney_level': 'string',
        'match_num': 'int64',
        'winner_id': 'Int64',
        'winner_name': 'string',
        'winner_hand': 'string',
        'winner_ht': 'float64',
        'winner_ioc': 'string',
        'winner_age': 'float64',
        'loser_id': 'Int64',
        'loser_name': 'string',
        'loser_hand': 'string',
        'loser_ht': 'float64',
        'loser_ioc': 'string',
        'loser_age': 'float64',
        'score': 'string',
        'best_of': 'Int64',
        'round': 'string',
        'minutes': 'float64',
        'w_ace': 'float64',
        'w_df': 'float64',
        'w_svpt': 'float64',
        'w_1stIn': 'float64',
        'w_1stWon': 'float64',
        'w_2ndWon': 'float64',
        'w_SvGms': 'float64',
        'w_bpSaved': 'float64',
        'w_bpFaced': 'float64',
        'l_ace': 'float64',
        'l_df': 'float64',
        'l_svpt': 'float64',
        'l_1stIn': 'float64',
        'l_1stWon': 'float64',
        'l_2ndWon': 'float64',
        'l_SvGms': 'float64',
        'l_bpSaved': 'float64',
        'l_bpFaced': 'float64',
        'winner_rank': 'float64',
        'winner_rank_points': 'float64',
        'loser_rank': 'float64',
        'loser_rank_points': 'float64'
    }
    df = pd.read_csv(path, dtype=dtypes, parse_dates=['tourney_date'])
    df = df.sort_values('tourney_date').reset_index(drop=True)
    return df

if __name__ == '__main__':
    print(load_matches().head())
