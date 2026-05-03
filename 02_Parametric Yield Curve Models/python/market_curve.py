import pandas as pd


class MarketCurve:
    """
    Container for market zero rate observations.

    FO Perspective
    --------------
    In practice, curve calibration starts from:
    - swap curves
    - government bond curves
    - OIS curves

    Here we use simplified market zero rates.
    """

    def __init__(self, csv_path):

        df = pd.read_csv(csv_path)

        self.times = df["maturity"].values
        self.rates = df["zero_rate"].values