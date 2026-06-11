"""
diagnostics.py

Diagnostics for SABR calibration quality.
"""

import numpy as np


def print_calibration_summary(
    sabr_surface
):
    """
    Print SABR calibration results.
    """

    table = sabr_surface.parameter_table

    print("\nSABR Calibration Summary")
    print("=" * 80)

    print(table)

    print("\nAverage RMSE:")
    print(table["rmse"].mean())


def compare_market_and_model(
    calibration_result
):
    """
    Print market vs fitted vols for one expiry.
    """

    strikes = calibration_result["strikes"]
    market_vols = calibration_result["market_vols"]
    fitted_vols = calibration_result["fitted_vols"]

    print("\nStrike | Market Vol | SABR Vol | Error")
    print("=" * 60)

    for K, m, f in zip(
        strikes,
        market_vols,
        fitted_vols
    ):

        print(
            f"{K:.6f} | {m:.6f} | {f:.6f} | {f-m:.6f}"
        )


def calibration_error_stats(
    calibration_result
):
    """
    Return useful error statistics.
    """

    errors = (
        calibration_result["fitted_vols"]
        -
        calibration_result["market_vols"]
    )

    return {
        "mean_error": np.mean(errors),
        "max_abs_error": np.max(np.abs(errors)),
        "rmse": np.sqrt(np.mean(errors ** 2))
    }