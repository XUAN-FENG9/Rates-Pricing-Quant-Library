
import sys
sys.path.append("../python")

"""
test_sabr_surface.py

End-to-end SABR surface calibration test.
"""

from market_data import (
    load_curve_data,
    load_raw_swaption_quotes,
    clean_swaption_quotes
)

from sabr_surface import SABRSurface


def test_sabr_surface():

    curve = load_curve_data(
        "../data/curve_data.csv"
    )

    raw = load_raw_swaption_quotes(
        "../data/swaption_vol_surface.csv"
    )

    clean = clean_swaption_quotes(
        raw,
        curve,
        target_tenor=5.0
    )

    sabr_surface = SABRSurface(
        clean,
        beta=0.5
    )

    table = sabr_surface.calibrate()
    
    print(table)

    assert len(table) > 0
    assert table["alpha"].min() > 0.0
    assert table["nu"].min() > 0.0