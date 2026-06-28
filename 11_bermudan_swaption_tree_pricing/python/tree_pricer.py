"""
tree_pricer.py

Bermudan swaption pricing by backward induction.
"""

import numpy as np


class BermudanSwaptionTreePricer:
    """
    Bermudan swaption tree pricer.
    """

    def __init__(
        self,
        tree,
        bermudan_swaption
    ):

        self.tree = tree
        self.instrument = bermudan_swaption

        self.value_tree = None
        self.exercise_tree = None

    def is_exercise_time(
        self,
        t,
        tolerance=1e-8
    ):
        """
        Check whether t is an exercise date.
        """

        return np.any(
            np.abs(
                self.instrument.exercise_dates
                -
                t
            )
            <
            tolerance
        )

    def price(
        self
    ):
        """
        Backward induction.

        At each node:

            if exercise date:
                value = max(exercise value, continuation value)

            otherwise:
                value = continuation value
        """

        n_steps = self.tree.n_steps

        values = [
            np.zeros(step + 1)
            for step in range(n_steps + 1)
        ]

        exercise_flags = [
            np.zeros(step + 1, dtype=bool)
            for step in range(n_steps + 1)
        ]

        terminal_time = self.tree.times[-1]

        for node in range(n_steps + 1):

            r = self.tree.rates[-1][node]

            if self.is_exercise_time(
                terminal_time
            ):

                values[-1][node] = (
                    self.instrument.exercise_value(
                        model=self.tree.model,
                        exercise_time=terminal_time,
                        short_rate=r
                    )
                )

                exercise_flags[-1][node] = (
                    values[-1][node] > 0.0
                )

        for step in reversed(
            range(n_steps)
        ):

            t = self.tree.times[step]

            for node in range(step + 1):

                p_up = self.tree.probabilities[step][node]
                p_down = 1.0 - p_up

                df = self.tree.discount_factor_one_step(
                    step,
                    node
                )

                continuation_value = (
                    df
                    *
                    (
                        p_down
                        *
                        values[step + 1][node]
                        +
                        p_up
                        *
                        values[step + 1][node + 1]
                    )
                )

                node_value = continuation_value

                if self.is_exercise_time(t):

                    r = self.tree.rates[step][node]

                    exercise_value = (
                        self.instrument.exercise_value(
                            model=self.tree.model,
                            exercise_time=t,
                            short_rate=r
                        )
                    )

                    if exercise_value > continuation_value:

                        node_value = exercise_value
                        exercise_flags[step][node] = True

                values[step][node] = node_value

        self.value_tree = values
        self.exercise_tree = exercise_flags

        return values[0][0]

    def get_value_tree(
        self
    ):
        """
        Return value tree.
        """

        if self.value_tree is None:
            raise ValueError(
                "Run price() before accessing the value tree."
            )

        return self.value_tree

    def get_exercise_tree(
        self
    ):
        """
        Return exercise decision tree.
        """

        if self.exercise_tree is None:
            raise ValueError(
                "Run price() before accessing the exercise tree."
            )

        return self.exercise_tree