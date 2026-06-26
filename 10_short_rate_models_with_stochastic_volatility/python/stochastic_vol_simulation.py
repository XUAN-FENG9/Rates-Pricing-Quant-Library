"""
stochastic_vol_simulation.py

Monte Carlo simulation for the stochastic-volatility short-rate model.
"""

import numpy as np


def simulate_stochastic_vol_paths(
    model,
    r0,
    v0,
    maturity,
    n_steps,
    n_paths,
    seed=42
):
    """
    Simulate correlated short-rate and variance paths.
    """

    np.random.seed(seed)

    dt = maturity / n_steps

    times = np.linspace(
        0.0,
        maturity,
        n_steps + 1
    )

    rate_paths = np.zeros(
        (n_paths, n_steps + 1)
    )

    variance_paths = np.zeros(
        (n_paths, n_steps + 1)
    )

    rate_paths[:, 0] = r0
    variance_paths[:, 0] = v0

    for step in range(n_steps):

        t = times[step]

        z_rate = np.random.normal(
            size=n_paths
        )

        z_independent = np.random.normal(
            size=n_paths
        )

        z_vol = (
            model.rho * z_rate
            +
            np.sqrt(1.0 - model.rho ** 2)
            *
            z_independent
        )

        for path in range(n_paths):

            r_next, v_next = model.evolve(
                t=t,
                r=rate_paths[path, step],
                v=variance_paths[path, step],
                dt=dt,
                z_rate=z_rate[path],
                z_vol=z_vol[path]
            )

            rate_paths[path, step + 1] = r_next
            variance_paths[path, step + 1] = v_next

    return times, rate_paths, variance_paths


def path_discount_factors(
    times,
    rate_paths,
    end_index=None
):
    """
    Compute pathwise discount factors:

        D(0,T) = exp(- integral_0^T r_t dt)
    """

    if end_index is None:
        end_index = rate_paths.shape[1] - 1

    dt = times[1] - times[0]

    integrals = np.sum(
        rate_paths[:, :end_index],
        axis=1
    ) * dt

    return np.exp(
        -integrals
    )


def forward_discount_factors(
    times,
    rate_paths,
    start_index,
    end_index
):
    """
    Compute pathwise discount factors from start_index to end_index:

        D(t,T) = exp(- integral_t^T r_s ds)
    """

    dt = times[1] - times[0]

    integrals = np.sum(
        rate_paths[:, start_index:end_index],
        axis=1
    ) * dt

    return np.exp(
        -integrals
    )