"""
diagnostics.py

Diagnostic utilities for Chapter 10.
"""

import numpy as np


def summarize_stochastic_vol_paths(
    rate_paths,
    variance_paths
):
    """
    Print summary statistics for stochastic-vol paths.
    """

    final_rates = rate_paths[:, -1]
    final_variances = variance_paths[:, -1]
    final_vols = np.sqrt(final_variances)

    print("Stochastic-Vol Short-Rate Path Summary")
    print("=" * 70)

    print(f"Final rate mean     : {final_rates.mean():.6f}")
    print(f"Final rate std      : {final_rates.std():.6f}")
    print(f"Final rate min      : {final_rates.min():.6f}")
    print(f"Final rate max      : {final_rates.max():.6f}")
    print()
    print(f"Final variance mean : {final_variances.mean():.6f}")
    print(f"Final variance std  : {final_variances.std():.6f}")
    print(f"Final vol mean      : {final_vols.mean():.6f}")
    print(f"Final vol std       : {final_vols.std():.6f}")


def compare_discount_bond_prices(
    market_price,
    constant_hw_price,
    stochastic_vol_price
):
    """
    Print bond price comparison.
    """

    print("Discount Bond Price Comparison")
    print("=" * 70)

    print(f"Market DF              : {market_price:.8f}")
    print(f"Constant-vol HW MC     : {constant_hw_price:.8f}")
    print(f"Stochastic-vol MC      : {stochastic_vol_price:.8f}")
    print(f"SV - Market            : {stochastic_vol_price - market_price:.8f}")
    print(f"SV - Constant HW       : {stochastic_vol_price - constant_hw_price:.8f}")


def compare_option_prices(
    constant_hw_price,
    stochastic_vol_price
):
    """
    Print option price comparison.
    """

    print("Bond Option Price Comparison")
    print("=" * 70)

    print(f"Constant-vol HW price  : {constant_hw_price:.8f}")
    print(f"Stochastic-vol price   : {stochastic_vol_price:.8f}")
    print(f"Difference             : {stochastic_vol_price - constant_hw_price:.8f}")


def print_calibration_result(
    result
):
    """
    Print stochastic-vol calibration result.
    """

    print("Stochastic-Vol Calibration Result")
    print("=" * 70)

    for key, value in result.items():
        print(f"{key}: {value}")