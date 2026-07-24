"""
Simplified CVA, DVA, and FVA calculations.

The implementation uses deterministic discount factors,
flat hazard rates, constant recovery rates, and discrete
exposure integration.
"""

import numpy as np


class CreditCurve:
    """
    Flat-hazard credit curve.
    """

    def __init__(
        self,
        hazard_rate,
        recovery_rate
    ):
        self.hazard_rate = float(
            hazard_rate
        )

        self.recovery_rate = float(
            recovery_rate
        )

        self.validate()

    def validate(
        self
    ):
        """
        Validate credit-curve parameters.
        """

        if self.hazard_rate < 0.0:
            raise ValueError(
                "hazard_rate must be non-negative."
            )

        if not (
            0.0
            <=
            self.recovery_rate
            <=
            1.0
        ):
            raise ValueError(
                "recovery_rate must lie between zero and one."
            )

    def survival_probability(
        self,
        times
    ):
        """
        Calculate survival probability.
        """

        times = np.asarray(
            times,
            dtype=float
        )

        return np.exp(
            -self.hazard_rate
            *
            times
        )

    def default_probability_increments(
        self,
        times
    ):
        """
        Calculate marginal default probabilities between dates.
        """

        times = np.asarray(
            times,
            dtype=float
        )

        survival = self.survival_probability(
            times
        )

        previous_survival = np.concatenate(
            (
                np.array(
                    [
                        1.0
                    ]
                ),
                survival[:-1]
            )
        )

        default_increments = (
            previous_survival
            -
            survival
        )

        return np.maximum(
            default_increments,
            0.0
        )

    def loss_given_default(
        self
    ):
        """
        Return one minus recovery.
        """

        return (
            1.0
            -
            self.recovery_rate
        )


def interpolate_initial_discount_factors(
    model,
    times
):
    """
    Interpolate initial discount factors to exposure dates.
    """

    times = np.asarray(
        times,
        dtype=float
    )

    if hasattr(
        model,
        "initial_discount_factors"
    ):
        discount_factors = np.asarray(
            model.initial_discount_factors,
            dtype=float
        )

    elif hasattr(
        model,
        "initialDiscountFactors"
    ):
        discount_factors = np.asarray(
            model.initialDiscountFactors,
            dtype=float
        )

    else:
        raise AttributeError(
            "The model must contain initial discount factors."
        )

    if hasattr(
        model,
        "tenor"
    ):
        tenor_times = np.asarray(
            model.tenor.times,
            dtype=float
        )

    elif hasattr(
        model,
        "tenor_structure"
    ):
        tenor_times = np.asarray(
            model.tenor_structure.times,
            dtype=float
        )

    else:
        raise AttributeError(
            "The model must contain tenor information."
        )

    return np.interp(
        times,
        tenor_times,
        discount_factors
    )


def calculate_cva(
    times,
    expected_exposure,
    discount_factors,
    counterparty_credit_curve
):
    """
    Calculate unilateral CVA.

    CVA is returned as a positive valuation cost.
    """

    times = np.asarray(
        times,
        dtype=float
    )

    expected_exposure = np.asarray(
        expected_exposure,
        dtype=float
    )

    discount_factors = np.asarray(
        discount_factors,
        dtype=float
    )

    default_increments = (
        counterparty_credit_curve
        .default_probability_increments(
            times
        )
    )

    cva = (
        counterparty_credit_curve
        .loss_given_default()
        *
        np.sum(
            discount_factors
            *
            expected_exposure
            *
            default_increments
        )
    )

    return float(
        cva
    )


def calculate_dva(
    times,
    expected_negative_exposure,
    discount_factors,
    bank_credit_curve
):
    """
    Calculate DVA as a positive valuation benefit.
    """

    times = np.asarray(
        times,
        dtype=float
    )

    expected_negative_exposure = np.asarray(
        expected_negative_exposure,
        dtype=float
    )

    discount_factors = np.asarray(
        discount_factors,
        dtype=float
    )

    default_increments = (
        bank_credit_curve
        .default_probability_increments(
            times
        )
    )

    dva = (
        bank_credit_curve
        .loss_given_default()
        *
        np.sum(
            discount_factors
            *
            expected_negative_exposure
            *
            default_increments
        )
    )

    return float(
        dva
    )


def calculate_funding_adjustments(
    times,
    expected_exposure,
    expected_negative_exposure,
    discount_factors,
    borrowing_spread,
    lending_spread=0.0
):
    """
    Calculate simple funding cost and benefit adjustments.

    FCA represents the cost of funding positive exposure.

    FBA represents a benefit associated with negative exposure.

    FVA is reported as:

        FVA = FCA - FBA
    """

    times = np.asarray(
        times,
        dtype=float
    )

    ee = np.asarray(
        expected_exposure,
        dtype=float
    )

    ene = np.asarray(
        expected_negative_exposure,
        dtype=float
    )

    discount_factors = np.asarray(
        discount_factors,
        dtype=float
    )

    borrowing_spread = float(
        borrowing_spread
    )

    lending_spread = float(
        lending_spread
    )

    if borrowing_spread < 0.0:
        raise ValueError(
            "borrowing_spread must be non-negative."
        )

    if lending_spread < 0.0:
        raise ValueError(
            "lending_spread must be non-negative."
        )

    if len(
        times
    ) == 1:
        time_steps = np.array(
            [
                0.0
            ]
        )

    else:
        time_steps = np.diff(
            times,
            prepend=times[0]
        )

    fca = np.sum(
        discount_factors
        *
        ee
        *
        borrowing_spread
        *
        time_steps
    )

    fba = np.sum(
        discount_factors
        *
        ene
        *
        lending_spread
        *
        time_steps
    )

    return {
        "FCA": float(
            fca
        ),
        "FBA": float(
            fba
        ),
        "FVA": float(
            fca
            -
            fba
        )
    }


def calculate_xva(
    model,
    exposure_metrics,
    counterparty_credit_curve,
    bank_credit_curve,
    borrowing_spread,
    lending_spread=0.0
):
    """
    Calculate CVA, DVA, FCA, FBA, FVA, and net adjustment.
    """

    times = exposure_metrics.times

    discount_factors = (
        interpolate_initial_discount_factors(
            model=model,
            times=times
        )
    )

    cva = calculate_cva(
        times=times,
        expected_exposure=(
            exposure_metrics.expected_exposure
        ),
        discount_factors=discount_factors,
        counterparty_credit_curve=(
            counterparty_credit_curve
        )
    )

    dva = calculate_dva(
        times=times,
        expected_negative_exposure=(
            exposure_metrics
            .expected_negative_exposure
        ),
        discount_factors=discount_factors,
        bank_credit_curve=bank_credit_curve
    )

    funding = calculate_funding_adjustments(
        times=times,
        expected_exposure=(
            exposure_metrics.expected_exposure
        ),
        expected_negative_exposure=(
            exposure_metrics
            .expected_negative_exposure
        ),
        discount_factors=discount_factors,
        borrowing_spread=borrowing_spread,
        lending_spread=lending_spread
    )

    net_adjustment = (
        -cva
        +
        dva
        -
        funding[
            "FVA"
        ]
    )

    return {
        "CVA": cva,
        "DVA": dva,
        "FCA": funding["FCA"],
        "FBA": funding["FBA"],
        "FVA": funding["FVA"],
        "net_valuation_adjustment": float(
            net_adjustment
        )
    }