def vega(
    swaption,
    curve,
    bump=0.0001
):
    """
    Finite-difference vega.
    """

    base_vol = swaption.volatility

    base_price = swaption.price(
        curve
    )

    swaption.volatility = (
        base_vol + bump
    )

    bumped_price = swaption.price(
        curve
    )

    swaption.volatility = base_vol

    return (
        bumped_price
        - base_price
    ) / bump