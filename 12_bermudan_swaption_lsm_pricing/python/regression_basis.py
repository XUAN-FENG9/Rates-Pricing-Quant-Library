"""
regression_basis.py

Regression basis functions for Longstaff-Schwartz Bermudan swaption pricing.
"""

import numpy as np


def polynomial_basis(
    x,
    degree=2
):
    """
    Polynomial regression basis.

    Parameters
    ----------
    x : np.ndarray
        State variable, usually short rate or swap rate.

    degree : int
        Polynomial degree.

    Returns
    -------
    np.ndarray
        Design matrix.
    """

    x = np.asarray(x)

    columns = [
        np.ones_like(x)
    ]

    for d in range(1, degree + 1):

        columns.append(
            x ** d
        )

    return np.column_stack(
        columns
    )


def rate_and_swap_basis(
    short_rates,
    swap_rates,
    degree=2
):
    """
    Regression basis using both short rate and swap rate.

    This is useful because the continuation value of a Bermudan swaption
    depends on both the short-rate state and the moneyness of the swap.
    """

    r = np.asarray(short_rates)
    s = np.asarray(swap_rates)

    columns = [
        np.ones_like(r),
        r,
        s,
        r * s
    ]

    if degree >= 2:

        columns.extend(
            [
                r ** 2,
                s ** 2
            ]
        )

    if degree >= 3:

        columns.extend(
            [
                r ** 3,
                s ** 3,
                (r ** 2) * s,
                r * (s ** 2)
            ]
        )

    return np.column_stack(
        columns
    )