import numpy as np

from scipy.stats import norm


class BlackSwaption:
    """
    Black lognormal swaption model.

    WARNING:
    --------
    Invalid when forward rates
    become negative.
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

        # ----------------------------------------
        # Black model invalid for negative rates
        # ----------------------------------------

        if F <= 0 or K <= 0:

            raise ValueError(
                "Black model invalid for "
                "negative rates."
            )

        d1 = (
            np.log(F / K)
            + 0.5 * sigma**2 * T
        ) / (sigma * np.sqrt(T))

        d2 = (
            d1
            - sigma * np.sqrt(T)
        )

        if self.payer:

            price = (
                self.notional
                * annuity
                * (
                    F * norm.cdf(d1)
                    - K * norm.cdf(d2)
                )
            )

        else:

            price = (
                self.notional
                * annuity
                * (
                    K * norm.cdf(-d2)
                    - F * norm.cdf(-d1)
                )
            )

        return price