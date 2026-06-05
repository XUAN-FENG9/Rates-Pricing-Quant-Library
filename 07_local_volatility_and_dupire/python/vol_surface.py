"""
vol_surface.py

Black implied volatility surface.

The surface is built from cleaned market quotes and interpolated using
LinearNDInterpolator.

Important:
----------
The surface stores actual strike levels, not strike shifts.
"""

import numpy as np
from scipy.interpolate import LinearNDInterpolator


class VolSurface:
    """
    Black implied volatility surface sigma_imp(T, K).
    """

    def __init__(
        self,
        clean_quotes_df,
        common_strikes
    ):

        self.clean_quotes_df = clean_quotes_df.copy()

        self.expiries = np.sort(
            self.clean_quotes_df["expiry"].unique()
        )

        self.strikes = np.array(common_strikes)

        points = []
        values = []

        for _, row in self.clean_quotes_df.iterrows():

            points.append(
                [
                    float(row["expiry"]),
                    float(row["strike"])
                ]
            )

            values.append(
                float(row["black_vol"])
            )

        self.interpolator = LinearNDInterpolator(
            np.array(points),
            np.array(values)
        )

    def get_vol(self, expiry, strike):
        """
        Interpolate Black implied volatility.
        """

        vol = self.interpolator(
            expiry,
            strike
        )

        if np.isnan(vol):
            raise ValueError(
                f"Vol interpolation failed at expiry={expiry}, strike={strike}. "
                "Point is outside the valid interpolation region."
            )

        return float(vol)

    def vols_from_quotes(self):
        """
        Build rectangular implied vol matrix on the common strike grid.
        """

        matrix = np.full(
            (len(self.expiries), len(self.strikes)),
            np.nan
        )

        for i, expiry in enumerate(self.expiries):

            for j, strike in enumerate(self.strikes):

                matrix[i, j] = self.get_vol(
                    expiry,
                    strike
                )

        return matrix