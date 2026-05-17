import copy

from curve import YieldCurve


def parallel_shift_curve(
    curve,
    shift_bp
):
    """
    Parallel shift the zero curve.

    Parameters
    ----------
    shift_bp : float
        Shift in basis points.
    """

    shifted_rates = (
        curve.zero_rates
        + shift_bp / 10000
    )

    return YieldCurve(
        curve.maturities,
        shifted_rates
    )


def dv01(
    instrument,
    curve
):
    """
    Compute DV01 using bump-and-reprice.

    DV01:
    ------
    Dollar value of 1bp move.
    """

    base_npv = instrument.npv(curve)

    bumped_curve = parallel_shift_curve(
        curve,
        1
    )

    bumped_npv = instrument.npv(
        bumped_curve
    )

    return bumped_npv - base_npv


def pv01(
    instrument,
    curve
):
    """
    PV01 magnitude.
    """

    return abs(
        dv01(
            instrument,
            curve
        )
    )