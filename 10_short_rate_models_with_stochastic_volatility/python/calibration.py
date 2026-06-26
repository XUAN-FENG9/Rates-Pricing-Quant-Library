"""
calibration.py

Simple calibration utilities for stochastic-volatility short-rate models.

This is intentionally lightweight. A production implementation would use
swaption surfaces and more robust optimizers.
"""

import numpy as np
from scipy.optimize import minimize

from stochastic_vol_model import (
    StochasticVolShortRateModel
)

from stochastic_vol_simulation import (
    simulate_stochastic_vol_paths
)

from pricing import (
    monte_carlo_bond_option_price
)


def stochastic_vol_calibration_objective(
    params,
    base_hw_model,
    r0,
    option_data,
    fixed_rho=-0.3,
    fixed_kappa=None,
    n_steps=240,
    n_paths=3000,
    seed=42
):
    """
    Calibration objective for stochastic-vol parameters.

    To keep the example stable, we calibrate:

        v_bar
        eta

    and optionally kappa.

    rho is fixed by default.
    """

    if fixed_kappa is None:

        kappa, v_bar, eta = params

    else:

        v_bar, eta = params
        kappa = fixed_kappa

    if kappa <= 0 or v_bar <= 0 or eta < 0:
        return 1e10

    if v_bar > 0.05 or eta > 2.0:
        return 1e10

    model = StochasticVolShortRateModel(
        base_hw_model=base_hw_model,
        kappa=kappa,
        v_bar=v_bar,
        eta=eta,
        rho=fixed_rho
    )

    max_maturity = max(
        item["bond_maturity"]
        for item in option_data
    )

    v0 = v_bar

    times, rate_paths, variance_paths = simulate_stochastic_vol_paths(
        model=model,
        r0=r0,
        v0=v0,
        maturity=max_maturity,
        n_steps=n_steps,
        n_paths=n_paths,
        seed=seed
    )

    error = 0.0

    for item in option_data:

        model_price = monte_carlo_bond_option_price(
            times=times,
            rate_paths=rate_paths,
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

    return float(error)


def calibrate_stochastic_vol_model(
    base_hw_model,
    r0,
    option_data,
    fixed_rho=-0.3,
    fixed_kappa=1.0,
    initial_guess=(0.0001, 0.20),
    n_steps=240,
    n_paths=3000,
    seed=42
):
    """
    Calibrate v_bar and eta with fixed kappa and rho.

    Parameters
    ----------
    base_hw_model : HullWhiteModel
        Chapter 09 Hull-White model.

    r0 : float
        Initial short rate.

    option_data : list of dict
        Calibration instruments.

    fixed_rho : float
        Fixed correlation.

    fixed_kappa : float
        Fixed variance mean reversion speed.

    initial_guess : tuple
        Initial guess for (v_bar, eta).

    Returns
    -------
    dict
        Calibration result.
    """

    bounds = [
        (1e-8, 0.05),   # v_bar
        (1e-4, 2.0)     # eta
    ]

    result = minimize(
        stochastic_vol_calibration_objective,
        initial_guess,
        args=(
            base_hw_model,
            r0,
            option_data,
            fixed_rho,
            fixed_kappa,
            n_steps,
            n_paths,
            seed
        ),
        bounds=bounds,
        method="L-BFGS-B"
    )

    return {
        "kappa": fixed_kappa,
        "v_bar": result.x[0],
        "eta": result.x[1],
        "rho": fixed_rho,
        "objective": result.fun,
        "success": result.success,
        "message": result.message
    }