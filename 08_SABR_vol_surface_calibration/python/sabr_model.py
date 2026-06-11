"""
sabr_model.py

SABR implied volatility formula.

This module implements Hagan's SABR Black implied volatility approximation.

SABR dynamics:
--------------
dF = alpha * F^beta dW1

dalpha = nu * alpha dW2

corr(dW1, dW2) = rho dt

Parameters:
-----------
alpha : initial volatility level
beta  : elasticity parameter
rho   : correlation between forward and volatility shocks
nu    : volatility of volatility

This chapter focuses on Black implied volatility calibration.
"""

import numpy as np


def hagan_sabr_black_vol(
    forward,
    strike,
    expiry,
    alpha,
    beta,
    rho,
    nu
):
    """
    Hagan SABR Black implied volatility approximation.

    Parameters
    ----------
    forward : float
        Forward swap rate.

    strike : float
        Strike.

    expiry : float
        Option expiry.

    alpha : float
        SABR alpha parameter.

    beta : float
        SABR beta parameter.

    rho : float
        SABR correlation parameter.

    nu : float
        SABR volatility-of-volatility parameter.

    Returns
    -------
    float
        Black implied volatility.
    """

    F = float(forward)
    K = float(strike)
    T = float(expiry)

    if F <= 0 or K <= 0:
        raise ValueError(
            "Hagan Black SABR formula requires positive forward and strike."
        )

    one_minus_beta = 1.0 - beta

    # ------------------------------------------------------------
    # ATM case: F approximately equals K
    # ------------------------------------------------------------

    if abs(F - K) < 1e-12:

        FK_beta = F ** one_minus_beta

        term1 = (
            (one_minus_beta ** 2 / 24.0)
            * (alpha ** 2)
            / (F ** (2.0 * one_minus_beta))
        )

        term2 = (
            0.25
            * rho
            * beta
            * nu
            * alpha
            / (F ** one_minus_beta)
        )

        term3 = (
            (2.0 - 3.0 * rho * rho)
            * nu * nu
            / 24.0
        )

        vol = (
            alpha
            / FK_beta
            * (
                1.0
                + (term1 + term2 + term3) * T
            )
        )

        return vol

    # ------------------------------------------------------------
    # Non-ATM case
    # ------------------------------------------------------------

    log_fk = np.log(F / K)

    FK = F * K

    FK_beta = FK ** (
        one_minus_beta / 2.0
    )

    z = (
        (nu / alpha)
        * FK_beta
        * log_fk
    )

    numerator_x = (
        np.sqrt(
            1.0
            - 2.0 * rho * z
            + z * z
        )
        + z
        - rho
    )

    denominator_x = 1.0 - rho

    x_z = np.log(
        numerator_x / denominator_x
    )

    denominator = (
        FK_beta
        * (
            1.0
            + (one_minus_beta ** 2 / 24.0) * log_fk ** 2
            + (one_minus_beta ** 4 / 1920.0) * log_fk ** 4
        )
    )

    term1 = (
        (one_minus_beta ** 2 / 24.0)
        * alpha * alpha
        / (FK ** one_minus_beta)
    )

    term2 = (
        0.25
        * rho
        * beta
        * nu
        * alpha
        / (FK ** (one_minus_beta / 2.0))
    )

    term3 = (
        (2.0 - 3.0 * rho * rho)
        * nu * nu
        / 24.0
    )

    time_adjustment = (
        1.0
        + (term1 + term2 + term3) * T
    )

    vol = (
        alpha
        / denominator
        * (z / x_z)
        * time_adjustment
    )

    return vol


def sabr_vol_vector(
    forward,
    strikes,
    expiry,
    alpha,
    beta,
    rho,
    nu
):
    """
    Compute SABR Black vols for a vector of strikes.
    """

    vols = []

    for strike in strikes:

        vol = hagan_sabr_black_vol(
            forward=forward,
            strike=strike,
            expiry=expiry,
            alpha=alpha,
            beta=beta,
            rho=rho,
            nu=nu
        )

        vols.append(vol)

    return np.array(vols)