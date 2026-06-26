"""
pricing.py

Pricing functions for stochastic-volatility short-rate models.

Unlike Chapter 09, this model generally does not have simple closed-form
bond option prices. Therefore pricing is primarily Monte Carlo based.
"""

import numpy as np

from stochastic_vol_simulation import (
    path_discount_factors,
    forward_discount_factors
)


def monte_carlo_zero_coupon_bond_price(
    times,
    rate_paths,
    maturity
):
    """
    Price a zero-coupon bond by Monte Carlo.

    The maturity must lie on the simulation grid or close to a grid point.
    """

    idx = np.argmin(
        np.abs(times - maturity)
    )

    dfs = path_discount_factors(
        times,
        rate_paths,
        end_index=idx
    )

    return float(
        np.mean(dfs)
    )


def monte_carlo_bond_option_price(
    times,
    rate_paths,
    option_expiry,
    bond_maturity,
    strike,
    option_type="call"
):
    """
    Price a European option on a zero-coupon bond by Monte Carlo.

    Payoff at option expiry:

        max(P(tau,T) - K, 0)

    We estimate P(tau,T) pathwise using the simulated short-rate path
    from tau to T.
    """

    expiry_idx = np.argmin(
        np.abs(times - option_expiry)
    )

    maturity_idx = np.argmin(
        np.abs(times - bond_maturity)
    )

    if maturity_idx <= expiry_idx:
        raise ValueError(
            "bond_maturity must be greater than option_expiry."
        )

    discount_0_tau = path_discount_factors(
        times,
        rate_paths,
        end_index=expiry_idx
    )

    bond_tau_T = forward_discount_factors(
        times,
        rate_paths,
        start_index=expiry_idx,
        end_index=maturity_idx
    )

    if option_type == "call":

        payoffs = np.maximum(
            bond_tau_T - strike,
            0.0
        )

    elif option_type == "put":

        payoffs = np.maximum(
            strike - bond_tau_T,
            0.0
        )

    else:
        raise ValueError(
            "option_type must be 'call' or 'put'."
        )

    discounted_payoffs = (
        discount_0_tau
        *
        payoffs
    )

    return float(
        np.mean(discounted_payoffs)
    )


def estimate_terminal_statistics(
    rate_paths,
    variance_paths
):
    """
    Return terminal statistics for rates and variance.
    """

    final_rates = rate_paths[:, -1]
    final_variances = variance_paths[:, -1]

    return {
        "rate_mean": float(final_rates.mean()),
        "rate_std": float(final_rates.std()),
        "variance_mean": float(final_variances.mean()),
        "variance_std": float(final_variances.std()),
        "vol_mean": float(np.sqrt(final_variances).mean())
    }