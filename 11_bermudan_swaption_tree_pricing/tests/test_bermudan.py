import sys

sys.path.append("../python")
sys.path.append("../../09_hull_white_short_rate_model/python")

from market_data import load_curve_data
from hull_white_model import HullWhiteModel

from hull_white_tree import HullWhiteBinomialTree
from bermudan_swaption import BermudanSwaption
from tree_pricer import BermudanSwaptionTreePricer


def test_bermudan_price_positive():

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
        n_steps=40
    )

    bermudan = BermudanSwaption(
    notional=1_000_000,
    fixed_rate=0.045,
    option_start=1.0,
    option_end=5.0,
    swap_tenor=5.0,
    payment_frequency=2,
    exercise_frequency=1,
    payer=True
)

    pricer = BermudanSwaptionTreePricer(
        tree,
        bermudan
    )

    price = pricer.price()
    
    print(price)

    assert price >= 0.0