from curve import YieldCurve


def steepener_scenario(curve):
    """
    Long-end rates rise more.
    """

    shocked = curve.zero_rates.copy()

    for i, t in enumerate(curve.maturities):

        if t < 5:

            shocked[i] += 0.001

        else:

            shocked[i] += 0.005

    return YieldCurve(
        curve.maturities,
        shocked
    )


def flattener_scenario(curve):
    """
    Short-end rates rise more.
    """

    shocked = curve.zero_rates.copy()

    for i, t in enumerate(curve.maturities):

        if t < 5:

            shocked[i] += 0.005

        else:

            shocked[i] += 0.001

    return YieldCurve(
        curve.maturities,
        shocked
    )