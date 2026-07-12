# ✝ In memory of my beloved grandfather - Heshun Feng (冯和顺), who passed away today (11th July 2026)
# His love and encouragement will forever inspire me.


"""
plotting.py

Plotting utilities for Chapter 13.
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_initial_forward_curve(
    tenor_structure,
    initial_forwards
):
    """
    Plot initial discrete forward curve.
    """

    plt.figure(figsize=(10, 6))

    plt.plot(
        tenor_structure.times[:-1],
        initial_forwards,
        marker="o"
    )

    plt.title(
        "Initial LMM Forward Curve"
    )

    plt.xlabel(
        "Forward Reset Time"
    )

    plt.ylabel(
        "Forward Rate"
    )

    plt.grid()
    plt.show()


def plot_forward_paths(
    times,
    forward_paths,
    forward_index,
    n_plot=30
):
    """
    Plot simulated paths for one forward rate.
    """

    plt.figure(figsize=(10, 6))

    for path in range(
        min(
            n_plot,
            forward_paths.shape[0]
        )
    ):

        plt.plot(
            times,
            forward_paths[
                path,
                :,
                forward_index
            ]
        )

    plt.title(
        f"Simulated Forward Rate L[{forward_index}]"
    )

    plt.xlabel("Time")
    plt.ylabel("Forward Rate")
    plt.grid()
    plt.show()


def plot_terminal_forward_distribution(
    times,
    forward_paths,
    forward_index,
    target_time
):
    """
    Plot forward-rate distribution at a selected time.
    """

    index = int(
        np.argmin(
            np.abs(
                times
                -
                target_time
            )
        )
    )

    values = forward_paths[
        :,
        index,
        forward_index
    ]

    plt.figure(figsize=(10, 6))

    plt.hist(
        values,
        bins=50
    )

    plt.title(
        f"Forward L[{forward_index}] Distribution at t={target_time}"
    )

    plt.xlabel("Forward Rate")
    plt.ylabel("Frequency")
    plt.grid()
    plt.show()


def plot_correlation_matrix(
    correlation_matrix
):
    """
    Plot forward-rate correlation matrix.
    """

    plt.figure(figsize=(8, 7))

    plt.imshow(
        correlation_matrix,
        aspect="auto"
    )

    plt.colorbar(
        label="Correlation"
    )

    plt.title(
        "LMM Forward-Rate Correlation Matrix"
    )

    plt.xlabel("Forward Index")
    plt.ylabel("Forward Index")
    plt.show()


def plot_mean_forward_surface(
    times,
    tenor_structure,
    forward_paths
):
    """
    Plot mean simulated forward-rate surface.
    """

    mean_surface = forward_paths.mean(
        axis=0
    )

    X, Y = np.meshgrid(
        tenor_structure.times[:-1],
        times
    )

    fig = plt.figure(
        figsize=(10, 6)
    )

    ax = fig.add_subplot(
        111,
        projection="3d"
    )

    ax.plot_surface(
        X,
        Y,
        mean_surface,
        cmap="viridis"
    )

    ax.set_title(
        "Mean Simulated Forward-Rate Surface"
    )

    ax.set_xlabel(
        "Forward Reset Time"
    )

    ax.set_ylabel(
        "Simulation Time"
    )

    ax.set_zlabel(
        "Forward Rate"
    )

    plt.show()