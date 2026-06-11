"""
sabr_calibration.py

Calibration routines for SABR model.

This module calibrates SABR parameters to one expiry slice:

    market vols at different strikes
        ↓
    calibrated alpha, rho, nu

We typically fix beta because beta is hard to identify
from a single smile slice.
"""

import numpy as np
from scipy.optimize import minimize

from sabr_model import sabr_vol_vector


def sabr_objective(
    params,
    forward,
    strikes,
    expiry,
    market_vols,
    beta
):
    """
    Sum of squared errors between market vols and SABR vols.

    Parameters
    ----------
    params : array-like
        [alpha, rho, nu]

    beta : float
        Fixed beta parameter.

    Returns
    -------
    float
        Calibration error.
    """

    alpha, rho, nu = params

    # ------------------------------------------------------------
    # Soft parameter constraints
    # ------------------------------------------------------------

    if alpha <= 0:
        return 1e10

    if nu <= 0:
        return 1e10

    if rho <= -0.999 or rho >= 0.999:
        return 1e10

    try:
        model_vols = sabr_vol_vector(
            forward=forward,
            strikes=strikes,
            expiry=expiry,
            alpha=alpha,
            beta=beta,
            rho=rho,
            nu=nu
        )

    except Exception:
        return 1e10

    errors = model_vols - market_vols

    return float(
        np.sum(errors ** 2)
    )


def calibrate_sabr_slice(
    forward,
    strikes,
    expiry,
    market_vols,
    beta=0.5,
    initial_guess=None
):
    """
    Calibrate SABR parameters for one expiry slice.

    Parameters
    ----------
    forward : float
        Forward swap rate.

    strikes : np.ndarray
        Strike levels.

    expiry : float
        Option expiry.

    market_vols : np.ndarray
        Market Black implied vols.

    beta : float
        Fixed beta.

    initial_guess : list or None
        Initial guess [alpha, rho, nu].

    Returns
    -------
    dict
        Calibrated SABR parameters and diagnostics.
    """

    if initial_guess is None:

        # Alpha roughly matches ATM vol scaled by F^(1-beta)
        atm_index = np.argmin(
            np.abs(strikes - forward)
        )

        atm_vol = market_vols[atm_index]

        alpha0 = (
            atm_vol
            * (forward ** (1.0 - beta))
        )

        initial_guess = [
            alpha0,
            -0.25,
            0.50
        ]

    bounds = [
        (1e-6, 5.0),       # alpha
        (-0.90, 0.90),     # rho
        (0.05, 2.0)        # nu
    ]

    result = minimize(
        sabr_objective,
        initial_guess,
        args=(
            forward,
            strikes,
            expiry,
            market_vols,
            beta
        ),
        method="L-BFGS-B",
        bounds=bounds
    )

    alpha, rho, nu = result.x

    fitted_vols = sabr_vol_vector(
        forward=forward,
        strikes=strikes,
        expiry=expiry,
        alpha=alpha,
        beta=beta,
        rho=rho,
        nu=nu
    )

    rmse = np.sqrt(
        np.mean(
            (fitted_vols - market_vols) ** 2
        )
    )

    return {
        "expiry": expiry,
        "forward": forward,
        "alpha": alpha,
        "beta": beta,
        "rho": rho,
        "nu": nu,
        "success": result.success,
        "objective": result.fun,
        "rmse": rmse,
        "market_vols": market_vols,
        "fitted_vols": fitted_vols,
        "strikes": strikes
    }


def calibrate_alpha_only(
    forward,
    strikes,
    expiry,
    market_vols,
    beta,
    rho,
    nu,
    alpha_bounds=(1e-6, 5.0)
):
    """
    Calibrate only SABR alpha while keeping beta, rho, and nu fixed.

    This mimics a common practical workflow:

    - beta is fixed by convention
    - rho and nu are updated less frequently
    - alpha is updated more frequently to match volatility level

    Parameters
    ----------
    forward : float
        Forward swap rate.

    strikes : np.ndarray
        Strike levels.

    expiry : float
        Option expiry.

    market_vols : np.ndarray
        Market Black implied vols.

    beta, rho, nu : float
        Fixed SABR parameters.

    alpha_bounds : tuple
        Lower and upper bounds for alpha.

    Returns
    -------
    dict
        Alpha-only calibration result.
    """

    def objective(alpha):

        model_vols = sabr_vol_vector(
            forward=forward,
            strikes=strikes,
            expiry=expiry,
            alpha=alpha,
            beta=beta,
            rho=rho,
            nu=nu
        )

        errors = model_vols - market_vols

        return float(
            (errors ** 2).sum()
        )

    result = minimize_scalar(
        objective,
        bounds=alpha_bounds,
        method="bounded"
    )

    alpha = result.x

    fitted_vols = sabr_vol_vector(
        forward=forward,
        strikes=strikes,
        expiry=expiry,
        alpha=alpha,
        beta=beta,
        rho=rho,
        nu=nu
    )

    rmse = (
        ((fitted_vols - market_vols) ** 2).mean()
    ) ** 0.5

    return {
        "alpha": alpha,
        "beta": beta,
        "rho": rho,
        "nu": nu,
        "rmse": rmse,
        "success": result.success,
        "fitted_vols": fitted_vols
    }