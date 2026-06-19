"""
plotting.py

Plotting utilities for Chapter 09.
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_short_rate_paths(
    times,
    paths,
    n_plot=20
):
    """
    Plot simulated short-rate paths.

    Parameters
    ----------
    times : np.ndarray
        Time grid.

    paths : np.ndarray
        Short-rate paths.

    n_plot : int
        Number of paths to plot.
    """

    plt.figure(figsize=(10, 6))

    for i in range(
        min(
            n_plot,
            paths.shape[0]
        )
    ):

        plt.plot(
            times,
            paths[i]
        )

    plt.title(
        "Hull-White Simulated Short-Rate Paths"
    )

    plt.xlabel("Time")
    plt.ylabel("Short Rate")
    plt.grid()
    plt.show()


def plot_mean_short_rate(
    times,
    paths
):
    """
    Plot average simulated short rate.
    """

    mean_path = paths.mean(axis=0)

    plt.figure(figsize=(10, 6))

    plt.plot(
        times,
        mean_path,
        marker="o"
    )

    plt.title(
        "Mean Simulated Short Rate"
    )

    plt.xlabel("Time")
    plt.ylabel("Short Rate")
    plt.grid()
    plt.show()


def plot_curve_fit(
    fit_df
):
    """
    Plot market vs model discount factors.
    """

    plt.figure(figsize=(10, 6))

    plt.plot(
        fit_df["maturity"],
        fit_df["market_df"],
        marker="o",
        label="Market DF"
    )

    plt.plot(
        fit_df["maturity"],
        fit_df["model_df"],
        marker="x",
        label="Hull-White DF"
    )

    plt.title(
        "Initial Curve Fit"
    )

    plt.xlabel("Maturity")
    plt.ylabel("Discount Factor")
    plt.grid()
    plt.legend()
    plt.show()


def plot_calibration_errors(
    fit_df
):
    """
    Plot discount factor fitting errors.
    """

    plt.figure(figsize=(10, 6))

    plt.plot(
        fit_df["maturity"],
        fit_df["difference"],
        marker="o"
    )

    plt.axhline(
        0.0,
        linestyle="--"
    )

    plt.title(
        "Initial Curve Fit Error"
    )

    plt.xlabel("Maturity")
    plt.ylabel("Model DF - Market DF")
    plt.grid()
    plt.show()