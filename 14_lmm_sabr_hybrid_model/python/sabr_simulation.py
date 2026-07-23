"""
sabr_simulation.py

Monte Carlo simulation for the LMM-SABR hybrid.

The simulator stores:

    forward_paths
        path x time x forward

    alpha_paths
        path x time x forward

The simulation grid can include mandatory dates so that:

    reset dates
    caplet fixing dates
    swaption expiries

are represented exactly.
"""

import numpy as np


class LMMSABRSimulationResult:
    """
    Store LMM-SABR simulation results.
    """

    def __init__(
        self,
        times,
        forward_paths,
        alpha_paths
    ):

        self.times = np.asarray(
            times,
            dtype=float
        )

        self.forward_paths = np.asarray(
            forward_paths,
            dtype=float
        )

        self.alpha_paths = np.asarray(
            alpha_paths,
            dtype=float
        )

        self.validate()

    def validate(
        self
    ):
        """
        Validate simulation dimensions.
        """

        if self.forward_paths.ndim != 3:

            raise ValueError(
                "forward_paths must be three-dimensional."
            )

        if self.alpha_paths.ndim != 3:

            raise ValueError(
                "alpha_paths must be three-dimensional."
            )

        if (
            self.forward_paths.shape
            !=
            self.alpha_paths.shape
        ):

            raise ValueError(
                "Forward and alpha paths "
                "must have equal dimensions."
            )

        if (
            self.forward_paths.shape[1]
            !=
            len(
                self.times
            )
        ):

            raise ValueError(
                "The time dimension is inconsistent."
            )

    def get_number_of_paths(
        self
    ):

        return self.forward_paths.shape[0]

    def get_number_of_times(
        self
    ):

        return self.forward_paths.shape[1]

    def get_number_of_forwards(
        self
    ):

        return self.forward_paths.shape[2]


def build_time_grid(
    simulation_end,
    number_of_steps,
    mandatory_times=None
):
    """
    Build a sorted simulation time grid.
    """

    if simulation_end <= 0.0:

        raise ValueError(
            "simulation_end must be positive."
        )

    if number_of_steps <= 0:

        raise ValueError(
            "number_of_steps must be positive."
        )

    base_grid = np.linspace(
        0.0,
        simulation_end,
        number_of_steps + 1
    )

    if mandatory_times is None:

        return base_grid

    mandatory_times = np.asarray(
        mandatory_times,
        dtype=float
    )

    mandatory_times = mandatory_times[
        (
            mandatory_times >= 0.0
        )
        &
        (
            mandatory_times <= simulation_end
        )
    ]

    combined_grid = np.concatenate(
        [
            base_grid,
            mandatory_times
        ]
    )

    combined_grid = np.unique(
        combined_grid
    )

    return np.sort(
        combined_grid
    )


def simulate_lmm_sabr(
    model,
    simulation_end,
    number_of_steps,
    number_of_paths,
    seed=42,
    antithetic=True,
    mandatory_times=None
):
    """
    Simulate forward rates and stochastic volatilities.
    """

    if number_of_paths <= 0:

        raise ValueError(
            "number_of_paths must be positive."
        )

    if mandatory_times is None:

        mandatory_times = (
            model.get_reset_times()
        )

    times = build_time_grid(
        simulation_end,
        number_of_steps,
        mandatory_times
    )

    number_of_times = len(
        times
    )

    forward_paths = np.empty(
        (
            number_of_paths,
            number_of_times,
            model.number_of_forwards
        )
    )

    alpha_paths = np.empty(
        (
            number_of_paths,
            number_of_times,
            model.number_of_forwards
        )
    )

    forward_paths[:, 0, :] = (
        model.initial_forwards
    )

    alpha_paths[:, 0, :] = (
        model.sabr_parameters.alpha0
    )

    random_generator = (
        np.random.default_rng(
            seed
        )
    )

    half_number_of_paths = (
        number_of_paths + 1
    ) // 2

    for time_index in range(
        number_of_times - 1
    ):

        current_time = float(
            times[time_index]
        )

        dt = float(
            times[time_index + 1]
            -
            times[time_index]
        )

        if antithetic:

            base_rate_shocks = (
                random_generator.normal(
                    size=(
                        half_number_of_paths,
                        model.number_of_factors
                    )
                )
            )

            base_volatility_shocks = (
                random_generator.normal(
                    size=(
                        half_number_of_paths,
                        model.number_of_forwards
                    )
                )
            )

            rate_shocks = np.concatenate(
                [
                    base_rate_shocks,
                    -base_rate_shocks
                ],
                axis=0
            )

            volatility_shocks = np.concatenate(
                [
                    base_volatility_shocks,
                    -base_volatility_shocks
                ],
                axis=0
            )

            rate_shocks = rate_shocks[
                :number_of_paths
            ]

            volatility_shocks = (
                volatility_shocks[
                    :number_of_paths
                ]
            )

        else:

            rate_shocks = (
                random_generator.normal(
                    size=(
                        number_of_paths,
                        model.number_of_factors
                    )
                )
            )

            volatility_shocks = (
                random_generator.normal(
                    size=(
                        number_of_paths,
                        model.number_of_forwards
                    )
                )
            )

        for path_index in range(
            number_of_paths
        ):

            current_forwards = (
                forward_paths[
                    path_index,
                    time_index,
                    :
                ]
            )

            current_alpha = (
                alpha_paths[
                    path_index,
                    time_index,
                    :
                ]
            )

            next_forwards, next_alpha = (
                model.evolve(
                    current_time,
                    current_forwards,
                    current_alpha,
                    dt,
                    rate_shocks[
                        path_index
                    ],
                    volatility_shocks[
                        path_index
                    ]
                )
            )

            forward_paths[
                path_index,
                time_index + 1,
                :
            ] = next_forwards

            alpha_paths[
                path_index,
                time_index + 1,
                :
            ] = next_alpha

    return LMMSABRSimulationResult(
        times,
        forward_paths,
        alpha_paths
    )


def exact_time_index(
    times,
    target_time,
    tolerance=1.0e-10
):
    """
    Find a target time on the simulation grid.
    """

    times = np.asarray(
        times,
        dtype=float
    )

    differences = np.abs(
        times
        -
        float(
            target_time
        )
    )

    index = int(
        np.argmin(
            differences
        )
    )

    if differences[index] > tolerance:

        raise ValueError(
            f"Target time {target_time} "
            "is not on the simulation grid."
        )

    return index