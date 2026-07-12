import sys

sys.path.append("../python")
sys.path.append("../../09_hull_white_short_rate_model/python")

from market_data import load_curve_data
from hull_white_model import HullWhiteModel
from lsm_path_simulation import simulate_hull_white_paths_for_lsm


def test_lsm_path_shape():

    curve = load_curve_data(
        "../../09_hull_white_short_rate_model/data/usd_zero_curve.csv"
    )

    model = HullWhiteModel(
        mean_reversion=0.05,
        volatility=0.01,
        curve=curve
    )

    r0 = model.instantaneous_forward_rate(1e-6)

    times, paths = simulate_hull_white_paths_for_lsm(
        model=model,
        r0=r0,
        maturity=10.0,
        n_steps=100,
        n_paths=500,
        seed=42
    )

    assert paths.shape == (500, 101)
    assert len(times) == 101