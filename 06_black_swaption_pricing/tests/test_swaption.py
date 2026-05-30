import sys
sys.path.append("../python")


from curve import YieldCurve
from forward_swap import ForwardStartingSwap
from black_swaption import BlackSwaption
from bachelier_swaption import BachelierSwaption


def test_swaption_price():

    curve = YieldCurve(
        [1,2,5,10],
        [0.02,0.025,0.03,0.035]
    )

    swap = ForwardStartingSwap(
        notional=10_000_000,
        fixed_rate=0.03,
        start=1.0,
        end=6.0
    )

## Example 1: Positive rates
# using Black formula
    black_swaption_1 = BlackSwaption(
        notional=10_000_000,
        strike=0.03,
        expiry=swap.start,
        underlying_swap=swap,
        volatility=0.10
    )

    black_price_1 = black_swaption_1.price(curve)
    
    assert black_price_1 > 0
    
    print(black_price_1)

# using Bachelier formula
    bachelier_swaption_1 = BachelierSwaption(
        notional=10_000_000,
        strike=0.03,
        expiry=swap.start,
        underlying_swap=swap,
        volatility=0.10
    )

    bachelier_price_1 = bachelier_swaption_1.price(curve)

    assert bachelier_price_1 > 0
    
    print(bachelier_price_1)
    
    
## Example 2: Negative rates
# using Bachelier formula
    bachelier_swaption_2 = BachelierSwaption(
        notional=10_000_000,
        strike=-0.0025,
        expiry=swap.start,
        underlying_swap=swap,
        volatility=0.01
    )

    bachelier_price_2 = bachelier_swaption_2.price(curve)

    assert bachelier_price_2 > 0
    
    print(bachelier_price_2)
    
# using Black formula
    black_swaption_2 = BlackSwaption(
        notional=10_000_000,
        strike=-0.0025,
        expiry=swap.start,
        underlying_swap=swap,
        volatility=0.01
    )

    black_price_2 = black_swaption_2.price(curve)
    
    assert black_price_2 > 0
    
    print(black_price_2)

