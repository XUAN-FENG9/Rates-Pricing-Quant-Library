import sys
sys.path.append("../python")
sys.path.append("../../09_hull_white_short_rate_model/python")

from market_data import load_curve_data
from hull_white_model import HullWhiteModel
from stochastic_vol_model import StochasticVolShortRateModel


def test_model_creation():

    curve = load_curve_data(
        "../../09_hull_white_short_rate_model/data/usd_zero_curve.csv"
    )

    hw = HullWhiteModel(
        mean_reversion=0.05,
        volatility=0.01,
        curve=curve
    )

    model = StochasticVolShortRateModel(
        base_hw_model=hw,
        kappa=1.0,
        v_bar=0.0001,
        eta=0.2,
        rho=-0.3
    )
    
    print(model.kappa)
    print(model.v_bar)

    assert model.kappa > 0
    assert model.v_bar > 0