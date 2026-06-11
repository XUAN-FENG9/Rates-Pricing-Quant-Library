"""
market_data.py

Market data loader for Chapter 08 — SABR Vol Surface Calibration.

This file intentionally reuses the same market data convention
as Chapter 07:

- curve_data.csv
- swaption_vol_surface.csv

Raw swaption quotes:
- strike_shift_bp is quoted in basis points relative to ATM
- black_vol_bp is stored as Black vol × 10000

Example:
--------
black_vol_bp = 2100

means:

Black vol = 2100 / 10000 = 0.21 = 21%

This convention is consistent with the Black swaption framework
from Chapter 06.
"""

import pandas as pd
import numpy as np

from curve import YieldCurve
from forward_swap import ForwardStartingSwap


def load_curve_data(file_path="../data/curve_data.csv"):
    """
    Load zero curve data and return a YieldCurve object.

    Parameters
    ----------
    file_path : str
        Path to curve_data.csv.

    Returns
    -------
    YieldCurve
        Yield curve object from previous chapters.
    """

    df = pd.read_csv(file_path)

    maturities = df["tenor"].values
    zero_rates = df["zero_rate"].values

    return YieldCurve(
        maturities,
        zero_rates
    )


def load_raw_swaption_quotes(
    file_path="../data/swaption_vol_surface.csv"
):
    """
    Load raw swaption volatility surface.

    Returns
    -------
    pandas.DataFrame
        Raw quote table.
    """

    return pd.read_csv(file_path)


def clean_swaption_quotes(
    raw_df,
    curve,
    target_tenor=5.0
):
    """
    Convert raw swaption quotes into clean decimal market data.

    For each expiry:
    - build forward-starting swap
    - compute forward swap rate
    - convert strike shift into actual strike
    - convert Black vol from bp-style quote into decimal vol

    Parameters
    ----------
    raw_df : pandas.DataFrame
        Raw swaption quote table.

    curve : YieldCurve
        Yield curve object.

    target_tenor : float
        Underlying swap tenor.

    Returns
    -------
    pandas.DataFrame
        Clean quote table with:
        expiry, tenor, forward_swap_rate, strike_shift_bp, strike, black_vol
    """

    rows = []

    df = raw_df[
        raw_df["tenor"] == target_tenor
    ].copy()

    for _, row in df.iterrows():

        expiry = float(row["expiry"])
        tenor = float(row["tenor"])

        underlying_swap = ForwardStartingSwap(
            notional=1.0,
            fixed_rate=None,
            start=expiry,
            end=expiry + tenor,
            payment_frequency=2
        )

        forward = underlying_swap.forward_swap_rate(
            curve
        )

        strike_shift = (
            float(row["strike_shift_bp"])
            / 10000.0
        )

        strike = forward + strike_shift

        black_vol = (
            float(row["black_vol_bp"])
            / 10000.0
        )

        rows.append(
            {
                "expiry": expiry,
                "tenor": tenor,
                "forward_swap_rate": forward,
                "strike_shift_bp": float(row["strike_shift_bp"]),
                "strike": strike,
                "black_vol": black_vol
            }
        )

    return pd.DataFrame(rows)


def get_quotes_for_expiry(
    clean_df,
    expiry
):
    """
    Extract all strikes and vols for one expiry.

    Parameters
    ----------
    clean_df : pandas.DataFrame
        Clean quote table.

    expiry : float
        Option expiry.

    Returns
    -------
    forward : float
        Forward swap rate for this expiry.

    strikes : np.ndarray
        Actual strike levels.

    market_vols : np.ndarray
        Market Black implied vols.
    """

    sub = clean_df[
        np.isclose(clean_df["expiry"], expiry)
    ].copy()

    sub = sub.sort_values(
        "strike"
    )

    if len(sub) == 0:
        raise ValueError(
            f"No quotes found for expiry={expiry}"
        )

    forward = float(
        sub["forward_swap_rate"].iloc[0]
    )

    strikes = sub["strike"].values
    market_vols = sub["black_vol"].values

    return forward, strikes, market_vols