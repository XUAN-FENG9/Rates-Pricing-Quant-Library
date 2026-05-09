import numpy as np


def generate_forward_curve(
    curve,
    start=0.25,
    end=30,
    step=0.25
):
    """
    Generate forward curve.

    Parameters
    ----------
    curve : YieldCurve
    start : float
    end : float
    step : float

    Returns
    -------
    times : np.array
    fwds  : np.array
    """

    times = np.arange(start, end, step)

    fwds = []

    for t in times:

        fwd = curve.forward_rate(
            t,
            t + step
        )

        fwds.append(fwd)

    return times, np.array(fwds)