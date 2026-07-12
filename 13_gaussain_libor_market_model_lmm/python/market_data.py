# ✝ In memory of my beloved grandfather - Heshun Feng (冯和顺), who passed away today (11th July 2026)
# His love and encouragement will forever inspire me.

"""
market_data.py

Market-data utilities for Chapter 13.

This chapter reuses the yield-curve infrastructure from Chapter 09.
The initial discount curve is converted into a discrete set of forward
rates on the LMM tenor grid.
"""

import pandas as pd

from curve import YieldCurve


def load_curve_data(
    file_path
):
    """
    Load zero-curve data.

    Expected columns
    ----------------
    tenor
        Maturity in years.

    zero_rate
        Continuously compounded zero rate in decimal form.

    Parameters
    ----------
    file_path : str
        Path to the zero-curve CSV file.

    Returns
    -------
    YieldCurve
        YieldCurve object reused from previous chapters.
    """

    data = pd.read_csv(
        file_path
    )

    required_columns = {
        "maturity",
        "zero_rate"
    }

    missing = (
        required_columns
        -
        set(data.columns)
    )

    if missing:
        raise ValueError(
            f"Missing curve columns: {missing}"
        )

    return YieldCurve(
        data["maturity"].to_numpy(),
        data["zero_rate"].to_numpy()
    )