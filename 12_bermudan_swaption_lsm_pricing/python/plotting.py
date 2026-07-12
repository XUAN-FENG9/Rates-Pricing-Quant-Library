"""
plotting.py

Plotting utilities for Bermudan swaption LSM pricing.
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
        min(
            n_plot,
            rate_paths.shape[0]
        )
    ):

        plt.plot(
            times,
            rate_paths[i]
        )

    plt.title("Simulated Hull-White Short-Rate Paths")
    plt.xlabel("Time")
    plt.ylabel("Short Rate")
    plt.grid()
    plt.show()


def plot_exercise_distribution(
    exercise_df
):
    """
    Plot exercise distribution.
    """

    df = exercise_df.dropna(
        subset=["time"]
    )

    plt.figure(figsize=(10, 6))

    plt.bar(
        df["time"],
        df["exercise_ratio"],
        width=0.4
    )

    plt.title("LSM Exercise Distribution")
    plt.xlabel("Exercise Time")
    plt.ylabel("Exercise Ratio")
    plt.grid()
    plt.show()


def plot_price_sensitivity(
    df,
    x_col,
    y_col="price",
    title="Price Sensitivity"
):
    """
    Generic sensitivity plot.
    """

    plt.figure(figsize=(10, 6))

    plt.plot(
        df[x_col],
        df[y_col],
        marker="o"
    )

    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.grid()
    plt.show()


def plot_regression_path_counts(
    regression_df
):
    """
    Plot number of regression paths by exercise date.
    """

    plt.figure(figsize=(10, 6))

    plt.plot(
        regression_df["exercise_time"],
        regression_df["n_regression_paths"],
        marker="o"
    )

    plt.title("Number of Regression Paths by Exercise Date")
    plt.xlabel("Exercise Time")
    plt.ylabel("Number of ITM Regression Paths")
    plt.grid()
    plt.show()