import sys

sys.path.append("../python")
sys.path.append("../../09_hull_white_short_rate_model/python")

from market_data import load_curve_data
from hull_white_model import HullWhiteModel
from hull_white_tree import HullWhiteBinomialTree


def test_tree_build():

    curve = load_curve_data(
        "../../09_hull_white_short_rate_model/data/usd_zero_curve.csv"
    )

    model = HullWhiteModel(
        mean_reversion=0.05,
        volatility=0.01,
        curve=curve
    )

    tree = HullWhiteBinomialTree(
        model=model,
        maturity=5.0,
        n_steps=20
    )

    assert len(tree.rates) == 21
    assert len(tree.rates[-1]) == 21