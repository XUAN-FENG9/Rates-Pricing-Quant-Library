# ✝ In memory of my beloved grandfather - Heshun Feng (冯和顺), who passed away today (11th July 2026)
# His love and encouragement will forever inspire me.


import numpy as np


class YieldCurve:
    """
    Continuously compounded zero curve.

    This curve provides:
    - zero rates
    - discount factors
    - implied forward rates

    In production systems:
    - discount curves are usually OIS curves
    - forward curves are tenor-specific

    Here we use a simplified single-curve framework.
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

    def get_df(self, t):
        """
        DF(t) = exp(-r*t)
        """

        r = self.zero_rate(t)

        return np.exp(-r * t)

    def forward_rate(self, t1, t2):
        """
        Implied forward rate.
        """

        df1 = self.discount_factor(t1)
        df2 = self.discount_factor(t2)

        return (
            (df1 / df2) - 1
        ) / (t2 - t1)