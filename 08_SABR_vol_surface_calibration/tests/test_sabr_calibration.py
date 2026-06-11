
import sys
sys.path.append("../python")


"""
test_sabr_calibration.py

Test SABR calibration for one expiry slice.
"""

from market_data import (
    load_curve_data,
    load_raw_swaption_quotes,
    clean_swaption_quotes,
    get_quotes_for_expiry
)

from sabr_calibration import calibrate_sabr_slice


def test_sabr_calibration():

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

    forward, strikes, market_vols = get_quotes_for_expiry(
        clean,
        expiry=5.0
    )

    result = calibrate_sabr_slice(
        forward=forward,
        strikes=strikes,
        expiry=5.0,
        market_vols=market_vols,
        beta=0.5
    )
    
    print(result)

    assert result["success"] is True
    assert result["alpha"] > 0.0
    assert -1.0 < result["rho"] < 1.0
    assert result["nu"] > 0.0