import sys
sys.path.append("../python")
sys.path.append("../../06_black_swaption_pricing/python")

from market_data import load_curve_data
from hull_white_model import HullWhiteModel
import numpy as np

def test_B_function_positive():

    curve = load_curve_data("../data/usd_zero_curve.csv")

    model = HullWhiteModel(
        mean_reversion=0.05,
        volatility=0.01,
        curve=curve
    )

    B = model.B(
        1.0,
        5.0
    )
    
    print(B)

    assert B > 0.0


def test_theta_finite():

    curve = load_curve_data("../data/usd_zero_curve.csv")

    model = HullWhiteModel(
        mean_reversion=0.05,
        volatility=0.01,
        curve=curve
    )

    theta = model.theta(2.0)
    
    print(theta)

    assert np.isfinite(theta)
    assert abs(theta) < 1.0