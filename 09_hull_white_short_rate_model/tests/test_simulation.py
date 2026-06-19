import sys
sys.path.append("../python")
sys.path.append("../../06_black_swaption_pricing/python")

from market_data import load_curve_data
from hull_white_model import HullWhiteModel
from hull_white_simulation import simulate_short_rate_paths


def test_simulation_shape():

    curve = load_curve_data("../data/usd_zero_curve.csv")

    model = HullWhiteModel(
        mean_reversion=0.05,
        volatility=0.01,
        curve=curve
    )

    r0 = model.instantaneous_forward_rate(1e-6)

    times, paths = simulate_short_rate_paths(
        model=model,
        r0=r0,
        maturity=5.0,
        n_steps=50,
        n_paths=100,
        seed=42
    )

    assert paths.shape == (100, 51)
    assert len(times) == 51