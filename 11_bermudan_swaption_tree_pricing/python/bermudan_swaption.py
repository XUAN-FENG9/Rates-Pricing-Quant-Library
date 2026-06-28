"""
bermudan_swaption.py

Bermudan swaption instrument definition.

Market-style convention:

    exercise at time t
        ↓
    enter into a swap starting at t
        ↓
    swap ends at t + swap_tenor

Example:
    exercise at 2Y
    swap_tenor = 5Y

means:
    enter into a 2Y -> 7Y swap.
"""

import numpy as np

from swap_schedule import (
    generate_payment_dates,
    generate_exercise_dates
)

import sys
sys.path.append("../../09_hull_white_short_rate_model/python")
from bond_pricing import (
    zero_coupon_bond_price
)


class BermudanSwaption:
    """
    Bermudan swaption.

    Parameters
    ----------
    notional : float
        Swap notional.

    fixed_rate : float
        Fixed rate of the underlying swap.

    option_start : float
        First exercise date.

    option_end : float
        Last exercise date.

    swap_tenor : float
        Tenor of the underlying swap after exercise.

    payment_frequency : int
        Fixed-leg payment frequency.

    exercise_frequency : int
        Exercise frequency.

    payer : bool
        True for payer swaption.
        False for receiver swaption.
    """

    def __init__(
        self,
        notional,
        fixed_rate,
        option_start,
        option_end,
        swap_tenor,
        payment_frequency=2,
        exercise_frequency=1,
        payer=True
    ):

        self.notional = notional
        self.fixed_rate = fixed_rate

        self.option_start = option_start
        self.option_end = option_end
        self.swap_tenor = swap_tenor

        self.payment_frequency = payment_frequency
        self.exercise_frequency = exercise_frequency

        self.payer = payer

        self.exercise_dates = generate_exercise_dates(
            first_exercise=option_start,
            last_exercise=option_end,
            exercise_frequency=exercise_frequency
        )

        self.payment_schedule_cache = {}

        for exercise_time in self.exercise_dates:

            self.payment_schedule_cache[
                round(float(exercise_time), 10)
            ] = generate_payment_dates(
                start=exercise_time,
                end=exercise_time + swap_tenor,
                payment_frequency=payment_frequency
            )

    def payment_dates(
        self,
        exercise_time
    ):
        """
        Return payment dates for the swap entered at exercise_time.
        """

        key = round(float(exercise_time), 10)

        if key in self.payment_schedule_cache:
            return self.payment_schedule_cache[key]

        return generate_payment_dates(
            start=exercise_time,
            end=exercise_time + self.swap_tenor,
            payment_frequency=self.payment_frequency
        )

    def annuity(
        self,
        model,
        exercise_time,
        short_rate
    ):
        """
        Fixed-leg annuity:

            A(t) = sum_i accrual * P(t,T_i)
        """

        pay_dates = self.payment_dates(
            exercise_time
        )

        accrual = (
            1.0
            /
            self.payment_frequency
        )

        dfs = np.array(
            [
                zero_coupon_bond_price(
                    model=model,
                    t=exercise_time,
                    T=T,
                    r_t=short_rate
                )
                for T in pay_dates
            ]
        )

        return accrual * np.sum(dfs)

    def forward_swap_rate(
        self,
        model,
        exercise_time,
        short_rate
    ):
        """
        Forward swap rate at an exercise node:

            S(t) = [1 - P(t,T_N)] / A(t)
        """

        pay_dates = self.payment_dates(
            exercise_time
        )

        if len(pay_dates) == 0:
            return 0.0

        final_maturity = pay_dates[-1]

        final_df = zero_coupon_bond_price(
            model=model,
            t=exercise_time,
            T=final_maturity,
            r_t=short_rate
        )

        float_leg = 1.0 - final_df

        annuity = self.annuity(
            model=model,
            exercise_time=exercise_time,
            short_rate=short_rate
        )

        if abs(annuity) < 1e-12:
            return 0.0

        return float_leg / annuity

    def swap_value(
        self,
        model,
        exercise_time,
        short_rate
    ):
        """
        Value of entering the underlying swap.

        Payer swap:
            N * A(t) * [S(t) - K]

        Receiver swap:
            N * A(t) * [K - S(t)]
        """

        annuity = self.annuity(
            model=model,
            exercise_time=exercise_time,
            short_rate=short_rate
        )

        swap_rate = self.forward_swap_rate(
            model=model,
            exercise_time=exercise_time,
            short_rate=short_rate
        )

        if self.payer:

            value = annuity * (
                swap_rate - self.fixed_rate
            )

        else:

            value = annuity * (
                self.fixed_rate - swap_rate
            )

        return self.notional * value

    def exercise_value(
        self,
        model,
        exercise_time,
        short_rate
    ):
        """
        Immediate exercise value.
        """

        return max(
            self.swap_value(
                model=model,
                exercise_time=exercise_time,
                short_rate=short_rate
            ),
            0.0
        )

    def summary(
        self
    ):
        """
        Return instrument summary.
        """

        return {
            "notional": self.notional,
            "fixed_rate": self.fixed_rate,
            "option_start": self.option_start,
            "option_end": self.option_end,
            "swap_tenor": self.swap_tenor,
            "payment_frequency": self.payment_frequency,
            "exercise_frequency": self.exercise_frequency,
            "payer": self.payer,
            "exercise_dates": self.exercise_dates
        }