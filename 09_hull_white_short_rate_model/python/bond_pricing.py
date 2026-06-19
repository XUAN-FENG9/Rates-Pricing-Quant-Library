"""
bond_pricing.py

Zero-coupon bond pricing under the Hull-White model.

The Hull-White model is affine:

    P(t,T) = A(t,T) exp(-B(t,T) r(t))

This file implements the A and B functions and bond pricing.
"""

import numpy as np


def A_function(
    model,
    t,
    T
):
    """
    Compute Hull-White A(t,T).

    A(t,T) is chosen so that the model fits the initial discount curve.

    A common expression is:

        A(t,T)
        =
        P(0,T) / P(0,t)
        *
        exp(
            B(t,T) f(0,t)
            - sigma^2 / (4a) * (1 - exp(-2at)) * B(t,T)^2
        )

    Parameters
    ----------
    model : HullWhiteModel
        Hull-White model object.

    t : float
        Current time.

    T : float
        Maturity.

    Returns
    -------
    float
        A(t,T).
    """

    if T < t:
        raise ValueError("T must be greater than or equal to t.")

    P0T = model.curve.discount_factor(T)
    P0t = model.curve.discount_factor(t)

    B = model.B(t, T)

    f0t = model.instantaneous_forward_rate(t)

    a = model.a
    sigma = model.sigma

    if abs(a) < 1e-12:
        variance_adjustment = (
            0.5
            *
            sigma
            *
            sigma
            *
            t
            *
            B
            *
            B
        )
    else:
        variance_adjustment = (
            sigma
            *
            sigma
            /
            (4.0 * a)
            *
            (
                1.0
                -
                np.exp(
                    -2.0 * a * t
                )
            )
            *
            B
            *
            B
        )

    return (
        P0T
        /
        P0t
        *
        np.exp(
            B * f0t
            -
            variance_adjustment
        )
    )


def zero_coupon_bond_price(
    model,
    t,
    T,
    r_t
):
    """
    Hull-White zero-coupon bond price.

    Formula:

        P(t,T) = A(t,T) exp(-B(t,T) r_t)

    Parameters
    ----------
    model : HullWhiteModel
        Hull-White model.

    t : float
        Current time.

    T : float
        Bond maturity.

    r_t : float
        Short rate at time t.

    Returns
    -------
    float
        Zero-coupon bond price.
    """

    A = A_function(
        model,
        t,
        T
    )

    B = model.B(
        t,
        T
    )

    return (
        A
        *
        np.exp(
            -B * r_t
        )
    )


def check_initial_curve_fit(
    model,
    maturities
):
    """
    Check whether Hull-White bond pricing reproduces initial curve at t=0.

    At t=0, the model should satisfy:

        P_HW(0,T) = P_market(0,T)

    Parameters
    ----------
    model : HullWhiteModel
        Hull-White model.

    maturities : array-like
        Maturities to test.

    Returns
    -------
    pandas.DataFrame
        Market and model discount factors.
    """

    import pandas as pd

    rows = []

    r0 = model.instantaneous_forward_rate(
        1e-6
    )

    for T in maturities:

        market_df = model.curve.discount_factor(T)

        model_df = zero_coupon_bond_price(
            model,
            0.0,
            T,
            r0
        )

        rows.append(
            {
                "maturity": T,
                "market_df": market_df,
                "model_df": model_df,
                "difference": model_df - market_df
            }
        )

    return pd.DataFrame(rows)