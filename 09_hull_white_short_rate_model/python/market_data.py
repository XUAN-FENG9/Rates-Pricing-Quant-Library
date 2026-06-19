"""
market_data.py

Market data utilities for Chapter 09.

This chapter reuses the same curve data convention as previous chapters.

The curve is used as the initial discount curve that the Hull-White model
must fit exactly.
"""

import pandas as pd
import numpy as np

from curve import YieldCurve


def load_curve_data(file_path="../data/usd_zero_curve.csv"):
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

    maturities = df["maturity"].values
    zero_rates = df["zero_rate"].values

    return YieldCurve(
        maturities,
        zero_rates
    )


def curve_to_dataframe(curve, times):
    """
    Convert discount curve information into a DataFrame.

    Parameters
    ----------
    curve : YieldCurve
        Yield curve object.

    times : array-like
        Times at which to evaluate the curve.

    Returns
    -------
    pandas.DataFrame
        Table of discount factors and zero rates.
    """

    rows = []

    for t in times:

        df = curve.discount_factor(t)

        zero = curve.zero_rate(t)

        rows.append(
            {
                "time": t,
                "discount_factor": df,
                "zero_rate": zero
            }
        )

    return pd.DataFrame(rows)