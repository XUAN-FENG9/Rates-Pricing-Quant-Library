# ✝ In memory of my beloved grandfather - Heshun Feng (冯和顺), who passed away today (11th July 2026)
# His love and encouragement will forever inspire me.


"""
diagnostics.py

Diagnostics for the Gaussian LMM.
"""

import numpy as np
import pandas as pd


def forward_curve_table(
    tenor_structure,
    initial_forwards
):
    """
    Return initial forward curve as a DataFrame.
    """

    return pd.DataFrame(
        {
            "reset_time": tenor_structure.times[:-1],
            "payment_time": tenor_structure.times[1:],
            "accrual": tenor_structure.accruals,
            "initial_forward": initial_forwards
        }
    )


def summarize_simulation(
    times,
    forward_paths,
    tenor_structure
):
    """
    Summarize simulated forward rates at their reset dates.
    """

    rows = []

    for i in range(
        tenor_structure.n_forwards
    ):

        reset_time = tenor_structure.times[i]

        simulation_index = int(
            np.argmin(
                np.abs(
                    times
                    -
                    reset_time
                )
            )
        )

        values = forward_paths[
            :,
            simulation_index,
            i
        ]

        rows.append(
            {
                "forward_index": i,
                "reset_time": reset_time,
                "mean": values.mean(),
                "std": values.std(),
                "min": values.min(),
                "max": values.max()
            }
        )

    return pd.DataFrame(rows)


def check_correlation_matrix(
    correlation_matrix
):
    """
    Return basic correlation diagnostics.
    """

    eigenvalues = np.linalg.eigvalsh(
        correlation_matrix
    )

    return {
        "minimum_eigenvalue": float(
            eigenvalues.min()
        ),
        "maximum_eigenvalue": float(
            eigenvalues.max()
        ),
        "symmetric": bool(
            np.allclose(
                correlation_matrix,
                correlation_matrix.T
            )
        ),
        "unit_diagonal": bool(
            np.allclose(
                np.diag(
                    correlation_matrix
                ),
                1.0
            )
        )
    }


def print_pricing_summary(
    caplet_price,
    swaption_price
):
    """
    Print caplet and swaption prices.
    """

    print("Gaussian LMM Pricing Summary")
    print("=" * 70)

    print(
        f"Caplet price          : {caplet_price:,.6f}"
    )

    print(
        f"Payer swaption price : {swaption_price:,.6f}"
    )