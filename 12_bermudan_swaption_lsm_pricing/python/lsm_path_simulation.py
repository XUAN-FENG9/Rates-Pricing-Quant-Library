"""
lsm_path_simulation.py

Monte Carlo path simulation for Bermudan swaption LSM pricing.

This chapter reuses the Chapter 09 HullWhiteModel object.
"""

import numpy as np


def simulate_hull_white_paths_for_lsm(
    model,
    r0,
    maturity,
    n_steps,
    n_paths,
    seed=42
):
    """
    Simulate Hull-White short-rate paths for LSM.

    Parameters
    ----------
    model : HullWhiteModel
        Chapter 09 Hull-White model.

    r0 : float
        Initial short rate.

    maturity : float
        Final simulation horizon.

    n_steps : int
        Number of simulation steps.

    n_paths : int
        Number of Monte Carlo paths.

    seed : int
        Random seed.

    Returns
    -------
    times : np.ndarray
        Simulation time grid.

    rate_paths : np.ndarray
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

    rate_paths = np.zeros(
        (
            n_paths,
            n_steps + 1
        )
    )

    rate_paths[:, 0] = r0

    for step in range(n_steps):

        t = times[step]

        z = np.random.normal(
            size=n_paths
        )

        r = rate_paths[:, step]

        drift = np.array(
            [
                model.short_rate_drift(
                    t,
                    ri
                )
                for ri in r
            ]
        )

        rate_paths[:, step + 1] = (
            r
            +
            drift * dt
            +
            model.sigma
            *
            np.sqrt(dt)
            *
            z
        )

    return times, rate_paths


def path_discount_factors_to_index(
    times,
    rate_paths,
    end_index
):
    """
    Pathwise discount factors from time 0 to a time index.

    D(0,t_i) = exp(- integral_0^t_i r_s ds)
    """

    dt = times[1] - times[0]

    integrals = np.sum(
        rate_paths[:, :end_index],
        axis=1
    ) * dt

    return np.exp(
        -integrals
    )


def path_discount_factors_between_indices(
    times,
    rate_paths,
    start_index,
    end_index
):
    """
    Pathwise discount factors between two time indices.

    D(t_i,t_j) = exp(- integral_t_i^t_j r_s ds)
    """

    dt = times[1] - times[0]

    integrals = np.sum(
        rate_paths[:, start_index:end_index],
        axis=1
    ) * dt

    return np.exp(
        -integrals
    )


def nearest_time_index(
    times,
    target_time
):
    """
    Return nearest simulation-grid index.
    """

    return int(
        np.argmin(
            np.abs(
                times - target_time
            )
        )
    )