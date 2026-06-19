"""
option_pricing.py

Bond option pricing under the Hull-White model.

This file includes:

1. Analytic zero-coupon bond option approximation
2. Monte Carlo bond option pricing
"""

import numpy as np
from scipy.stats import norm

from bond_pricing import zero_coupon_bond_price


def bond_option_volatility(
    model,
    option_expiry,
    bond_maturity
):
    """
    Effective volatility of a zero-coupon bond option under Hull-White.

    The variance of log bond price under the appropriate measure is:

        sigma_P^2
        =
        sigma^2
        *
        (1 - exp(-2 a tau)) / (2a)
        *
        B(tau, T)^2

    where tau is option expiry.

    Parameters
    ----------
    model : HullWhiteModel
        Hull-White model.

    option_expiry : float
        Option expiry.

    bond_maturity : float
        Underlying zero-coupon bond maturity.

    Returns
    -------
    float
        Bond option volatility.
    """

    a = model.a
    sigma = model.sigma
    tau = option_expiry

    B_tau_T = model.B(
        option_expiry,
        bond_maturity
    )

    if abs(a) < 1e-12:
        variance = (
            sigma
            *
            sigma
            *
            tau
            *
            B_tau_T
            *
            B_tau_T
        )
    else:
        variance = (
            sigma
            *
            sigma
            *
            (
                1.0
                -
                np.exp(
                    -2.0 * a * tau
                )
            )
            /
            (2.0 * a)
            *
            B_tau_T
            *
            B_tau_T
        )

    return np.sqrt(
        variance
    )


def price_zero_coupon_bond_option(
    model,
    option_expiry,
    bond_maturity,
    strike,
    option_type="call"
):
    """
    Analytic European option on a zero-coupon bond.

    The option payoff at option expiry tau is:

        max(P(tau,T) - K, 0)

    for a call option.

    Parameters
    ----------
    model : HullWhiteModel
        Hull-White model.

    option_expiry : float
        Option expiry tau.

    bond_maturity : float
        Underlying bond maturity T.

    strike : float
        Strike price.

    option_type : str
        "call" or "put".

    Returns
    -------
    float
        Option price.
    """

    tau = option_expiry

    P0_tau = model.curve.discount_factor(tau)
    P0_T = model.curve.discount_factor(bond_maturity)

    sigma_P = bond_option_volatility(
        model,
        option_expiry,
        bond_maturity
    )

    if sigma_P < 1e-12:

        intrinsic_call = max(
            P0_T
            -
            strike * P0_tau,
            0.0
        )

        intrinsic_put = max(
            strike * P0_tau
            -
            P0_T,
            0.0
        )

        return (
            intrinsic_call
            if option_type == "call"
            else intrinsic_put
        )

    h = (
        np.log(
            P0_T
            /
            (
                strike
                *
                P0_tau
            )
        )
        /
        sigma_P
        +
        0.5
        *
        sigma_P
    )

    if option_type == "call":

        return (
            P0_T
            *
            norm.cdf(h)
            -
            strike
            *
            P0_tau
            *
            norm.cdf(
                h - sigma_P
            )
        )

    elif option_type == "put":

        return (
            strike
            *
            P0_tau
            *
            norm.cdf(
                -h + sigma_P
            )
            -
            P0_T
            *
            norm.cdf(-h)
        )

    else:
        raise ValueError(
            "option_type must be 'call' or 'put'."
        )


def monte_carlo_bond_option_price(
    model,
    times,
    short_rate_paths,
    option_expiry,
    bond_maturity,
    strike,
    option_type="call"
):
    """
    Monte Carlo price of a zero-coupon bond option.

    This function prices the payoff:

        max(P(tau,T) - K, 0)

    at option expiry tau and discounts it back pathwise.

    Parameters
    ----------
    model : HullWhiteModel
        Hull-White model.

    times : np.ndarray
        Simulation time grid.

    short_rate_paths : np.ndarray
        Short-rate paths.

    option_expiry : float
        Option expiry.

    bond_maturity : float
        Bond maturity.

    strike : float
        Bond option strike.

    option_type : str
        "call" or "put".

    Returns
    -------
    float
        Monte Carlo option price.
    """

    idx = np.argmin(
        np.abs(
            times
            -
            option_expiry
        )
    )

    dt = times[1] - times[0]

    discounted_payoffs = []

    for path in range(
        short_rate_paths.shape[0]
    ):

        r_tau = short_rate_paths[
            path,
            idx
        ]

        P_tau_T = zero_coupon_bond_price(
            model,
            option_expiry,
            bond_maturity,
            r_tau
        )

        if option_type == "call":

            payoff = max(
                P_tau_T
                -
                strike,
                0.0
            )

        else:

            payoff = max(
                strike
                -
                P_tau_T,
                0.0
            )

        discount_integral = np.sum(
            short_rate_paths[
                path,
                :idx
            ]
        ) * dt

        discount_factor = np.exp(
            -discount_integral
        )

        discounted_payoffs.append(
            discount_factor
            *
            payoff
        )

    return float(
        np.mean(
            discounted_payoffs
        )
    )