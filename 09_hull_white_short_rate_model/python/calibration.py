"""
calibration.py

Simple Hull-White parameter calibration utilities.

This chapter uses a lightweight calibration setup:

- mean reversion a
- volatility sigma

can be calibrated to target bond option prices or target implied vols.

A full production calibration would typically use a swaption volatility cube.
"""

import numpy as np
from scipy.optimize import minimize

from option_pricing import price_zero_coupon_bond_option


def calibration_objective(
    params,
    curve,
    option_data,
    model_class
):
    """
    Objective function for Hull-White calibration.

    Parameters
    ----------
    params : array-like
        [mean_reversion, volatility]

    curve : YieldCurve
        Initial yield curve.

    option_data : list of dict
        Each dict should contain:
        - option_expiry
        - bond_maturity
        - strike
        - market_price

    model_class : class
        HullWhiteModel class.

    Returns
    -------
    float
        Sum of squared pricing errors.
    """

    a, sigma = params

    if a <= 0.0 or sigma <= 0.0:
        return 1e10

    model = model_class(
        mean_reversion=a,
        volatility=sigma,
        curve=curve
    )

    error = 0.0

    for item in option_data:

        model_price = price_zero_coupon_bond_option(
            model=model,
            option_expiry=item["option_expiry"],
            bond_maturity=item["bond_maturity"],
            strike=item["strike"],
            option_type=item.get(
                "option_type",
                "call"
            )
        )

        diff = (
            model_price
            -
            item["market_price"]
        )

        error += diff * diff

    return error


def calibrate_hull_white(
    curve,
    option_data,
    model_class,
    initial_guess=(0.05, 0.01)
):
    """
    Calibrate Hull-White mean reversion and volatility.

    Parameters
    ----------
    curve : YieldCurve
        Initial yield curve.

    option_data : list of dict
        Target option prices.

    model_class : class
        HullWhiteModel class.

    initial_guess : tuple
        Initial guess for (a, sigma).

    Returns
    -------
    dict
        Calibration result.
    """

    bounds = [
        (1e-4, 1.0),    # mean reversion
        (1e-4, 0.10)    # short-rate volatility
    ]

    result = minimize(
        calibration_objective,
        initial_guess,
        args=(
            curve,
            option_data,
            model_class
        ),
        bounds=bounds,
        method="L-BFGS-B"
    )

    return {
        "mean_reversion": result.x[0],
        "volatility": result.x[1],
        "objective": result.fun,
        "success": result.success,
        "message": result.message
    }