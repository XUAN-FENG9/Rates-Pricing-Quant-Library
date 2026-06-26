"""
plotting.py

Plotting utilities for Chapter 10.
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_rate_paths(
    times,
    rate_paths,
    n_plot=30
):
    """
    Plot simulated short-rate paths.
    """

    plt.figure(figsize=(10, 6))

    for i in range(
        min(n_plot, rate_paths.shape[0])
    ):
        plt.plot(
            times,
            rate_paths[i]
        )

    plt.title(
        "Stochastic-Volatility Short-Rate Paths"
    )
    plt.xlabel("Time")
    plt.ylabel("Short Rate")
    plt.grid()
    plt.show()


def plot_variance_paths(
    times,
    variance_paths,
    n_plot=30
):
    """
    Plot simulated variance paths.
    """

    plt.figure(figsize=(10, 6))

    for i in range(
        min(n_plot, variance_paths.shape[0])
    ):
        plt.plot(
            times,
            variance_paths[i]
        )

    plt.title(
        "Stochastic Variance Paths"
    )
    plt.xlabel("Time")
    plt.ylabel("Variance")
    plt.grid()
    plt.show()


def plot_mean_rate_and_vol(
    times,
    rate_paths,
    variance_paths
):
    """
    Plot mean short rate and mean instantaneous volatility.
    """

    mean_rate = rate_paths.mean(axis=0)

    mean_vol = np.sqrt(
        variance_paths
    ).mean(axis=0)

    plt.figure(figsize=(10, 6))
    plt.plot(times, mean_rate)
    plt.title("Mean Short Rate")
    plt.xlabel("Time")
    plt.ylabel("Short Rate")
    plt.grid()
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(times, mean_vol)
    plt.title("Mean Instantaneous Volatility")
    plt.xlabel("Time")
    plt.ylabel("Volatility")
    plt.grid()
    plt.show()


def plot_terminal_distributions(
    rate_paths,
    variance_paths
):
    """
    Plot terminal rate and volatility distributions.
    """

    final_rates = rate_paths[:, -1]

    final_vols = np.sqrt(
        variance_paths[:, -1]
    )

    plt.figure(figsize=(10, 6))
    plt.hist(final_rates, bins=50)
    plt.title("Terminal Short-Rate Distribution")
    plt.xlabel("Short Rate")
    plt.ylabel("Frequency")
    plt.grid()
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.hist(final_vols, bins=50)
    plt.title("Terminal Volatility Distribution")
    plt.xlabel("Volatility")
    plt.ylabel("Frequency")
    plt.grid()
    plt.show()


def plot_constant_vs_stochastic_vol_rates(
    times,
    constant_paths,
    stochastic_paths
):
    """
    Compare mean short-rate paths under constant-vol and stochastic-vol models.
    """

    plt.figure(figsize=(10, 6))

    plt.plot(
        times,
        constant_paths.mean(axis=0),
        label="Constant-Vol Hull-White"
    )

    plt.plot(
        times,
        stochastic_paths.mean(axis=0),
        label="Stochastic-Vol Short Rate"
    )

    plt.title(
        "Mean Short Rate: Constant Vol vs Stochastic Vol"
    )

    plt.xlabel("Time")
    plt.ylabel("Mean Short Rate")
    plt.grid()
    plt.legend()
    plt.show()