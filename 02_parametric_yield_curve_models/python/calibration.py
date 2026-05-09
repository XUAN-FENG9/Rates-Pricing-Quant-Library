import numpy as np
from scipy.optimize import minimize
from nelson_siegel import NelsonSiegelCurve


def calibration_error(params, times, market_rates):
    """
    Objective function for calibration.

    We minimize squared errors between:
    - market zero rates
    - model zero rates
    """

    beta0, beta1, beta2, tau = params

    model = NelsonSiegelCurve(
        beta0,
        beta1,
        beta2,
        tau
    )

    model_rates = np.array(
        [model.zero_rate(t) for t in times]
    )

    error = np.sum(
        (model_rates - market_rates) ** 2
    )

    return error


def calibrate_nelson_siegel(
    times,
    market_rates
):
    """
    Calibrate NS parameters using least squares.
    """

    initial_guess = [0.03, -0.02, 0.02, 2.0]

    result = minimize(
        calibration_error,
        initial_guess,
        args=(times, market_rates),
        method="Nelder-Mead"
    )

    return result.x