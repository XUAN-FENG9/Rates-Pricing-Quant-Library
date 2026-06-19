"""
diagnostics.py

Diagnostic utilities for Chapter 09.
"""

import numpy as np


def summarize_paths(
    times,
    paths
):
    """
    Print summary statistics for simulated short-rate paths.
    """

    final_rates = paths[:, -1]

    print("Short-Rate Path Summary")
    print("=" * 60)

    print(f"Initial rate: {paths[0, 0]:.6f}")
    print(f"Final mean  : {final_rates.mean():.6f}")
    print(f"Final std   : {final_rates.std():.6f}")
    print(f"Final min   : {final_rates.min():.6f}")
    print(f"Final max   : {final_rates.max():.6f}")


def summarize_curve_fit(
    fit_df
):
    """
    Print curve fitting summary.
    """

    max_abs_error = np.max(
        np.abs(
            fit_df["difference"]
        )
    )

    print("Curve Fit Summary")
    print("=" * 60)

    print(fit_df)

    print("\nMax absolute error:")
    print(max_abs_error)


def compare_prices(
    analytic_price,
    monte_carlo_price
):
    """
    Print analytic vs Monte Carlo price comparison.
    """

    print("Pricing Comparison")
    print("=" * 60)

    print(f"Analytic price    : {analytic_price:.8f}")
    print(f"Monte Carlo price : {monte_carlo_price:.8f}")
    print(f"Difference        : {monte_carlo_price - analytic_price:.8f}")