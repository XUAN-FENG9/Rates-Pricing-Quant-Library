import sys

sys.path.append("../python")
sys.path.append("../../09_hull_white_short_rate_model/python")
sys.path.append("../../11_bermudan_swaption_tree_pricing/python")

from market_data import load_curve_data
from hull_white_model import HullWhiteModel
from bermudan_swaption import BermudanSwaption

from lsm_path_simulation import simulate_hull_white_paths_for_lsm
from lsm_bermudan_pricer import BermudanSwaptionLSMPricer


def test_lsm_price_positive():

    curve = load_curve_data(
        "../../09_hull_white_short_rate_model/data/usd_zero_curve.csv"
    )

    model = HullWhiteModel(
        mean_reversion=0.05,
        volatility=0.01,
        curve=curve
    )

    r0 = model.instantaneous_forward_rate(1e-6)

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

    times, paths = simulate_hull_white_paths_for_lsm(
        model=model,
        r0=r0,
        maturity=10.0,
        n_steps=200,
        n_paths=1000,
        seed=42
    )

    pricer = BermudanSwaptionLSMPricer(
        model=model,
        instrument=bermudan,
        times=times,
        rate_paths=paths,
        basis_type="rate_swap",
        basis_degree=2
    )

    price = pricer.price()
    
    print(price)

    assert price >= 0.0