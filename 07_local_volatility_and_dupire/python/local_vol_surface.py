"""
local_vol_surface.py

Local volatility surface:

    sigma_local(T, K)

generated from Dupire's formula.

Uses LinearNDInterpolator for expiry/strike interpolation.
"""

import numpy as np
from scipy.interpolate import LinearNDInterpolator


class LocalVolSurface:
    """
    Container for Dupire local volatility surface.
    """

    def __init__(
        self,
        expiries,
        strikes,
        local_vol_matrix
    ):

        self.expiries = np.array(expiries)
        self.strikes = np.array(strikes)
        self.local_vol_matrix = np.array(local_vol_matrix)

        points = []
        values = []

        for i, expiry in enumerate(self.expiries):

            for j, strike in enumerate(self.strikes):

                vol = self.local_vol_matrix[i, j]

                if np.isnan(vol):
                    continue

                points.append([expiry, strike])
                values.append(vol)

        self.interpolator = LinearNDInterpolator(
            np.array(points),
            np.array(values)
        )

    def get_local_vol(self, expiry, strike):
        """
        Return interpolated local volatility.

        Parameters
        ----------
        expiry : float
            Option expiry.

        strike : float
            Actual strike level.

        Returns
        -------
        float
        """

        vol = self.interpolator(expiry, strike)

        if np.isnan(vol):
            raise ValueError(
                f"Local vol interpolation failed at expiry={expiry}, strike={strike}."
            )

        return float(vol)