import sys
sys.path.append("../python")

from curve import YieldCurve
from swap import InterestRateSwap
from risk import dv01


def test_dv01():

    maturities = [1, 2, 5, 10]

    rates = [0.02, 0.025, 0.03, 0.035]

    curve = YieldCurve(
        maturities,
        rates
    )

    swap = InterestRateSwap(
        1_000_000,
        0.03,
        5
    )

    risk = dv01(
        swap,
        curve
    )

    assert isinstance(
        risk,
        float
    )
    
    return risk

