"""
test_off_grid_local_vol_pricing.py
"""
import sys
sys.path.append("../python")

import numpy as np

from market_data import (
    load_curve_data,
    load_raw_swaption_quotes,
    clean_swaption_quotes,
    build_common_strike_grid
)

from vol_surface import VolSurface
from swaption_price_surface import SwaptionPriceSurface
from dupire_builder import DupireBuilder

from forward_swap import ForwardStartingSwap
from black_swaption import BlackSwaption


def find_valid_off_grid_point(local_surface):
    """
    Find an off-grid point inside a valid local-vol cell.

    We need four surrounding local-vol values to be finite:

        (i, j), (i+1, j)
        (i, j+1), (i+1, j+1)

    Then we choose the midpoint of that cell.
    """

    expiries = local_surface.expiries
    strikes = local_surface.strikes
    vols = local_surface.local_vol_matrix

    for i in range(len(expiries) - 1):

        for j in range(len(strikes) - 1):

            cell = [
                vols[i, j],
                vols[i + 1, j],
                vols[i, j + 1],
                vols[i + 1, j + 1]
            ]

            if all(np.isfinite(x) and x > 0 for x in cell):

                expiry = 0.5 * (
                    expiries[i] + expiries[i + 1]
                )

                strike = 0.5 * (
                    strikes[j] + strikes[j + 1]
                )

                return expiry, strike

    raise ValueError(
        "No valid local-vol interpolation cell found. "
        "Dupire surface may be too sparse or unstable."
    )


def test_off_grid_local_vol_pricing():

    curve = load_curve_data(
        "../data/curve_data.csv"
    )

    raw_quotes = load_raw_swaption_quotes(
        "../data/swaption_vol_surface.csv"
    )

    clean_quotes = clean_swaption_quotes(
        raw_quotes,
        curve,
        target_tenor=5.0
    )

    common_strikes = build_common_strike_grid(
        clean_quotes,
        num_strikes=10
    )

    vol_surface = VolSurface(
        clean_quotes,
        common_strikes
    )

    price_surface = SwaptionPriceSurface(
        curve=curve,
        vol_surface=vol_surface,
        tenor=5.0,
        notional=1.0,
        payer=True
    )

    price_surface.build()

    dupire = DupireBuilder(
        price_surface
    )

    local_surface = dupire.build()

    off_grid_expiry, off_grid_strike = (
        find_valid_off_grid_point(local_surface)
    )

    local_vol = local_surface.get_local_vol(
        off_grid_expiry,
        off_grid_strike
    )

    underlying_swap = ForwardStartingSwap(
        notional=1.0,
        fixed_rate=None,
        start=off_grid_expiry,
        end=off_grid_expiry + 5.0,
        payment_frequency=2
    )

    swaption = BlackSwaption(
        notional=1_000_000,
        strike=off_grid_strike,
        expiry=off_grid_expiry,
        underlying_swap=underlying_swap,
        volatility=local_vol,
        payer=True
    )

    price = swaption.price(curve)
    
    forward = underlying_swap.forward_swap_rate(curve)

    print("Off-grid expiry:", off_grid_expiry)
    print("Off-grid strike:", off_grid_strike)
    print("Forward swap rate:", forward)
    print("Moneyness F-K:", forward - off_grid_strike)
    print("Local vol:", local_vol)
    print("Price:", price)

    assert np.isfinite(local_vol)
    assert local_vol > 0.0
    assert np.isfinite(price)
    assert price > 0.0