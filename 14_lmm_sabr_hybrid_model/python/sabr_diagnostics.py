"""
sabr_diagnostics.py

Diagnostic tables and model checks for the LMM-SABR hybrid.
"""

import numpy as np
import pandas as pd

from sabr_simulation import exact_time_index


def parameter_table(
    model
):
    """
    Return one row per modeled forward.
    """

    return pd.DataFrame(
        {
            "forward_index":
                np.arange(
                    model.number_of_forwards
                ),

            "reset_time":
                model.get_reset_times(),

            "payment_time":
                np.asarray(
                    model.tenor.times[1:],
                    dtype=float
                ),

            "accrual":
                model.get_accruals(),

            "initial_forward":
                model.initial_forwards,

            "alpha0":
                model.sabr_parameters.alpha0,

            "beta":
                model.sabr_parameters.beta,

            "rho":
                model.sabr_parameters.rho,

            "nu":
                model.sabr_parameters.nu,

            "shift":
                model.sabr_parameters.shift
        }
    )


def simulation_state_table(
    model,
    simulation,
    path_index,
    time
):
    """
    Return the complete forward and alpha state
    for one path at one time.
    """

    number_of_paths = (
        simulation.get_number_of_paths()
    )

    if (
        path_index < 0
        or
        path_index >= number_of_paths
    ):

        raise ValueError(
            "path_index is invalid."
        )

    time_index = exact_time_index(
        simulation.times,
        time
    )

    return pd.DataFrame(
        {
            "forward_index":
                np.arange(
                    model.number_of_forwards
                ),

            "reset_time":
                model.get_reset_times(),

            "forward_rate":
                simulation.forward_paths[
                    path_index,
                    time_index,
                    :
                ],

            "alpha":
                simulation.alpha_paths[
                    path_index,
                    time_index,
                    :
                ],

            "active":
                model.active_mask(
                    time
                )
        }
    )


def distribution_summary(
    model,
    simulation,
    time
):
    """
    Summarize simulated forward and alpha distributions.
    """

    time_index = exact_time_index(
        simulation.times,
        time
    )

    forwards = (
        simulation.forward_paths[
            :,
            time_index,
            :
        ]
    )

    alpha = (
        simulation.alpha_paths[
            :,
            time_index,
            :
        ]
    )

    return pd.DataFrame(
        {
            "forward_index":
                np.arange(
                    model.number_of_forwards
                ),

            "reset_time":
                model.get_reset_times(),

            "forward_mean":
                np.mean(
                    forwards,
                    axis=0
                ),

            "forward_std":
                np.std(
                    forwards,
                    axis=0,
                    ddof=1
                ),

            "forward_5_percent":
                np.quantile(
                    forwards,
                    0.05,
                    axis=0
                ),

            "forward_95_percent":
                np.quantile(
                    forwards,
                    0.95,
                    axis=0
                ),

            "alpha_mean":
                np.mean(
                    alpha,
                    axis=0
                ),

            "alpha_std":
                np.std(
                    alpha,
                    axis=0,
                    ddof=1
                )
        }
    )


def last_forward_drift_check(
    model,
    time=0.0
):
    """
    Check that the final forward drift is zero
    under the terminal measure.
    """

    drift = model.terminal_measure_drift(
        time,
        model.initial_forwards,
        model.sabr_parameters.alpha0
    )

    return {
        "last_forward_drift":
            float(
                drift[-1]
            ),

        "absolute_error":
            float(
                abs(
                    drift[-1]
                )
            )
    }


def alpha_positivity_check(
    simulation
):
    """
    Check that all simulated alpha values are positive.
    """

    minimum_alpha = np.min(
        simulation.alpha_paths
    )

    return {
        "minimum_alpha":
            float(
                minimum_alpha
            ),

        "all_positive":
            bool(
                minimum_alpha > 0.0
            )
    }


def forward_validity_check(
    model,
    simulation
):
    """
    Check the discount-factor restriction:

        1 + delta * L > 0
    """

    accruals = model.get_accruals()

    denominators = (
        1.0
        +
        simulation.forward_paths
        *
        accruals[
            None,
            None,
            :
        ]
    )

    minimum_denominator = np.min(
        denominators
    )

    return {
        "minimum_denominator":
            float(
                minimum_denominator
            ),

        "all_valid":
            bool(
                minimum_denominator > 0.0
            )
    }