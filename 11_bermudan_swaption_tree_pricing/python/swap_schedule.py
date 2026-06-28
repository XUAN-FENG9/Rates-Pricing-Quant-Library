"""
swap_schedule.py

Schedule utilities for Bermudan swaption tree pricing.
"""

import numpy as np


def generate_payment_dates(
    start,
    end,
    payment_frequency=2
):
    """
    Generate regular swap payment dates.

    Example:
        start = 2.0
        end   = 7.0
        payment_frequency = 2

    returns:
        2.5, 3.0, 3.5, ..., 7.0
    """

    dt = 1.0 / payment_frequency

    n_payments = int(
        round(
            (end - start) * payment_frequency
        )
    )

    return np.array(
        [
            start + (i + 1) * dt
            for i in range(n_payments)
        ]
    )


def generate_exercise_dates(
    first_exercise,
    last_exercise,
    exercise_frequency=1
):
    """
    Generate Bermudan exercise dates.
    """

    dt = 1.0 / exercise_frequency

    n_dates = int(
        round(
            (last_exercise - first_exercise)
            *
            exercise_frequency
        )
    )

    return np.array(
        [
            first_exercise + i * dt
            for i in range(n_dates + 1)
        ]
    )