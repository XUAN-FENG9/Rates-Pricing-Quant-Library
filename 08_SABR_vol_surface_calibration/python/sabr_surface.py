"""
sabr_surface.py

Build SABR parameter surface across expiries.

Each expiry slice is calibrated independently.

Output:
-------
A table of SABR parameters:

expiry | alpha | beta | rho | nu | rmse

This is the core object used later for:
- smile interpolation
- surface generation
- pricing comparison
"""

import pandas as pd

from market_data import get_quotes_for_expiry
from sabr_calibration import calibrate_sabr_slice
from sabr_model import sabr_vol_vector


class SABRSurface:
    """
    SABR calibrated parameter surface.
    """

    def __init__(
        self,
        clean_quotes_df,
        beta=0.5
    ):

        self.clean_quotes_df = clean_quotes_df.copy()
        self.beta = beta

        self.expiries = sorted(
            self.clean_quotes_df["expiry"].unique()
        )

        self.calibrations = {}
        self.parameter_table = None
        
        
    def calibrate(self):
        """
        Calibrate SABR independently for each expiry,
        but use the previous expiry's calibrated parameters
        as the next initial guess.

        This stabilizes the parameter term structure.
        """
        rows = []

        previous_guess = None

        for expiry in self.expiries:

            forward, strikes, market_vols = (
                get_quotes_for_expiry(
                    self.clean_quotes_df,
                    expiry
                )
            )

            result = calibrate_sabr_slice(
                forward=forward,
                strikes=strikes,
                expiry=expiry,
                market_vols=market_vols,
                beta=self.beta,
                initial_guess=previous_guess
            )

            self.calibrations[expiry] = result

            rows.append(
                {
                    "expiry": expiry,
                    "forward": result["forward"],
                    "alpha": result["alpha"],
                    "beta": result["beta"],
                    "rho": result["rho"],
                    "nu": result["nu"],
                    "rmse": result["rmse"],
                    "success": result["success"]
                }
            )

            previous_guess = [
                result["alpha"],
                result["rho"],
                result["nu"]
            ]

        self.parameter_table = pd.DataFrame(rows)

        return self.parameter_table


    def get_params(self, expiry):
        """
        Get calibrated SABR parameters for one expiry.

        Current version requires exact expiry.
        Surface interpolation is left for later extension.
        """

        if expiry not in self.calibrations:
            raise ValueError(
                f"SABR not calibrated for expiry={expiry}"
            )

        result = self.calibrations[expiry]

        return (
            result["alpha"],
            result["beta"],
            result["rho"],
            result["nu"]
        )

    def fitted_vols(self, expiry):
        """
        Return fitted vols for one calibrated expiry.
        """

        result = self.calibrations[expiry]

        vols = sabr_vol_vector(
            forward=result["forward"],
            strikes=result["strikes"],
            expiry=expiry,
            alpha=result["alpha"],
            beta=result["beta"],
            rho=result["rho"],
            nu=result["nu"]
        )

        return vols