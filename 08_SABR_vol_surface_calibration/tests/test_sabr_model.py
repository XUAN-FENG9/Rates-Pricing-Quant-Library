
import sys
sys.path.append("../python")


"""
test_sabr_model.py

Basic SABR model tests.
"""

from sabr_model import hagan_sabr_black_vol


def test_sabr_vol_positive():

    vol = hagan_sabr_black_vol(
        forward=0.04,
        strike=0.04,
        expiry=5.0,
        alpha=0.04,
        beta=0.5,
        rho=-0.25,
        nu=0.50
    )
    
    print(vol)

    assert vol > 0.0