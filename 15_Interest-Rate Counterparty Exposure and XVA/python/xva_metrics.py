"""
Exposure metrics for counterparty credit risk.

The module calculates positive exposure, negative exposure,
EE, ENE, PFE, EPE, and related summary statistics.
"""

import numpy as np
import pandas as pd


class ExposureMetricsResult:
    """
    Container for exposure profiles and summary statistics.
    """

    def __init__(
        self,
        times,
        positive_exposure,
        negative_exposure,
        expected_exposure,
        expected_negative_exposure,
        potential_future_exposure,
        pfe_confidence_level,
        expected_positive_exposure,
        average_expected_negative_exposure
    ):
        self.times = np.asarray(
            times,
            dtype=float
        )

        self.positive_exposure = np.asarray(
            positive_exposure,
            dtype=float
        )

        self.negative_exposure = np.asarray(
            negative_exposure,
            dtype=float
        )

        self.expected_exposure = np.asarray(
            expected_exposure,
            dtype=float
        )

        self.expected_negative_exposure = np.asarray(
            expected_negative_exposure,
            dtype=float
        )

        self.potential_future_exposure = np.asarray(
            potential_future_exposure,
            dtype=float
        )

        self.pfe_confidence_level = float(
            pfe_confidence_level
        )

        self.expected_positive_exposure = float(
            expected_positive_exposure
        )

        self.average_expected_negative_exposure = float(
            average_expected_negative_exposure
        )

    def profile_table(
        self
    ):
        """
        Return EE, ENE, and PFE as a DataFrame.
        """

        return pd.DataFrame(
            {
                "time": self.times,
                "EE": self.expected_exposure,
                "ENE": self.expected_negative_exposure,
                "PFE": self.potential_future_exposure
            }
        )

    def summary(
        self
    ):
        """
        Return scalar exposure summaries.
        """

        return {
            "EPE": self.expected_positive_exposure,
            "average_ENE": (
                self.average_expected_negative_exposure
            ),
            "maximum_EE": float(
                np.max(
                    self.expected_exposure
                )
            ),
            "maximum_ENE": float(
                np.max(
                    self.expected_negative_exposure
                )
            ),
            "maximum_PFE": float(
                np.max(
                    self.potential_future_exposure
                )
            ),
            "PFE_confidence_level": (
                self.pfe_confidence_level
            )
        }


def positive_exposure(
    portfolio_values
):
    """
    Calculate pathwise positive exposure.
    """

    portfolio_values = np.asarray(
        portfolio_values,
        dtype=float
    )

    return np.maximum(
        portfolio_values,
        0.0
    )


def negative_exposure(
    portfolio_values
):
    """
    Calculate pathwise negative exposure as a positive amount.
    """

    portfolio_values = np.asarray(
        portfolio_values,
        dtype=float
    )

    return np.maximum(
        -portfolio_values,
        0.0
    )


def expected_exposure(
    portfolio_values
):
    """
    Calculate expected positive exposure at each time.
    """

    return np.mean(
        positive_exposure(
            portfolio_values
        ),
        axis=0
    )


def expected_negative_exposure(
    portfolio_values
):
    """
    Calculate expected negative exposure at each time.
    """

    return np.mean(
        negative_exposure(
            portfolio_values
        ),
        axis=0
    )


def potential_future_exposure(
    portfolio_values,
    confidence_level=0.95
):
    """
    Calculate PFE as a quantile of positive exposure.
    """

    if not (
        0.0
        <
        confidence_level
        <
        1.0
    ):
        raise ValueError(
            "confidence_level must lie between zero and one."
        )

    return np.quantile(
        positive_exposure(
            portfolio_values
        ),
        confidence_level,
        axis=0
    )


def time_weighted_average(
    times,
    values
):
    """
    Calculate a time-weighted average profile.

    The result uses trapezoidal integration over the
    exposure horizon.
    """

    times = np.asarray(
        times,
        dtype=float
    )

    values = np.asarray(
        values,
        dtype=float
    )

    if len(
        times
    ) != len(
        values
    ):
        raise ValueError(
            "times and values must have equal length."
        )

    if len(
        times
    ) == 1:
        return float(
            values[0]
        )

    horizon = (
        times[-1]
        -
        times[0]
    )

    if horizon <= 0.0:
        return float(
            np.mean(
                values
            )
        )

    return float(
        np.trapezoid(
            values,
            times
        )
        /
        horizon
    )


def calculate_exposure_metrics(
    times,
    portfolio_values,
    pfe_confidence_level=0.95
):
    """
    Calculate the main exposure profiles and statistics.
    """

    times = np.asarray(
        times,
        dtype=float
    )

    portfolio_values = np.asarray(
        portfolio_values,
        dtype=float
    )

    if portfolio_values.ndim != 2:
        raise ValueError(
            "portfolio_values must have dimensions "
            "[path, time]."
        )

    if (
        portfolio_values.shape[1]
        !=
        len(
            times
        )
    ):
        raise ValueError(
            "Time dimension does not match portfolio values."
        )

    positive = positive_exposure(
        portfolio_values
    )

    negative = negative_exposure(
        portfolio_values
    )

    ee = np.mean(
        positive,
        axis=0
    )

    ene = np.mean(
        negative,
        axis=0
    )

    pfe = potential_future_exposure(
        portfolio_values=portfolio_values,
        confidence_level=pfe_confidence_level
    )

    epe = time_weighted_average(
        times=times,
        values=ee
    )

    average_ene = time_weighted_average(
        times=times,
        values=ene
    )

    return ExposureMetricsResult(
        times=times,
        positive_exposure=positive,
        negative_exposure=negative,
        expected_exposure=ee,
        expected_negative_exposure=ene,
        potential_future_exposure=pfe,
        pfe_confidence_level=pfe_confidence_level,
        expected_positive_exposure=epe,
        average_expected_negative_exposure=(
            average_ene
        )
    )


def compare_exposure_profiles(
    uncollateralized_metrics,
    collateralized_metrics
):
    """
    Compare uncollateralized and collateralized profiles.
    """

    if not np.allclose(
        uncollateralized_metrics.times,
        collateralized_metrics.times
    ):
        raise ValueError(
            "Exposure profiles must use the same times."
        )

    return pd.DataFrame(
        {
            "time": (
                uncollateralized_metrics.times
            ),
            "EE_uncollateralized": (
                uncollateralized_metrics
                .expected_exposure
            ),
            "EE_collateralized": (
                collateralized_metrics
                .expected_exposure
            ),
            "PFE_uncollateralized": (
                uncollateralized_metrics
                .potential_future_exposure
            ),
            "PFE_collateralized": (
                collateralized_metrics
                .potential_future_exposure
            )
        }
    )