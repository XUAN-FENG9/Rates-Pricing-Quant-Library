"""
lmm_sabr_plotting.py

Plotting utilities for the LMM-SABR hybrid.
"""

import matplotlib.pyplot as plt
import numpy as np

from sabr_simulation import exact_time_index


def plot_forward_paths(
    model,
    simulation,
    forward_index,
    number_of_paths_to_plot=30
):
    """
    Plot selected paths for one forward rate.
    """

    number_of_paths_to_plot = min(
        number_of_paths_to_plot,
        simulation.get_number_of_paths()
    )

    plt.figure(
        figsize=(10, 6)
    )

    for path_index in range(
        number_of_paths_to_plot
    ):

        plt.plot(
            simulation.times,
            simulation.forward_paths[
                path_index,
                :,
                forward_index
            ],
            alpha=0.6
        )

    plt.axvline(
        model.get_reset_times()[
            forward_index
        ],
        linestyle="--"
    )

    plt.title(
        f"Simulated Paths of Forward L{forward_index}"
    )

    plt.xlabel(
        "Simulation Time"
    )

    plt.ylabel(
        "Forward Rate"
    )

    plt.grid()

    plt.show()


def plot_alpha_paths(
    model,
    simulation,
    forward_index,
    number_of_paths_to_plot=30
):
    """
    Plot stochastic-volatility paths for one forward.
    """

    number_of_paths_to_plot = min(
        number_of_paths_to_plot,
        simulation.get_number_of_paths()
    )

    plt.figure(
        figsize=(10, 6)
    )

    for path_index in range(
        number_of_paths_to_plot
    ):

        plt.plot(
            simulation.times,
            simulation.alpha_paths[
                path_index,
                :,
                forward_index
            ],
            alpha=0.6
        )

    plt.axvline(
        model.get_reset_times()[
            forward_index
        ],
        linestyle="--"
    )

    plt.title(
        f"Stochastic Volatility Paths for L{forward_index}"
    )

    plt.xlabel(
        "Simulation Time"
    )

    plt.ylabel(
        "Alpha"
    )

    plt.grid()

    plt.show()


def plot_forward_distribution(
    simulation,
    forward_index,
    time,
    number_of_bins=50
):
    """
    Plot the distribution of one forward at one time.
    """

    time_index = exact_time_index(
        simulation.times,
        time
    )

    values = (
        simulation.forward_paths[
            :,
            time_index,
            forward_index
        ]
    )

    plt.figure(
        figsize=(10, 6)
    )

    plt.hist(
        values,
        bins=number_of_bins
    )

    plt.title(
        f"Distribution of L{forward_index} "
        f"at t = {time}"
    )

    plt.xlabel(
        "Forward Rate"
    )

    plt.ylabel(
        "Frequency"
    )

    plt.grid()

    plt.show()


def plot_alpha_distribution(
    simulation,
    forward_index,
    time,
    number_of_bins=50
):
    """
    Plot the distribution of alpha at one time.
    """

    time_index = exact_time_index(
        simulation.times,
        time
    )

    values = (
        simulation.alpha_paths[
            :,
            time_index,
            forward_index
        ]
    )

    plt.figure(
        figsize=(10, 6)
    )

    plt.hist(
        values,
        bins=number_of_bins
    )

    plt.title(
        f"Distribution of Alpha {forward_index} "
        f"at t = {time}"
    )

    plt.xlabel(
        "Alpha"
    )

    plt.ylabel(
        "Frequency"
    )

    plt.grid()

    plt.show()


def plot_mean_forward_curves(
    model,
    simulation
):
    """
    Plot the mean simulated value of every forward through time.
    """

    mean_forwards = np.mean(
        simulation.forward_paths,
        axis=0
    )

    plt.figure(
        figsize=(11, 7)
    )

    for forward_index in range(
        model.number_of_forwards
    ):

        plt.plot(
            simulation.times,
            mean_forwards[
                :,
                forward_index
            ],
            label=f"L{forward_index}"
        )

    plt.title(
        "Mean Simulated Forward Rates Through Time"
    )

    plt.xlabel(
        "Simulation Time"
    )

    plt.ylabel(
        "Mean Forward Rate"
    )

    plt.grid()

    plt.show()


def plot_mean_alpha_curves(
    model,
    simulation
):
    """
    Plot the mean stochastic-volatility level
    for every forward through time.
    """

    mean_alpha = np.mean(
        simulation.alpha_paths,
        axis=0
    )

    plt.figure(
        figsize=(11, 7)
    )

    for forward_index in range(
        model.number_of_forwards
    ):

        plt.plot(
            simulation.times,
            mean_alpha[
                :,
                forward_index
            ],
            label=f"Alpha {forward_index}"
        )

    plt.title(
        "Mean SABR Alpha Levels Through Time"
    )

    plt.xlabel(
        "Simulation Time"
    )

    plt.ylabel(
        "Mean Alpha"
    )

    plt.grid()

    plt.show()