import pandas as pd


def time_based_split(df: pd.DataFrame, train_end: str = '2019-12-31', val_end: str = '2022-12-31'):
    """Split the feature table into train, validation and test sets by date."""
    train = df[df['tourney_date'] <= train_end]
    val = df[(df['tourney_date'] > train_end) & (df['tourney_date'] <= val_end)]
    test = df[df['tourney_date'] > val_end]
    return train, val, test


if __name__ == '__main__':
    from src.features.build import build_features
    from src.data.load import load_matches

    feats = build_features(load_matches().head(1000))
    tr, va, te = time_based_split(feats)
    print(len(tr), len(va), len(te))
