"""
dupire_builder.py

Dupire local volatility construction.

Core formula:

    sigma_loc^2(K,T)
    =
    (dC/dT)
    /
    (0.5 * K^2 * d2C/dK2)

This module assumes:
- price surface is already built
- strikes are actual rate levels
- expiries are in years
"""

import numpy as np

from local_vol_surface import LocalVolSurface


class DupireBuilder:
    """
    Build local volatility surface from option price surface.
    """

    def __init__(
        self,
        price_surface
    ):

        self.price_surface = price_surface
        self.expiries = price_surface.expiries
        self.strikes = price_surface.strikes
        self.prices = price_surface.price_matrix

        if self.prices is None:
            raise ValueError(
                "Price surface has not been built. "
                "Call price_surface.build() first."
            )

    def build(self):
        """
        Compute Dupire local volatility matrix.

        Boundary rows/columns are left as NaN because
        central finite differences require neighboring points.
        """

        n_exp = len(self.expiries)
        n_strike = len(self.strikes)

        local_vols = np.full(
            (n_exp, n_strike),
            np.nan
        )

        for i in range(1, n_exp - 1):

            for j in range(1, n_strike - 1):

                T_prev = self.expiries[i - 1]
                T_next = self.expiries[i + 1]

                K_prev = self.strikes[j - 1]
                K = self.strikes[j]
                K_next = self.strikes[j + 1]

                C_T_prev = self.prices[i - 1, j]
                C_T_next = self.prices[i + 1, j]

                C_K_prev = self.prices[i, j - 1]
                C_K = self.prices[i, j]
                C_K_next = self.prices[i, j + 1]

                dC_dT = (
                    C_T_next - C_T_prev
                ) / (
                    T_next - T_prev
                )

                dK_left = K - K_prev
                dK_right = K_next - K

                if not np.isclose(dK_left, dK_right):
                    raise ValueError(
                        "Non-uniform strike grid detected. "
                        "Current implementation assumes uniform strike spacing."
                    )

                dK = dK_left

                d2C_dK2 = (
                    C_K_next
                    - 2.0 * C_K
                    + C_K_prev
                ) / (dK * dK)

                denominator = (
                    0.5
                    * K
                    * K
                    * d2C_dK2
                )

                if dC_dT <= 0 or denominator <= 0:
                    continue

                local_var = dC_dT / denominator

                if local_var <= 0:
                    continue

                local_vols[i, j] = np.sqrt(local_var)

        return LocalVolSurface(
            self.expiries,
            self.strikes,
            local_vols
        )