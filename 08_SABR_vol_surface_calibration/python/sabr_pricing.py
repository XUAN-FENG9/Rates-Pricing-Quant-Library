"""
sabr_pricing.py

Use calibrated SABR implied volatility to price swaptions.

This module reuses:
- ForwardStartingSwap
- BlackSwaption

from Chapter 06.
"""

from forward_swap import ForwardStartingSwap
from black_swaption import BlackSwaption

from sabr_model import hagan_sabr_black_vol


def price_swaption_with_sabr(
    curve,
    expiry,
    tenor,
    strike,
    notional,
    alpha,
    beta,
    rho,
    nu,
    payer=True
):
    """
    Price a swaption using SABR-implied Black volatility.

    Steps:
    ------
    1. Build forward-starting swap
    2. Compute forward swap rate
    3. Compute SABR Black implied vol
    4. Price using BlackSwaption
    """

    underlying_swap = ForwardStartingSwap(
        notional=notional,
        fixed_rate=None,
        start=expiry,
        end=expiry + tenor,
        payment_frequency=2
    )

    forward = underlying_swap.forward_swap_rate(
        curve
    )

    sabr_vol = hagan_sabr_black_vol(
        forward=forward,
        strike=strike,
        expiry=expiry,
        alpha=alpha,
        beta=beta,
        rho=rho,
        nu=nu
    )

    swaption = BlackSwaption(
        notional=notional,
        strike=strike,
        expiry=expiry,
        underlying_swap=underlying_swap,
        volatility=sabr_vol,
        payer=payer
    )

    price = swaption.price(
        curve
    )

    return {
        "price": price,
        "sabr_vol": sabr_vol,
        "forward": forward
    }