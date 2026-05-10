import pandas as pd


def load_market_curve(csv_path):

    df = pd.read_csv(csv_path)

    return (
        df["maturity"].values,
        df["zero_rate"].values
    )
