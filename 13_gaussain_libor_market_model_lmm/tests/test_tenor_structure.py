# ✝ In memory of my beloved grandfather - Heshun Feng (冯和顺), who passed away today (11th July 2026)
# His love and encouragement will forever inspire me.


import sys

sys.path.append("../python")


from market_data import load_curve_data
from tenor_structure import TenorStructure


def test_initial_forwards():

    curve = load_curve_data(
        "../data/usd_zero_curve.csv"
    )

    tenor = TenorStructure(
        start=0.0,
        end=10.0,
        payment_frequency=2
    )

    forwards = tenor.initial_forward_rates(
        curve
    )

    assert len(forwards) == 20

    assert all(
        forwards > -1.0
    )
