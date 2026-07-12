# ✝ In memory of my beloved grandfather - Heshun Feng (冯和顺), who passed away today (11th July 2026)
# His love and encouragement will forever inspire me.


"""
simulation.py

Monte Carlo simulation for the Gaussian LMM.
"""

import numpy as np


def simulate_gaussian_lmm(
    model,
    simulation_end,
    n_steps,
    n_paths,
    seed=42,
    antithetic=False
):
    """
    Simulate Gaussian LMM forward-rate paths.

    Parameters
    ----------
    model : GaussianLMM
        Gaussian forward-rate market model.

    simulation_end : float
        Final simulation time.

    n_steps : int
        Number of time steps.

    n_paths : int
        Number of Monte Carlo paths.

    seed : int
        Random seed.

    antithetic : bool
        If True, use antithetic normal shocks.

    Returns
    -------
    times : np.ndarray
        Simulation time grid.

    forward_paths : np.ndarray
        Shape:

            n_paths x (n_steps + 1) x n_forwards
    """

    if simulation_end <= 0.0:
        raise ValueError(
            "simulation_end must be positive."
        )

    if n_steps <= 0:
        raise ValueError(
            "n_steps must be positive."
        )

    if n_paths <= 0:
        raise ValueError(
            "n_paths must be positive."
        )

    rng = np.random.default_rng(
        seed
    )

    dt = (
        simulation_end
        /
        n_steps
    )

    times = np.linspace(
        0.0,
        simulation_end,
        n_steps + 1
    )

    forward_paths = np.zeros(
        (
            n_paths,
            n_steps + 1,
            model.n_forwards
        )
    )

    forward_paths[:, 0, :] = (
        model.initial_forwards
    )

    for step in range(
        n_steps
    ):

        t = times[step]

        if antithetic:

            half = (
                n_paths
                +
                1
            ) // 2

            base_shocks = rng.normal(
                size=(
                    half,
                    model.n_factors
                )
            )

            shocks = np.vstack(
                [
                    base_shocks,
                    -base_shocks
                ]
            )[:n_paths]

        else:

            shocks = rng.normal(
                size=(
                    n_paths,
                    model.n_factors
                )
            )

        for path in range(
            n_paths
        ):

            forward_paths[
                path,
                step + 1,
                :
            ] = model.evolve(
                t=t,
                forward_rates=forward_paths[
                    path,
                    step,
                    :
                ],
                dt=dt,
                factor_shocks=shocks[path]
            )

    return times, forward_paths


def nearest_simulation_index(
    times,
    target_time
):
    """
    Return nearest simulation-grid index.
    """

    return int(
        np.argmin(
            np.abs(
                times
                -
                target_time
            )
        )
    )