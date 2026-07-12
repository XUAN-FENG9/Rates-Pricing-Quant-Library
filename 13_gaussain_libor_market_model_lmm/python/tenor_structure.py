# ✝ In memory of my beloved grandfather - Heshun Feng (冯和顺), who passed away today (11th July 2026)
# His love and encouragement will forever inspire me.

"""
tenor_structure.py

Discrete tenor structure for the Gaussian LIBOR Market Model.

Forward rate L_i applies over:

    [T_i, T_{i+1}]

with accrual:

    delta_i = T_{i+1} - T_i
"""

import numpy as np


class TenorStructure:
    """
    Discrete forward-rate tenor structure.

    Parameters
    ----------
    start : float
        Initial tenor-grid time.

    end : float
        Final tenor-grid time.

    payment_frequency : int
        Number of periods per year.

        Examples:
            2 -> semiannual tenor grid
            4 -> quarterly tenor grid
    """

    def __init__(
        self,
        start,
        end,
        payment_frequency=2
    ):

        if end <= start:
            raise ValueError(
                "end must be greater than start."
            )

        if payment_frequency <= 0:
            raise ValueError(
                "payment_frequency must be positive."
            )

        self.start = float(start)
        self.end = float(end)

        self.payment_frequency = int(
            payment_frequency
        )

        self.delta = (
            1.0
            /
            self.payment_frequency
        )

        n_periods = int(
            round(
                (self.end - self.start)
                *
                self.payment_frequency
            )
        )

        self.times = np.array(
            [
                self.start
                +
                i
                *
                self.delta
                for i in range(
                    n_periods + 1
                )
            ],
            dtype=float
        )

        self.accruals = np.diff(
            self.times
        )

        self.n_forwards = len(
            self.accruals
        )

    def initial_forward_rates(
        self,
        curve
    ):
        """
        Extract initial simple-compounded forward rates.

        Formula:

            1 + delta_i L_i(0)
            =
            P(0,T_i) / P(0,T_{i+1})

        Therefore:

            L_i(0)
            =
            [P(0,T_i)/P(0,T_{i+1}) - 1] / delta_i

        Parameters
        ----------
        curve : YieldCurve
            Initial discount curve.

        Returns
        -------
        np.ndarray
            Initial forward-rate vector.
        """

        forwards = np.zeros(
            self.n_forwards
        )

        for i in range(
            self.n_forwards
        ):

            t0 = self.times[i]
            t1 = self.times[i + 1]

            p0 = curve.get_df(t0)
            p1 = curve.get_df(t1)

            forwards[i] = (
                p0 / p1
                -
                1.0
            ) / self.accruals[i]

        return forwards

    def initial_discount_factors(
        self,
        curve
    ):
        """
        Return initial discount factors on the tenor grid.
        """

        return np.array(
            [
                curve.get_df(t)
                for t in self.times
            ]
        )

    def forward_index(
        self,
        reset_time,
        tolerance=1e-8
    ):
        """
        Return forward index associated with a reset time.
        """

        differences = np.abs(
            self.times[:-1]
            -
            reset_time
        )

        index = int(
            np.argmin(
                differences
            )
        )

        if differences[index] > tolerance:
            raise ValueError(
                f"Reset time {reset_time} is not on the tenor grid."
            )

        return index

    def time_index(
        self,
        target_time,
        tolerance=1e-8
    ):
        """
        Return tenor-grid index for a tenor date.
        """

        differences = np.abs(
            self.times
            -
            target_time
        )

        index = int(
            np.argmin(
                differences
            )
        )

        if differences[index] > tolerance:
            raise ValueError(
                f"Time {target_time} is not on the tenor grid."
            )

        return index