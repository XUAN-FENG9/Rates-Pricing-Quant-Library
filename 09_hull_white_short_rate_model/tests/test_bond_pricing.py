import sys
sys.path.append("../python")
sys.path.append("../../06_black_swaption_pricing/python")

from market_data import load_curve_data
from hull_white_model import HullWhiteModel
from bond_pricing import zero_coupon_bond_price


def test_zero_coupon_price_positive():

    curve = load_curve_data("../data/usd_zero_curve.csv")

    model = HullWhiteModel(
        mean_reversion=0.05,
        volatility=0.01,
        curve=curve
    )

    r = model.instantaneous_forward_rate(1e-6)

    price = zero_coupon_bond_price(
        model,
        0.0,
        5.0,
        r
    )
    
    print(price)

    assert price > 0.0
    assert price < 1.0