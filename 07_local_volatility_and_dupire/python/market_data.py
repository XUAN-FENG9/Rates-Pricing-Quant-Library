"""
market_data.py

Load and clean Chapter 07 market data.

Raw swaption quotes are given in bp:
- strike_shift_bp
- black_vol_bp

This module converts them into:
- actual strike levels
- decimal Black volatilities
- a common strike grid suitable for Dupire finite differences
"""

import numpy as np
import pandas as pd

from curve import YieldCurve
from forward_swap import ForwardStartingSwap


def load_curve_data(file_path="../data/curve_data.csv"):
    """
    Load zero curve data and return a YieldCurve object.
    """

    df = pd.read_csv(file_path)

    return YieldCurve(
        df["tenor"].values,
        df["zero_rate"].values
    )


def load_raw_swaption_quotes(file_path="../data/swaption_vol_surface.csv"):
    """
    Load raw swaption quote CSV.
    """

    return pd.read_csv(file_path)


def clean_swaption_quotes(raw_df, curve, target_tenor=5.0):
    """
    Convert bp market quotes into decimal actual-strike quotes.

    Output columns:
    - expiry
    - tenor
    - forward_swap_rate
    - strike_shift_bp
    - strike
    - black_vol
    """

    rows = []

    df = raw_df[
        raw_df["tenor"] == target_tenor
    ].copy()

    for _, row in df.iterrows():

        expiry = float(row["expiry"])
        tenor = float(row["tenor"])

        swap = ForwardStartingSwap(
            notional=1.0,
            fixed_rate=None,
            start=expiry,
            end=expiry + tenor,
            payment_frequency=2
        )

        forward = swap.forward_swap_rate(curve)

        strike = (
            forward
            + float(row["strike_shift_bp"]) / 10000.0
        )

        black_vol = (
            float(row["black_vol_bp"]) / 10000.0
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


def build_common_strike_grid(clean_quotes, num_strikes=5):
    """
    Build a common actual-strike grid.

    This is required because Dupire needs C(T,K)
    evaluated at the same strike values across expiries.

    We use the intersection of all expiry strike ranges.
    """

    lows = []
    highs = []

    for expiry in clean_quotes["expiry"].unique():

        sub = clean_quotes[
            clean_quotes["expiry"] == expiry
        ]

        lows.append(sub["strike"].min())
        highs.append(sub["strike"].max())

    lower = max(lows)
    upper = min(highs)

    if lower >= upper:
        raise ValueError(
            "No overlapping strike range across expiries. "
            "Increase strike quote width in market data."
        )

    return np.linspace(
        lower,
        upper,
        num_strikes
    )