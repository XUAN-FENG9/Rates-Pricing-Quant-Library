import sys
sys.path.append("../python")
sys.path.append("../../09_hull_white_short_rate_model/python")

from market_data import load_curve_data
from hull_white_model import HullWhiteModel
from stochastic_vol_model import StochasticVolShortRateModel
from stochastic_vol_simulation import simulate_stochastic_vol_paths


def test_simulation_shape():

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

    r0 = hw.instantaneous_forward_rate(1e-6)

    times, rates, variances = simulate_stochastic_vol_paths(
        model=model,
        r0=r0,
        v0=0.0001,
        maturity=5.0,
        n_steps=50,
        n_paths=100,
        seed=42
    )

    assert rates.shape == (100, 51)
    assert variances.shape == (100, 51)
