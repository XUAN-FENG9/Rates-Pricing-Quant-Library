"""
plotting.py

Plotting utilities for Chapter 07.
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_surface(expiries, strikes, values, title, zlabel):
    """
    Generic 3D surface plot.
    """

    X, Y = np.meshgrid(strikes, expiries)

    fig = plt.figure(figsize=(10, 6))

    ax = fig.add_subplot(
        111,
        projection="3d"
    )

    ax.plot_surface(
        X,
        Y,
        values,
        cmap="viridis"
    )

    ax.set_title(title)
    ax.set_xlabel("Strike")
    ax.set_ylabel("Expiry")
    ax.set_zlabel(zlabel)

    plt.show()


def plot_implied_vol_surface(vol_surface):
    """
    Plot implied volatility surface.
    """

    plot_surface(
        vol_surface.expiries,
        vol_surface.strikes,
        vol_surface.vols_from_quotes(),
        "Black Implied Volatility Surface",
        "Black Vol"
    )


def plot_price_surface(price_surface):
    """
    Plot swaption price surface.
    """

    plot_surface(
        price_surface.expiries,
        price_surface.strikes,
        price_surface.price_matrix,
        "Swaption Price Surface",
        "Price"
    )


def plot_local_vol_surface(local_vol_surface):
    """
    Plot Dupire local volatility surface.
    """

    plot_surface(
        local_vol_surface.expiries,
        local_vol_surface.strikes,
        local_vol_surface.local_vol_matrix,
        "Dupire Local Volatility Surface",
        "Local Vol"
    )