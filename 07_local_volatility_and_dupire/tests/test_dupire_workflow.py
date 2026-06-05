"""
test_dupire_workflow.py

End-to-end integration test for Chapter 07.
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


def test_dupire_workflow():

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
        num_strikes=5
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

    price_matrix = price_surface.build()

    dupire = DupireBuilder(
        price_surface
    )

    local_surface = dupire.build()

    assert price_matrix.shape == (
        len(vol_surface.expiries),
        len(vol_surface.strikes)
    )

    assert local_surface.local_vol_matrix.shape == price_matrix.shape

    finite_local_vols = local_surface.local_vol_matrix[
        ~np.isnan(local_surface.local_vol_matrix)
    ]

    assert len(finite_local_vols) > 0
    assert np.all(finite_local_vols > 0)
