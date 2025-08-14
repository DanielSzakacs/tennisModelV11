import pandas as pd

from src.data.load import load_matches


def player_stats(matches: pd.DataFrame) -> pd.DataFrame:
    matches = matches.copy()
    matches['match_id'] = matches.index

    w = matches[
        ['match_id', 'tourney_date', 'surface', 'best_of', 'winner_id', 'loser_id', 'w_ace', 'w_df', 'w_svpt']
    ].rename(
        columns={
            'winner_id': 'player_id',
            'loser_id': 'opponent_id',
            'w_ace': 'ace',
            'w_df': 'df',
            'w_svpt': 'svpt',
        }
    )
    w['is_winner'] = 1

    l = matches[
        ['match_id', 'tourney_date', 'surface', 'best_of', 'winner_id', 'loser_id', 'l_ace', 'l_df', 'l_svpt']
    ].rename(
        columns={
            'loser_id': 'player_id',
            'winner_id': 'opponent_id',
            'l_ace': 'ace',
            'l_df': 'df',
            'l_svpt': 'svpt',
        }
    )
    l['is_winner'] = 0

    long = pd.concat([w, l], ignore_index=True)
    long = long.sort_values('tourney_date')
    long[['ace', 'df', 'svpt']] = long[['ace', 'df', 'svpt']].fillna(0)
    long['loss_indicator'] = 1 - long['is_winner']

    grp = long.groupby('player_id', group_keys=False)
    long['cum_ace'] = grp['ace'].cumsum().shift(1)
    long['cum_df'] = grp['df'].cumsum().shift(1)
    long['cum_svpt'] = grp['svpt'].cumsum().shift(1)
    long['cum_wins'] = grp['is_winner'].cumsum().shift(1)
    long['cum_losses'] = grp['loss_indicator'].cumsum().shift(1)
    long['last_date'] = grp['tourney_date'].shift(1)

    long['ace_pct'] = long['cum_ace'] / long['cum_svpt'] * 100
    long['df_pct'] = long['cum_df'] / long['cum_svpt'] * 100
    long['wl_ratio'] = long['cum_wins'] / (long['cum_wins'] + long['cum_losses'])
    long['days_since'] = (long['tourney_date'] - long['last_date']).dt.days

    return long[
        ['match_id', 'player_id', 'is_winner', 'tourney_date', 'surface', 'best_of',
         'ace_pct', 'df_pct', 'wl_ratio', 'days_since']
    ]


def build_features(matches: pd.DataFrame | None = None) -> pd.DataFrame:
    if matches is None:
        matches = load_matches()
    stats = player_stats(matches)
    feat_cols = ['ace_pct', 'df_pct', 'wl_ratio', 'days_since']
    w_feats = stats[stats['is_winner'] == 1].set_index('match_id')
    l_feats = stats[stats['is_winner'] == 0].set_index('match_id')

    diff = w_feats[feat_cols] - l_feats[feat_cols]
    diff.columns = [f'diff_{c}' for c in feat_cols]
    res1 = diff.reset_index()
    res1['label'] = 1

    diff2 = l_feats[feat_cols] - w_feats[feat_cols]
    diff2.columns = [f'diff_{c}' for c in feat_cols]
    res0 = diff2.reset_index()
    res0['label'] = 0

    out = pd.concat([res1, res0], ignore_index=True)
    context = matches[['match_id', 'surface', 'best_of', 'tourney_date']]
    out = out.merge(context, on='match_id', how='left')
    return out


if __name__ == '__main__':
    df = build_features(load_matches().head(1000))
    print(df.head())
