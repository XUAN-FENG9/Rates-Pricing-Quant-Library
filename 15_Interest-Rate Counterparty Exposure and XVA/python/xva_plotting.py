"""
Plotting functions for exposure and XVA analysis.
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_exposure_profile(
    exposure_metrics,
    title="Interest-Rate Exposure Profile"
):
    """
    Plot EE, ENE, and PFE.
    """

    plt.figure(
        figsize=(
            10,
            6
        )
    )

    plt.plot(
        exposure_metrics.times,
        exposure_metrics.expected_exposure,
        marker="o",
        label="EE"
    )

    plt.plot(
        exposure_metrics.times,
        exposure_metrics.expected_negative_exposure,
        marker="o",
        label="ENE"
    )

    pfe_label = (
        f"PFE "
        f"{exposure_metrics.pfe_confidence_level:.0%}"
    )

    plt.plot(
        exposure_metrics.times,
        exposure_metrics.potential_future_exposure,
        marker="o",
        label=pfe_label
    )

    plt.title(
        title
    )

    plt.xlabel(
        "Time"
    )

    plt.ylabel(
        "Exposure"
    )

    plt.grid()

    plt.legend()

    plt.tight_layout()

    plt.show()


def plot_portfolio_value_distribution(
    exposure_times,
    portfolio_values,
    selected_time,
    number_of_bins=50
):
    """
    Plot the future portfolio MtM distribution.
    """

    exposure_times = np.asarray(
        exposure_times,
        dtype=float
    )

    differences = np.abs(
        exposure_times
        -
        float(
            selected_time
        )
    )

    time_index = int(
        np.argmin(
            differences
        )
    )

    if differences[
        time_index
    ] > 1.0e-10:
        raise ValueError(
            "selected_time is not present "
            "on the exposure grid."
        )

    values = np.asarray(
        portfolio_values,
        dtype=float
    )[
        :,
        time_index
    ]

    plt.figure(
        figsize=(
            9,
            6
        )
    )

    plt.hist(
        values,
        bins=number_of_bins
    )

    plt.axvline(
        0.0,
        linestyle="--"
    )

    plt.title(
        f"Portfolio Value Distribution at t={selected_time:.2f}"
    )

    plt.xlabel(
        "Portfolio Value"
    )

    plt.ylabel(
        "Frequency"
    )

    plt.grid()

    plt.tight_layout()

    plt.show()


def plot_collateral_comparison(
    uncollateralized_metrics,
    collateralized_metrics
):
    """
    Compare EE and PFE before and after collateral.
    """

    if not np.allclose(
        uncollateralized_metrics.times,
        collateralized_metrics.times
    ):
        raise ValueError(
            "Exposure profiles must use the same times."
        )

    times = (
        uncollateralized_metrics.times
    )

    plt.figure(
        figsize=(
            10,
            6
        )
    )

    plt.plot(
        times,
        uncollateralized_metrics.expected_exposure,
        marker="o",
        label="EE Uncollateralized"
    )

    plt.plot(
        times,
        collateralized_metrics.expected_exposure,
        marker="o",
        label="EE Collateralized"
    )

    plt.plot(
        times,
        uncollateralized_metrics.potential_future_exposure,
        linestyle="--",
        label="PFE Uncollateralized"
    )

    plt.plot(
        times,
        collateralized_metrics.potential_future_exposure,
        linestyle="--",
        label="PFE Collateralized"
    )

    plt.title(
        "Collateral Impact on Exposure"
    )

    plt.xlabel(
        "Time"
    )

    plt.ylabel(
        "Exposure"
    )

    plt.grid()

    plt.legend()

    plt.tight_layout()

    plt.show()


def plot_mean_collateral_profile(
    exposure_times,
    collateral_paths
):
    """
    Plot mean collateral held and posted.
    """

    collateral_paths = np.asarray(
        collateral_paths,
        dtype=float
    )

    collateral_received = np.maximum(
        collateral_paths,
        0.0
    )

    collateral_posted = np.maximum(
        -collateral_paths,
        0.0
    )

    mean_received = np.mean(
        collateral_received,
        axis=0
    )

    mean_posted = np.mean(
        collateral_posted,
        axis=0
    )

    plt.figure(
        figsize=(
            10,
            6
        )
    )

    plt.plot(
        exposure_times,
        mean_received,
        marker="o",
        label="Mean Collateral Received"
    )

    plt.plot(
        exposure_times,
        mean_posted,
        marker="o",
        label="Mean Collateral Posted"
    )

    plt.title(
        "Expected Collateral Profile"
    )

    plt.xlabel(
        "Time"
    )

    plt.ylabel(
        "Collateral Amount"
    )

    plt.grid()

    plt.legend()

    plt.tight_layout()

    plt.show()


def plot_xva_components(
    xva_results
):
    """
    Plot CVA, DVA, and funding components.
    """

    labels = [
        "CVA",
        "DVA",
        "FCA",
        "FBA",
        "FVA"
    ]

    values = [
        xva_results[
            label
        ]
        for label in labels
    ]

    plt.figure(
        figsize=(
            9,
            6
        )
    )

    plt.bar(
        labels,
        values
    )

    plt.title(
        "XVA Components"
    )

    plt.xlabel(
        "Adjustment"
    )

    plt.ylabel(
        "Amount"
    )

    plt.grid(
        axis="y"
    )

    plt.tight_layout()

    plt.show()