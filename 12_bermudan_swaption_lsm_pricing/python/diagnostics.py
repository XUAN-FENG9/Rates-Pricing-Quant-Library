"""
diagnostics.py

Diagnostics for Bermudan swaption LSM pricing.
"""

import numpy as np
import pandas as pd


def print_lsm_summary(
    price,
    pricer
):
    """
    Print LSM pricing summary.
    """

    print("Bermudan Swaption LSM Pricing Summary")
    print("=" * 70)

    print(f"Price       : {price:,.6f}")
    print(f"Basis type  : {pricer.basis_type}")
    print(f"Basis degree: {pricer.basis_degree}")
    print(f"Paths       : {pricer.rate_paths.shape[0]}")
    print(f"Steps       : {pricer.rate_paths.shape[1] - 1}")


def print_exercise_summary(
    exercise_df
):
    """
    Print exercise summary table.
    """

    print("Exercise Summary")
    print("=" * 70)

    print(exercise_df)


def regression_diagnostics_table(
    pricer
):
    """
    Convert regression diagnostics into a DataFrame.
    """

    rows = []

    for item in pricer.regression_diagnostics:

        coeffs = item["coefficients"]

        rows.append(
            {
                "exercise_time": item["exercise_time"],
                "n_regression_paths": item["n_regression_paths"],
                "basis_type": item["basis_type"],
                "basis_degree": item["basis_degree"],
                "n_coefficients": len(coeffs),
                "coefficients": coeffs
            }
        )

    return pd.DataFrame(rows)


def compare_tree_lsm_prices(
    tree_price,
    lsm_price
):
    """
    Compare Chapter 11 tree price and Chapter 12 LSM price.
    """

    print("Tree vs LSM Comparison")
    print("=" * 70)

    print(f"Tree price : {tree_price:,.6f}")
    print(f"LSM price  : {lsm_price:,.6f}")
    print(f"Difference : {lsm_price - tree_price:,.6f}")