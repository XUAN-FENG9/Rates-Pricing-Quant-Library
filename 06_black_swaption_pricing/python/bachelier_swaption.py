import numpy as np

from scipy.stats import norm


class BachelierSwaption:
    """
    Normal-model swaption pricing.

    Handles:
    ----------
    - low rates
    - negative rates

    Widely used after 2014.
    """

    def __init__(
        self,
        notional,
        strike,
        expiry,
        underlying_swap,
        volatility,
        payer=True
    ):

        self.notional = notional

        self.strike = strike

        self.expiry = expiry

        self.swap = underlying_swap

        self.volatility = volatility

        self.payer = payer

    def price(self, curve):

        F = self.swap.forward_swap_rate(
            curve
        )

        K = self.strike

        sigma = self.volatility

        T = self.expiry

        annuity = self.swap.annuity(
            curve
        )

        stddev = sigma * np.sqrt(T)

        d = (F - K) / stddev

        if self.payer:

            value = (
                self.notional
                * annuity
                * (
                    (F - K)
                    * norm.cdf(d)
                    + stddev
                    * norm.pdf(d)
                )
            )

        else:

            value = (
                self.notional
                * annuity
                * (
                    (K - F)
                    * norm.cdf(-d)
                    + stddev
                    * norm.pdf(d)
                )
            )

        return value