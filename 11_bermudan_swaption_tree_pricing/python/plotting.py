"""
plotting.py

Plotting utilities for Bermudan swaption tree pricing.
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_short_rate_tree(
    tree
):
    """
    Plot Hull-White short-rate tree nodes.
    """

    plt.figure(figsize=(10, 6))

    for step, t in enumerate(tree.times):

        xs = np.full(
            step + 1,
            t
        )

        ys = tree.rates[step]

        plt.scatter(
            xs,
            ys
        )

    plt.title(
        "Hull-White Short-Rate Tree"
    )

    plt.xlabel("Time")
    plt.ylabel("Short Rate")
    plt.grid()
    plt.show()


def plot_tree_values(
    tree,
    value_tree,
    title="Bermudan Swaption Value Tree"
):
    """
    Plot Bermudan swaption value tree.
    """

    plt.figure(figsize=(10, 6))

    for step, t in enumerate(tree.times):

        xs = np.full(
            step + 1,
            t
        )

        ys = value_tree[step]

        plt.scatter(
            xs,
            ys
        )

    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Option Value")
    plt.grid()
    plt.show()


def plot_exercise_boundary(
    tree,
    exercise_tree
):
    """
    Plot nodes where early exercise is optimal.
    """

    plt.figure(figsize=(10, 6))

    for step, t in enumerate(tree.times):

        flags = exercise_tree[step]

        if np.any(flags):

            rates = tree.rates[step][flags]

            xs = np.full(
                len(rates),
                t
            )

            plt.scatter(
                xs,
                rates,
                marker="x",
                s=80
            )

    plt.title(
        "Bermudan Swaption Exercise Nodes"
    )

    plt.xlabel("Exercise Time")
    plt.ylabel("Short Rate")
    plt.grid()
    plt.show()