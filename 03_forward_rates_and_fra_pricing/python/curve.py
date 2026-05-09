import numpy as np


class YieldCurve:
    """
    Simple continuously compounded zero curve.

    This class provides:
    - zero rates
    - discount factors
    - implied forward rates

    FO Perspective
    --------------
    In real trading systems, curves are built from:
    - OIS swaps
    - IRS swaps
    - futures
    - FRA instruments

    Here we use simplified market zero rates.
    """

    def __init__(self, maturities, zero_rates):

        self.maturities = np.array(maturities)
        self.zero_rates = np.array(zero_rates)

    def zero_rate(self, t):
        """
        Linear interpolation of zero rates.
        """

        return np.interp(
            t,
            self.maturities,
            self.zero_rates
        )

    def discount_factor(self, t):
        """
        Compute discount factor:

        DF(t) = exp(-r*t)
        """

        r = self.zero_rate(t)

        return np.exp(-r * t)

    def forward_rate(self, t1, t2):
        """
        Compute implied forward rate.

        Formula:

        F(t1,t2)
        =
        (DF(t1)/DF(t2)-1)/(t2-t1)
        """

        df1 = self.discount_factor(t1)
        df2 = self.discount_factor(t2)

        return (
            (df1 / df2) - 1
        ) / (t2 - t1)