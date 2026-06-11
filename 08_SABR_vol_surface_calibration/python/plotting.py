"""
plotting.py

Plotting utilities for SABR calibration.
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_sabr_fit(
    strikes,
    market_vols,
    fitted_vols,
    expiry
):
    """
    Plot market vols versus SABR-fitted vols.
    """

    plt.figure(figsize=(10, 6))

    plt.plot(
        strikes,
        market_vols,
        marker="o",
        label="Market Vol"
    )

    plt.plot(
        strikes,
        fitted_vols,
        marker="x",
        label="SABR Fit"
    )

    plt.title(
        f"SABR Smile Fit — Expiry {expiry}Y"
    )

    plt.xlabel("Strike")
    plt.ylabel("Black Vol")
    plt.grid()
    plt.legend()
    plt.show()


def plot_parameter_term_structure(
    parameter_table
):
    """
    Plot SABR parameters across expiries.
    """

    for col in ["alpha", "rho", "nu", "rmse"]:

        plt.figure(figsize=(10, 6))

        plt.plot(
            parameter_table["expiry"],
            parameter_table[col],
            marker="o"
        )

        plt.title(
            f"SABR {col} Term Structure"
        )

        plt.xlabel("Expiry")
        plt.ylabel(col)
        plt.grid()
        plt.show()


def plot_surface(
    expiries,
    strikes,
    values,
    title,
    zlabel
):
    """
    Generic 3D surface plot.

    Parameters
    ----------
    expiries : array-like
        Expiry grid.

    strikes : array-like
        Strike grid. In Chapter 08 we usually use strike_shift_bp.

    values : np.ndarray
        Surface values with shape:

            rows = expiries
            columns = strikes

    title : str
        Plot title.

    zlabel : str
        Label for z-axis.
    """

    X, Y = np.meshgrid(
        strikes,
        expiries
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
        values,
        cmap="viridis"
    )

    ax.set_title(title)

    ax.set_xlabel(
        "Strike Shift from ATM (bp)"
    )

    ax.set_ylabel(
        "Expiry"
    )

    ax.set_zlabel(zlabel)

    plt.show()


def build_market_vol_matrix(
    clean_quotes_df
):
    """
    Build rectangular market implied vol matrix.

    Rows:
        expiries

    Columns:
        strike_shift_bp

    Returns
    -------
    expiries : np.ndarray
    strike_shifts : np.ndarray
    market_matrix : np.ndarray
    """

    expiries = np.array(
        sorted(
            clean_quotes_df["expiry"].unique()
        )
    )

    strike_shifts = np.array(
        sorted(
            clean_quotes_df["strike_shift_bp"].unique()
        )
    )

    matrix = np.full(
        (
            len(expiries),
            len(strike_shifts)
        ),
        np.nan
    )

    for i, expiry in enumerate(expiries):

        sub = clean_quotes_df[
            clean_quotes_df["expiry"] == expiry
        ]

        for j, shift in enumerate(strike_shifts):

            match = sub[
                sub["strike_shift_bp"] == shift
            ]

            if len(match) > 0:

                matrix[i, j] = (
                    match["black_vol"]
                    .iloc[0]
                )

    return expiries, strike_shifts, matrix


def build_sabr_vol_matrix(
    clean_quotes_df,
    sabr_surface
):
    """
    Build rectangular SABR fitted vol matrix.

    The matrix is aligned with the same expiry × strike_shift_bp grid
    used by the market vol matrix.

    For each quote:
    - use the actual strike for SABR formula evaluation
    - store the result in the strike_shift_bp grid location
    """

    expiries = np.array(
        sorted(
            clean_quotes_df["expiry"].unique()
        )
    )

    strike_shifts = np.array(
        sorted(
            clean_quotes_df["strike_shift_bp"].unique()
        )
    )

    matrix = np.full(
        (
            len(expiries),
            len(strike_shifts)
        ),
        np.nan
    )

    for i, expiry in enumerate(expiries):

        result = sabr_surface.calibrations[
            expiry
        ]

        quoted_strikes = result["strikes"]
        fitted_vols = result["fitted_vols"]

        sub = clean_quotes_df[
            clean_quotes_df["expiry"] == expiry
        ]

        for j, shift in enumerate(strike_shifts):

            match = sub[
                sub["strike_shift_bp"] == shift
            ]

            if len(match) > 0:

                actual_strike = (
                    match["strike"]
                    .iloc[0]
                )

                idx = np.argmin(
                    np.abs(
                        quoted_strikes
                        - actual_strike
                    )
                )

                matrix[i, j] = fitted_vols[idx]

    return expiries, strike_shifts, matrix


def plot_market_vol_surface(
    clean_quotes_df
):
    """
    Plot market implied volatility surface.
    """

    expiries, strike_shifts, market_matrix = (
        build_market_vol_matrix(
            clean_quotes_df
        )
    )

    plot_surface(
        expiries,
        strike_shifts,
        market_matrix,
        "Market Implied Volatility Surface",
        "Market Black Vol"
    )


def plot_sabr_surface(
    clean_quotes_df,
    sabr_surface
):
    """
    Plot SABR fitted volatility surface.
    """

    expiries, strike_shifts, sabr_matrix = (
        build_sabr_vol_matrix(
            clean_quotes_df,
            sabr_surface
        )
    )

    plot_surface(
        expiries,
        strike_shifts,
        sabr_matrix,
        "SABR Fitted Volatility Surface",
        "SABR Black Vol"
    )


def plot_sabr_residual_surface(
    clean_quotes_df,
    sabr_surface
):
    """
    Plot SABR residual volatility surface.

    Residual:

        SABR fitted vol - market vol

    A good calibration should have residuals close to zero.
    """

    expiries, strike_shifts, market_matrix = (
        build_market_vol_matrix(
            clean_quotes_df
        )
    )

    _, _, sabr_matrix = (
        build_sabr_vol_matrix(
            clean_quotes_df,
            sabr_surface
        )
    )

    residual_matrix = (
        sabr_matrix
        -
        market_matrix
    )

    plot_surface(
        expiries,
        strike_shifts,
        residual_matrix,
        "SABR Calibration Residual Surface",
        "SABR Vol - Market Vol"
    )