# ✝ In memory of my beloved grandfather - Heshun Feng (冯和顺), who passed away today (11th July 2026)
# His love and encouragement will forever inspire me.


"""
volatility.py

Volatility specification for the Gaussian LMM.

The model uses deterministic normal forward-rate volatilities.

A compact specification is:

    sigma_i(t)
    =
    sigma_level
    exp[-decay (T_i - t)]

for t <= T_i.

Once forward L_i has reset, its volatility is set to zero.
"""

import numpy as np


class GaussianLMMVolatility:
    """
    Deterministic Gaussian LMM volatility structure.

    Parameters
    ----------
    reset_times : array-like
        Reset times T_i.

    sigma_level : float
        Normal forward-rate volatility level.

        Example:
            0.01 means approximately 100 basis points
            of annualized normal volatility.

    decay : float
        Maturity-decay parameter.

    floor : float
        Minimum volatility before reset.
    """

    def __init__(
        self,
        reset_times,
        sigma_level=0.01,
        decay=0.05,
        floor=0.001
    ):

        self.reset_times = np.asarray(
            reset_times,
            dtype=float
        )

        self.sigma_level = float(
            sigma_level
        )

        self.decay = float(
            decay
        )

        self.floor = float(
            floor
        )

        if self.sigma_level < 0.0:
            raise ValueError(
                "sigma_level must be non-negative."
            )

        if self.decay < 0.0:
            raise ValueError(
                "decay must be non-negative."
            )

    def instantaneous_vols(
        self,
        t
    ):
        """
        Return normal volatilities for all forwards at time t.
        """

        remaining = np.maximum(
            self.reset_times
            -
            t,
            0.0
        )

        vols = (
            self.sigma_level
            *
            np.exp(
                -self.decay
                *
                remaining
            )
        )

        vols = np.maximum(
            vols,
            self.floor
        )

        # A forward becomes fixed after its reset time.
        vols = np.where(
            t < self.reset_times - 1e-12,
            vols,
            0.0
        )

        return vols

    def factor_loadings(
        self,
        t,
        correlation_loadings
    ):
        """
        Combine marginal volatilities with correlation loadings.

        Returns
        -------
        np.ndarray
            Matrix with shape:

                n_forwards x n_factors
        """

        vols = self.instantaneous_vols(
            t
        )

        return (
            vols[:, None]
            *
            correlation_loadings
        )