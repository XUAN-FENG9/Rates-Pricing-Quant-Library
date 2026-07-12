"""
lsm_bermudan_pricer.py

Longstaff-Schwartz Monte Carlo pricer for Bermudan swaptions.

The central idea:

    immediate exercise value
        vs
    estimated continuation value

The continuation value is estimated by regression on simulated paths.
"""

import numpy as np
import pandas as pd

from regression_basis import (
    polynomial_basis,
    rate_and_swap_basis
)

from lsm_path_simulation import (
    nearest_time_index,
    path_discount_factors_between_indices,
    path_discount_factors_to_index
)


class BermudanSwaptionLSMPricer:
    """
    Bermudan swaption Longstaff-Schwartz pricer.

    Parameters
    ----------
    model : HullWhiteModel
        Chapter 09 Hull-White model.

    instrument : BermudanSwaption
        Chapter 11 Bermudan swaption instrument.

    times : np.ndarray
        Simulation time grid.

    rate_paths : np.ndarray
        Simulated short-rate paths.

    basis_type : str
        "rate", "swap", or "rate_swap".

    basis_degree : int
        Polynomial basis degree.
    """

    def __init__(
        self,
        model,
        instrument,
        times,
        rate_paths,
        basis_type="rate_swap",
        basis_degree=2
    ):

        self.model = model
        self.instrument = instrument

        self.times = times
        self.rate_paths = rate_paths

        self.basis_type = basis_type
        self.basis_degree = basis_degree

        self.exercise_indices = [
            nearest_time_index(
                times,
                t
            )
            for t in instrument.exercise_dates
        ]

        self.exercise_indices = sorted(
            list(
                set(
                    self.exercise_indices
                )
            )
        )

        self.cashflows = None
        self.exercise_time_index = None
        self.exercise_flag_matrix = None

        self.regression_diagnostics = []

    def discount_bond_pathwise(
        self,
        start_index,
        end_time,
        path_index
    ):
        """
        Approximate P(t,T) pathwise using simulated short rates.

        This is different from Chapter 11 tree pricing, where P(t,T)
        came from the affine Hull-White bond pricing formula.

        In LSM, we use the simulated path between t and T.
        """

        end_index = nearest_time_index(
            self.times,
            end_time
        )

        if end_index <= start_index:
            return 1.0

        dt = self.times[1] - self.times[0]

        integral = np.sum(
            self.rate_paths[
                path_index,
                start_index:end_index
            ]
        ) * dt

        return np.exp(
            -integral
        )

    def swap_rate_and_annuity_pathwise(
        self,
        exercise_index,
        path_index
    ):
        """
        Compute pathwise forward swap rate and annuity at an exercise time.
        """

        exercise_time = self.times[
            exercise_index
        ]

        pay_dates = self.instrument.payment_dates(
            exercise_time
        )

        accrual = (
            1.0
            /
            self.instrument.payment_frequency
        )

        dfs = np.array(
            [
                self.discount_bond_pathwise(
                    start_index=exercise_index,
                    end_time=T,
                    path_index=path_index
                )
                for T in pay_dates
            ]
        )

        annuity = accrual * np.sum(
            dfs
        )

        if len(dfs) == 0:
            return 0.0, 0.0

        float_leg = (
            1.0
            -
            dfs[-1]
        )

        if abs(annuity) < 1e-12:
            return 0.0, annuity

        swap_rate = (
            float_leg
            /
            annuity
        )

        return swap_rate, annuity

    def immediate_exercise_values(
        self,
        exercise_index
    ):
        """
        Compute immediate exercise value for all paths at one exercise date.
        """

        n_paths = self.rate_paths.shape[0]

        values = np.zeros(
            n_paths
        )

        swap_rates = np.zeros(
            n_paths
        )

        annuities = np.zeros(
            n_paths
        )

        for path in range(n_paths):

            swap_rate, annuity = (
                self.swap_rate_and_annuity_pathwise(
                    exercise_index,
                    path
                )
            )

            swap_rates[path] = swap_rate
            annuities[path] = annuity

            if self.instrument.payer:

                swap_value = (
                    self.instrument.notional
                    *
                    annuity
                    *
                    (
                        swap_rate
                        -
                        self.instrument.fixed_rate
                    )
                )

            else:

                swap_value = (
                    self.instrument.notional
                    *
                    annuity
                    *
                    (
                        self.instrument.fixed_rate
                        -
                        swap_rate
                    )
                )

            values[path] = max(
                swap_value,
                0.0
            )

        return values, swap_rates, annuities

    def build_basis(
        self,
        exercise_index,
        path_indices,
        swap_rates
    ):
        """
        Build regression design matrix.
        """

        short_rates = self.rate_paths[
            path_indices,
            exercise_index
        ]

        if self.basis_type == "rate":

            return polynomial_basis(
                short_rates,
                degree=self.basis_degree
            )

        elif self.basis_type == "swap":

            return polynomial_basis(
                swap_rates[path_indices],
                degree=self.basis_degree
            )

        elif self.basis_type == "rate_swap":

            return rate_and_swap_basis(
                short_rates,
                swap_rates[path_indices],
                degree=self.basis_degree
            )

        else:

            raise ValueError(
                "basis_type must be 'rate', 'swap', or 'rate_swap'."
            )

    def price(
        self
    ):
        """
        Price Bermudan swaption using Longstaff-Schwartz Monte Carlo.

        Algorithm:
        ----------
        1. Start from final exercise date.
        2. Move backward through exercise dates.
        3. At each date, regress discounted future cashflows on state variables.
        4. Exercise if immediate value exceeds estimated continuation value.
        """

        n_paths = self.rate_paths.shape[0]

        n_steps = self.rate_paths.shape[1]

        cashflows = np.zeros(
            n_paths
        )

        exercise_time_index = np.full(
            n_paths,
            -1,
            dtype=int
        )

        exercise_flag_matrix = np.zeros(
            (
                n_paths,
                n_steps
            ),
            dtype=bool
        )

        self.regression_diagnostics = []

        exercise_indices_reversed = list(
            reversed(
                self.exercise_indices
            )
        )

        last_exercise_index = exercise_indices_reversed[0]

        immediate, swap_rates, annuities = (
            self.immediate_exercise_values(
                last_exercise_index
            )
        )

        cashflows = immediate.copy()

        exercised = immediate > 0.0

        exercise_time_index[exercised] = (
            last_exercise_index
        )

        exercise_flag_matrix[
            exercised,
            last_exercise_index
        ] = True

        for exercise_index in exercise_indices_reversed[1:]:

            immediate, swap_rates, annuities = (
                self.immediate_exercise_values(
                    exercise_index
                )
            )

            itm = immediate > 0.0

            active = (
                exercise_time_index
                >
                exercise_index
            ) | (
                exercise_time_index
                ==
                -1
            )

            regression_paths = np.where(
                itm & active
            )[0]

            continuation = np.zeros(
                n_paths
            )

            if len(regression_paths) > 5:

                future_indices = exercise_time_index[
                    regression_paths
                ]

                future_indices = np.where(
                    future_indices == -1,
                    self.exercise_indices[-1],
                    future_indices
                )

                discounted_future_values = np.zeros(
                    len(regression_paths)
                )

                for k, path in enumerate(regression_paths):

                    future_index = future_indices[k]

                    df = path_discount_factors_between_indices(
                        self.times,
                        self.rate_paths[[path], :],
                        exercise_index,
                        future_index
                    )[0]

                    discounted_future_values[k] = (
                        cashflows[path]
                        *
                        df
                    )

                X = self.build_basis(
                    exercise_index,
                    regression_paths,
                    swap_rates
                )

                beta, *_ = np.linalg.lstsq(
                    X,
                    discounted_future_values,
                    rcond=None
                )

                continuation[regression_paths] = (
                    X @ beta
                )

                self.regression_diagnostics.append(
                    {
                        "exercise_time": self.times[exercise_index],
                        "n_regression_paths": len(regression_paths),
                        "basis_type": self.basis_type,
                        "basis_degree": self.basis_degree,
                        "coefficients": beta
                    }
                )

            exercise_now = (
                itm
                &
                active
                &
                (
                    immediate > continuation
                )
            )

            cashflows[exercise_now] = immediate[
                exercise_now
            ]

            exercise_time_index[exercise_now] = (
                exercise_index
            )

            exercise_flag_matrix[
                exercise_now,
                :
            ] = False

            exercise_flag_matrix[
                exercise_now,
                exercise_index
            ] = True

        discounted_cashflows = np.zeros(
            n_paths
        )

        for path in range(n_paths):

            ex_idx = exercise_time_index[path]

            if ex_idx == -1:

                discounted_cashflows[path] = 0.0

            else:

                df = path_discount_factors_to_index(
                    self.times,
                    self.rate_paths[[path], :],
                    ex_idx
                )[0]

                discounted_cashflows[path] = (
                    cashflows[path]
                    *
                    df
                )

        self.cashflows = cashflows
        self.exercise_time_index = exercise_time_index
        self.exercise_flag_matrix = exercise_flag_matrix

        return float(
            np.mean(
                discounted_cashflows
            )
        )

    def exercise_summary(
        self
    ):
        """
        Return exercise distribution by time.
        """

        if self.exercise_time_index is None:
            raise ValueError(
                "Run price() before calling exercise_summary()."
            )

        rows = []

        for idx in self.exercise_indices:

            count = int(
                np.sum(
                    self.exercise_time_index
                    ==
                    idx
                )
            )

            rows.append(
                {
                    "time": self.times[idx],
                    "exercise_count": count,
                    "exercise_ratio": count / len(
                        self.exercise_time_index
                    )
                }
            )

        never = int(
            np.sum(
                self.exercise_time_index
                ==
                -1
            )
        )

        rows.append(
            {
                "time": np.nan,
                "exercise_count": never,
                "exercise_ratio": never / len(
                    self.exercise_time_index
                )
            }
        )

        return pd.DataFrame(rows)