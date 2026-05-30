from scipy.optimize import brentq


def implied_volatility(
    target_price,
    curve,
    swaption,
    low=1e-6,
    high=5.0
):
    """
    Solve implied volatility.
    """

    def objective(vol):

        swaption.volatility = vol

        return (
            swaption.price(curve)
            - target_price
        )

    return brentq(
        objective,
        low,
        high
    )