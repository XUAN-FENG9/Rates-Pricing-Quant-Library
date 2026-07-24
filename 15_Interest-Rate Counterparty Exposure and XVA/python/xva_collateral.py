"""
Simple collateral and CSA mechanics.

The implementation supports bilateral thresholds,
minimum transfer amounts, independent amounts,
and a simple collateral lag.
"""

import numpy as np


class CSAParameters:
    """
    Simplified bilateral collateral agreement.
    """

    def __init__(
        self,
        counterparty_threshold=0.0,
        bank_threshold=0.0,
        minimum_transfer_amount=0.0,
        counterparty_independent_amount=0.0,
        bank_independent_amount=0.0,
        collateral_lag_steps=0
    ):
        self.counterparty_threshold = float(
            counterparty_threshold
        )

        self.bank_threshold = float(
            bank_threshold
        )

        self.minimum_transfer_amount = float(
            minimum_transfer_amount
        )

        self.counterparty_independent_amount = float(
            counterparty_independent_amount
        )

        self.bank_independent_amount = float(
            bank_independent_amount
        )

        self.collateral_lag_steps = int(
            collateral_lag_steps
        )

        self.validate()

    def validate(
        self
    ):
        """
        Validate CSA inputs.
        """

        values = [
            self.counterparty_threshold,
            self.bank_threshold,
            self.minimum_transfer_amount,
            self.counterparty_independent_amount,
            self.bank_independent_amount
        ]

        if any(
            value < 0.0
            for value in values
        ):
            raise ValueError(
                "CSA amounts and thresholds "
                "must be non-negative."
            )

        if self.collateral_lag_steps < 0:
            raise ValueError(
                "collateral_lag_steps cannot be negative."
            )

    def summary(
        self
    ):
        """
        Return the CSA settings.
        """

        return {
            "counterparty_threshold": (
                self.counterparty_threshold
            ),
            "bank_threshold": (
                self.bank_threshold
            ),
            "minimum_transfer_amount": (
                self.minimum_transfer_amount
            ),
            "counterparty_independent_amount": (
                self.counterparty_independent_amount
            ),
            "bank_independent_amount": (
                self.bank_independent_amount
            ),
            "collateral_lag_steps": (
                self.collateral_lag_steps
            )
        }


def target_collateral(
    portfolio_value,
    csa_parameters
):
    """
    Calculate the target signed collateral balance.

    Positive collateral is collateral held by the bank.

    Negative collateral is collateral posted by the bank.
    """

    value = float(
        portfolio_value
    )

    if value > (
        csa_parameters.counterparty_threshold
    ):
        collateral = (
            value
            -
            csa_parameters.counterparty_threshold
            +
            csa_parameters.counterparty_independent_amount
        )

    elif value < (
        -csa_parameters.bank_threshold
    ):
        collateral = (
            value
            +
            csa_parameters.bank_threshold
            -
            csa_parameters.bank_independent_amount
        )

    else:
        collateral = 0.0

    return collateral


def apply_minimum_transfer_amount(
    previous_collateral,
    target_balance,
    minimum_transfer_amount
):
    """
    Keep the previous collateral balance when the required
    transfer is smaller than the minimum transfer amount.
    """

    required_transfer = (
        target_balance
        -
        previous_collateral
    )

    if abs(
        required_transfer
    ) < minimum_transfer_amount:
        return previous_collateral

    return target_balance


def simulate_collateral_paths(
    portfolio_values,
    csa_parameters
):
    """
    Generate signed collateral balances for all paths.

    Parameters
    ----------
    portfolio_values
        Two-dimensional array [path, time].

    csa_parameters
        CSAParameters object.

    Returns
    -------
    collateral_paths
        Two-dimensional signed collateral array.
    """

    portfolio_values = np.asarray(
        portfolio_values,
        dtype=float
    )

    if portfolio_values.ndim != 2:
        raise ValueError(
            "portfolio_values must have dimensions "
            "[path, time]."
        )

    number_of_paths = (
        portfolio_values.shape[0]
    )

    number_of_times = (
        portfolio_values.shape[1]
    )

    immediate_targets = np.zeros_like(
        portfolio_values
    )

    for path_index in range(
        number_of_paths
    ):
        previous_collateral = 0.0

        for time_index in range(
            number_of_times
        ):
            target_balance = target_collateral(
                portfolio_value=portfolio_values[
                    path_index,
                    time_index
                ],
                csa_parameters=csa_parameters
            )

            current_collateral = (
                apply_minimum_transfer_amount(
                    previous_collateral=previous_collateral,
                    target_balance=target_balance,
                    minimum_transfer_amount=(
                        csa_parameters
                        .minimum_transfer_amount
                    )
                )
            )

            immediate_targets[
                path_index,
                time_index
            ] = current_collateral

            previous_collateral = (
                current_collateral
            )

    lag_steps = (
        csa_parameters.collateral_lag_steps
    )

    if lag_steps == 0:
        return immediate_targets

    collateral_paths = np.zeros_like(
        immediate_targets
    )

    for time_index in range(
        number_of_times
    ):
        source_index = (
            time_index
            -
            lag_steps
        )

        if source_index >= 0:
            collateral_paths[
                :,
                time_index
            ] = immediate_targets[
                :,
                source_index
            ]

    return collateral_paths


def collateralized_portfolio_values(
    portfolio_values,
    collateral_paths
):
    """
    Calculate residual values after collateral.

    Residual value = portfolio MtM - signed collateral.
    """

    portfolio_values = np.asarray(
        portfolio_values,
        dtype=float
    )

    collateral_paths = np.asarray(
        collateral_paths,
        dtype=float
    )

    if (
        portfolio_values.shape
        !=
        collateral_paths.shape
    ):
        raise ValueError(
            "portfolio_values and collateral_paths "
            "must have equal shape."
        )

    return (
        portfolio_values
        -
        collateral_paths
    )