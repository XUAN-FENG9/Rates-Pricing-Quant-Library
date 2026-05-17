from curve import YieldCurve


def key_rate_shift(
    curve,
    maturity,
    shift_bp
):
    """
    Shift only one key maturity.
    """

    shifted_rates = curve.zero_rates.copy()

    idx = (
        abs(
            curve.maturities - maturity
        )
    ).argmin()

    shifted_rates[idx] += (
        shift_bp / 10000
    )

    return YieldCurve(
        curve.maturities,
        shifted_rates
    )


def key_rate_dv01(
    instrument,
    curve,
    maturity
):
    """
    Compute key rate DV01.
    """

    base_npv = instrument.npv(curve)

    shifted_curve = key_rate_shift(
        curve,
        maturity,
        1
    )

    shifted_npv = instrument.npv(
        shifted_curve
    )

    return shifted_npv - base_npv