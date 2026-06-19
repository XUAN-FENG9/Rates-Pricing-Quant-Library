"""
hull_white_simulation.py

Monte Carlo simulation for the Hull-White short-rate model.
"""

import numpy as np


def simulate_short_rate_paths(
    model,
    r0,
    maturity,
    n_steps,
    n_paths,
    seed=42
):
    """
    Simulate Hull-White short-rate paths using Euler discretisation.

    Parameters
    ----------
    model : HullWhiteModel
        Hull-White model.

    r0 : float
        Initial short rate.

    maturity : float
        Simulation horizon.

    n_steps : int
        Number of time steps.

    n_paths : int
        Number of Monte Carlo paths.

    seed : int
        Random seed.

    Returns
    -------
    times : np.ndarray
        Simulation time grid.

    paths : np.ndarray
        Short-rate paths with shape:

            (n_paths, n_steps + 1)
    """

    np.random.seed(seed)

    dt = maturity / n_steps

    times = np.linspace(
        0.0,
        maturity,
        n_steps + 1
    )

    paths = np.zeros(
        (
            n_paths,
            n_steps + 1
        )
    )

    paths[:, 0] = r0

    for step in range(n_steps):

        t = times[step]

        z = np.random.normal(
            size=n_paths
        )

        for path in range(n_paths):

            paths[path, step + 1] = (
                model.evolve_short_rate(
                    t,
                    paths[path, step],
                    dt,
                    z[path]
                )
            )

    return times, paths


def path_discount_factors(
    times,
    short_rate_paths
):
    """
    Compute pathwise discount factors.

    Discount factor along a path:

        D(0,T) = exp(- integral_0^T r_t dt)

    The integral is approximated using a simple left Riemann sum.

    Parameters
    ----------
    times : np.ndarray
        Simulation time grid.

    short_rate_paths : np.ndarray
        Simulated short-rate paths.

    Returns
    -------
    np.ndarray
        Pathwise discount factors to final maturity.
    """

    dt = times[1] - times[0]

    integrals = np.sum(
        short_rate_paths[:, :-1],
        axis=1
    ) * dt

    return np.exp(
        -integrals
    )


def monte_carlo_zero_coupon_bond_price(
    times,
    short_rate_paths
):
    """
    Estimate zero-coupon bond price by Monte Carlo.

    Parameters
    ----------
    times : np.ndarray
        Simulation time grid.

    short_rate_paths : np.ndarray
        Short-rate paths.

    Returns
    -------
    float
        Monte Carlo estimate of discount bond price.
    """

    dfs = path_discount_factors(
        times,
        short_rate_paths
    )

    return float(
        np.mean(dfs)
    )