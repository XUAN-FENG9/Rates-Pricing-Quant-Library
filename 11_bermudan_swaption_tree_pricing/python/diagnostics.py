"""
diagnostics.py

Diagnostics for Bermudan swaption tree pricing.
"""

import numpy as np
import pandas as pd


def print_tree_summary(
    tree
):
    """
    Print short-rate tree summary.
    """

    print("Hull-White Tree Summary")
    print("=" * 60)

    print(f"Maturity        : {tree.maturity}")
    print(f"Number of steps : {tree.n_steps}")
    print(f"dt              : {tree.dt:.6f}")
    print(f"dr              : {tree.dr:.6f}")
    print(f"Initial rate    : {tree.r0:.6f}")

    print()
    print("Final rate range:")
    print(f"min = {tree.rates[-1].min():.6f}")
    print(f"max = {tree.rates[-1].max():.6f}")


def print_instrument_summary(
    instrument
):
    """
    Print Bermudan swaption summary.
    """

    print("Bermudan Swaption Summary")
    print("=" * 60)

    print(f"Notional          : {instrument.notional:,.2f}")
    print(f"Fixed rate        : {instrument.fixed_rate:.6f}")
    print(f"Payer             : {instrument.payer}")
    print(f"Option start      : {instrument.option_start}")
    print(f"Option end        : {instrument.option_end}")
    print(f"Swap tenor        : {instrument.swap_tenor}")
    print(f"Payment frequency : {instrument.payment_frequency}")
    print(f"Exercise frequency: {instrument.exercise_frequency}")

    print()
    print("Exercise dates:")
    print(instrument.exercise_dates)

    print()
    print("Example payment schedules:")

    for t in instrument.exercise_dates:

        print(
            f"Exercise at {t:.2f}Y -> "
            f"swap {t:.2f}Y to {t + instrument.swap_tenor:.2f}Y"
        )

        print(
            instrument.payment_dates(t)
        )


def print_pricing_summary(
    price
):
    """
    Print pricing result.
    """

    print("Pricing Result")
    print("=" * 60)

    print(f"Bermudan swaption price: {price:,.6f}")


def exercise_statistics(
    tree,
    exercise_tree
):
    """
    Return exercise statistics by tree time.
    """

    rows = []

    for step, t in enumerate(tree.times):

        flags = exercise_tree[step]

        n_exercise = int(
            np.sum(flags)
        )

        total_nodes = len(flags)

        rows.append(
            {
                "time": t,
                "exercise_nodes": n_exercise,
                "total_nodes": total_nodes,
                "exercise_ratio": (
                    n_exercise
                    /
                    total_nodes
                )
            }
        )

    return pd.DataFrame(rows)