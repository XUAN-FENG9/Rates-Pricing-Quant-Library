import sys
sys.path.append("../python")

from curve import YieldCurve
from swap import InterestRateSwap


def test_swap_pricing():

    maturities = [1, 2, 5, 10]

    rates = [0.02, 0.025, 0.03, 0.035]

    curve = YieldCurve(
        maturities,
        rates
    )

    swap = InterestRateSwap(
        notional=1_000_000,
        fixed_rate=0.03,
        maturity=5
    )

    npv = swap.npv(curve)

    assert isinstance(npv, float)
    
    print(swap.payment_dates)

    print(swap.fixed_leg.pv(curve))

    print(swap.floating_leg.pv(curve))

    print(swap.npv(curve))
    
    return npv
