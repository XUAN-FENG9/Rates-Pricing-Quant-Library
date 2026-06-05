"""
swaption_price_surface.py

Build Black swaption price surface C(T,K).

This module connects:
- YieldCurve
- ForwardStartingSwap
- BlackSwaption
- VolSurface
"""

import numpy as np

from forward_swap import ForwardStartingSwap
from black_swaption import BlackSwaption


class SwaptionPriceSurface:
    """
    Builds swaption price surface C(T,K).
    """

    def __init__(
        self,
        curve,
        vol_surface,
        tenor=5.0,
        notional=1.0,
        payer=True
    ):

        self.curve = curve
        self.vol_surface = vol_surface
        self.tenor = tenor
        self.notional = notional
        self.payer = payer

        self.expiries = vol_surface.expiries
        self.strikes = vol_surface.strikes

        self.price_matrix = None

    def build(self):
        """
        Build rectangular Black swaption price matrix.
        """

        prices = np.full(
            (len(self.expiries), len(self.strikes)),
            np.nan
        )

        for i, expiry in enumerate(self.expiries):

            underlying_swap = ForwardStartingSwap(
                notional=self.notional,
                fixed_rate=None,
                start=expiry,
                end=expiry + self.tenor,
                payment_frequency=2
            )

            for j, strike in enumerate(self.strikes):

                vol = self.vol_surface.get_vol(
                    expiry,
                    strike
                )

                swaption = BlackSwaption(
                    notional=self.notional,
                    strike=strike,
                    expiry=expiry,
                    underlying_swap=underlying_swap,
                    volatility=vol,
                    payer=self.payer
                )

                prices[i, j] = swaption.price(
                    self.curve
                )

        self.price_matrix = prices

        return prices