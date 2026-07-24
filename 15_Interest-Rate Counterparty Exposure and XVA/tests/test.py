"""
Simple tests for Chapter 15 interest-rate exposure and XVA.

The tests use a small object with the same interface as the
Chapter 13 Gaussian LMM simulation output.

This keeps the unit tests fast and isolates the Chapter 15
exposure, collateral, and XVA calculations.
"""

import sys

from types import SimpleNamespace

import numpy as np
import pytest


# Run this file with the working directory set to:
#
#     15_interest_rate_exposure_and_xva/tests
#
sys.path.insert(
    0,
    "../python"
)

sys.path.insert(
    1,
    "../../13_gaussain_libor_market_model_lmm/python"
)


from xva_trade import (
    InterestRateSwap,
    NettingSet
)

from xva_exposure import (
    bond_prices_from_forwards,
    value_interest_rate_swap,
    simulate_portfolio_values
)

from xva_collateral import (
    CSAParameters,
    target_collateral,
    simulate_collateral_paths,
    collateralized_portfolio_values
)

from xva_metrics import (
    positive_exposure,
    negative_exposure,
    calculate_exposure_metrics
)

from xva_adjustments import (
    CreditCurve,
    calculate_cva,
    calculate_dva,
    calculate_xva
)


# ============================================================
# Test data builders
# ============================================================

def build_simple_model():
    """
    Build a small Chapter-13-compatible model object.

    The model contains a semiannual tenor from 0 to 2 years.
    """

    tenor_times = np.asarray(
        [
            0.0,
            0.5,
            1.0,
            1.5,
            2.0
        ],
        dtype=float
    )

    accruals = np.diff(
        tenor_times
    )

    initial_forwards = np.asarray(
        [
            0.030,
            0.032,
            0.034,
            0.036
        ],
        dtype=float
    )

    initial_discount_factors = np.ones(
        len(
            tenor_times
        ),
        dtype=float
    )

    for index in range(
        len(
            initial_forwards
        )
    ):
        initial_discount_factors[
            index + 1
        ] = (
            initial_discount_factors[
                index
            ]
            /
            (
                1.0
                +
                accruals[
                    index
                ]
                *
                initial_forwards[
                    index
                ]
            )
        )

    tenor = SimpleNamespace(
        times=tenor_times,
        accruals=accruals
    )

    model = SimpleNamespace(
        tenor=tenor,
        initial_forwards=initial_forwards,
        initial_discount_factors=(
            initial_discount_factors
        )
    )

    return model


def build_simple_simulation():
    """
    Build a small forward-path simulation.

    The output follows the Chapter 13 convention:

        forward_paths[path, time, forward]
    """

    model = build_simple_model()

    times = np.asarray(
        [
            0.0,
            0.5,
            1.0,
            1.5,
            2.0
        ],
        dtype=float
    )

    number_of_paths = 8
    number_of_times = len(
        times
    )
    number_of_forwards = len(
        model.initial_forwards
    )

    forward_paths = np.zeros(
        (
            number_of_paths,
            number_of_times,
            number_of_forwards
        ),
        dtype=float
    )

    path_shocks = np.asarray(
        [
            -0.010,
            -0.007,
            -0.004,
            -0.001,
            0.001,
            0.004,
            0.007,
            0.010
        ],
        dtype=float
    )

    for path_index in range(
        number_of_paths
    ):
        for time_index, time in enumerate(
            times
        ):
            maturity_scale = (
                time
                /
                times[-1]
            )

            path_curve = (
                model.initial_forwards
                +
                path_shocks[
                    path_index
                ]
                *
                maturity_scale
            )

            forward_paths[
                path_index,
                time_index,
                :
            ] = path_curve

    simulation = SimpleNamespace(
        times=times,
        forward_paths=forward_paths
    )

    return model, simulation


def build_single_swap_netting_set():
    """
    Build one payer-fixed swap.
    """

    swap = InterestRateSwap(
        trade_id="IRS_001",
        notional=1_000_000.0,
        fixed_rate=0.033,
        start_time=0.0,
        end_time=2.0,
        pay_fixed=True
    )

    netting_set = NettingSet(
        netting_set_id="NETTING_SET_001",
        trades=[
            swap
        ]
    )

    return swap, netting_set


# ============================================================
# Trade tests
# ============================================================

def test_interest_rate_swap_is_created():
    """
    A valid interest-rate swap should be created correctly.
    """

    swap = InterestRateSwap(
        trade_id="IRS_TEST",
        notional=1_000_000.0,
        fixed_rate=0.03,
        start_time=0.0,
        end_time=2.0,
        pay_fixed=True
    )

    assert swap.trade_id == "IRS_TEST"

    assert swap.notional == pytest.approx(
        1_000_000.0
    )

    assert swap.fixed_rate == pytest.approx(
        0.03
    )

    assert swap.pay_fixed


def test_invalid_swap_maturity_raises_error():
    """
    Swap maturity must be after the start date.
    """

    with pytest.raises(
        ValueError
    ):
        InterestRateSwap(
            trade_id="INVALID",
            notional=1_000_000.0,
            fixed_rate=0.03,
            start_time=2.0,
            end_time=1.0,
            pay_fixed=True
        )


def test_netting_set_contains_trades():
    """
    The netting set should store its trades.
    """

    swap, netting_set = (
        build_single_swap_netting_set()
    )

    assert netting_set.number_of_trades() == 1

    assert netting_set.trades[0] is swap

    assert netting_set.maturity() == pytest.approx(
        2.0
    )


# ============================================================
# Discount-factor and swap valuation tests
# ============================================================

def test_bond_prices_are_positive():
    """
    Discount factors reconstructed from positive forwards
    should remain positive.
    """

    forwards = np.asarray(
        [
            0.03,
            0.032,
            0.034,
            0.036
        ]
    )

    accruals = np.asarray(
        [
            0.5,
            0.5,
            0.5,
            0.5
        ]
    )

    bonds = bond_prices_from_forwards(
        forwards=forwards,
        accruals=accruals,
        current_tenor_index=0
    )

    assert np.all(
        bonds > 0.0
    )

    assert bonds[0] == pytest.approx(
        1.0
    )


def test_bond_prices_decrease_for_positive_rates():
    """
    Discount factors should decrease when forward rates
    are positive.
    """

    forwards = np.asarray(
        [
            0.03,
            0.032,
            0.034,
            0.036
        ]
    )

    accruals = np.full(
        4,
        0.5
    )

    bonds = bond_prices_from_forwards(
        forwards,
        accruals,
        0
    )

    assert np.all(
        np.diff(
            bonds
        )
        <
        0.0
    )


def test_payer_and_receiver_values_are_opposite():
    """
    Identical payer and receiver swaps should have opposite
    values.
    """

    model = build_simple_model()

    payer_swap = InterestRateSwap(
        trade_id="PAYER",
        notional=1_000_000.0,
        fixed_rate=0.033,
        start_time=0.0,
        end_time=2.0,
        pay_fixed=True
    )

    receiver_swap = InterestRateSwap(
        trade_id="RECEIVER",
        notional=1_000_000.0,
        fixed_rate=0.033,
        start_time=0.0,
        end_time=2.0,
        pay_fixed=False
    )

    payer_value = value_interest_rate_swap(
        trade=payer_swap,
        valuation_time=0.0,
        forwards=model.initial_forwards,
        model=model
    )

    receiver_value = value_interest_rate_swap(
        trade=receiver_swap,
        valuation_time=0.0,
        forwards=model.initial_forwards,
        model=model
    )

    assert payer_value == pytest.approx(
        -receiver_value
    )


def test_matured_swap_value_is_zero():
    """
    A swap should have zero value at or after maturity.
    """

    model = build_simple_model()

    swap, _ = build_single_swap_netting_set()

    value = value_interest_rate_swap(
        trade=swap,
        valuation_time=2.0,
        forwards=model.initial_forwards,
        model=model
    )

    assert value == pytest.approx(
        0.0
    )


# ============================================================
# Exposure simulation tests
# ============================================================

def test_exposure_simulation_dimensions():
    """
    Exposure simulation should return path-time-trade values
    and path-time portfolio values.
    """

    model, simulation = (
        build_simple_simulation()
    )

    _, netting_set = (
        build_single_swap_netting_set()
    )

    result = simulate_portfolio_values(
        model=model,
        simulation=simulation,
        netting_set=netting_set
    )

    assert result.trade_values.shape == (
        8,
        5,
        1
    )

    assert result.portfolio_values.shape == (
        8,
        5
    )

    assert result.number_of_paths() == 8

    assert result.number_of_times() == 5

    assert result.number_of_trades() == 1


def test_portfolio_value_is_zero_at_maturity():
    """
    All swap values should be zero at the final maturity.
    """

    model, simulation = (
        build_simple_simulation()
    )

    _, netting_set = (
        build_single_swap_netting_set()
    )

    result = simulate_portfolio_values(
        model=model,
        simulation=simulation,
        netting_set=netting_set
    )

    assert np.allclose(
        result.portfolio_values[
            :,
            -1
        ],
        0.0
    )


# ============================================================
# Exposure metric tests
# ============================================================

def test_positive_and_negative_exposure():
    """
    Positive and negative exposures should be non-negative.
    """

    portfolio_values = np.asarray(
        [
            [
                -10.0,
                5.0
            ],
            [
                20.0,
                -4.0
            ]
        ]
    )

    positive = positive_exposure(
        portfolio_values
    )

    negative = negative_exposure(
        portfolio_values
    )

    expected_positive = np.asarray(
        [
            [
                0.0,
                5.0
            ],
            [
                20.0,
                0.0
            ]
        ]
    )

    expected_negative = np.asarray(
        [
            [
                10.0,
                0.0
            ],
            [
                0.0,
                4.0
            ]
        ]
    )

    assert np.allclose(
        positive,
        expected_positive
    )

    assert np.allclose(
        negative,
        expected_negative
    )


def test_exposure_metrics_are_non_negative():
    """
    EE, ENE, EPE, and PFE should be non-negative.
    """

    model, simulation = (
        build_simple_simulation()
    )

    _, netting_set = (
        build_single_swap_netting_set()
    )

    exposure_result = simulate_portfolio_values(
        model=model,
        simulation=simulation,
        netting_set=netting_set
    )

    metrics = calculate_exposure_metrics(
        times=exposure_result.exposure_times,
        portfolio_values=(
            exposure_result.portfolio_values
        ),
        pfe_confidence_level=0.95
    )

    assert np.all(
        metrics.expected_exposure >= 0.0
    )

    assert np.all(
        metrics.expected_negative_exposure >= 0.0
    )

    assert np.all(
        metrics.potential_future_exposure >= 0.0
    )

    assert metrics.expected_positive_exposure >= 0.0

    assert (
        metrics.average_expected_negative_exposure
        >=
        0.0
    )


def test_pfe_confidence_level_is_stored():
    """
    The PFE confidence level should be retained.
    """

    times = np.asarray(
        [
            0.0,
            1.0
        ]
    )

    values = np.asarray(
        [
            [
                0.0,
                10.0
            ],
            [
                0.0,
                20.0
            ],
            [
                0.0,
                30.0
            ],
            [
                0.0,
                40.0
            ]
        ]
    )

    metrics = calculate_exposure_metrics(
        times=times,
        portfolio_values=values,
        pfe_confidence_level=0.95
    )

    assert metrics.pfe_confidence_level == pytest.approx(
        0.95
    )

    assert metrics.potential_future_exposure[-1] > 0.0


# ============================================================
# Collateral tests
# ============================================================

def test_target_collateral_with_zero_threshold():
    """
    With zero thresholds and zero MTA, target collateral
    should equal the portfolio value.
    """

    csa = CSAParameters(
        counterparty_threshold=0.0,
        bank_threshold=0.0,
        minimum_transfer_amount=0.0,
        collateral_lag_steps=0
    )

    assert target_collateral(
        100.0,
        csa
    ) == pytest.approx(
        100.0
    )

    assert target_collateral(
        -75.0,
        csa
    ) == pytest.approx(
        -75.0
    )


def test_perfect_collateral_removes_exposure():
    """
    Zero-threshold immediate collateral should remove all
    residual exposure in this simplified framework.
    """

    portfolio_values = np.asarray(
        [
            [
                100.0,
                -50.0,
                20.0
            ],
            [
                -80.0,
                40.0,
                0.0
            ]
        ]
    )

    csa = CSAParameters(
        counterparty_threshold=0.0,
        bank_threshold=0.0,
        minimum_transfer_amount=0.0,
        collateral_lag_steps=0
    )

    collateral = simulate_collateral_paths(
        portfolio_values=portfolio_values,
        csa_parameters=csa
    )

    residual_values = (
        collateralized_portfolio_values(
            portfolio_values=portfolio_values,
            collateral_paths=collateral
        )
    )

    assert np.allclose(
        collateral,
        portfolio_values
    )

    assert np.allclose(
        residual_values,
        0.0
    )


# ============================================================
# Credit and XVA tests
# ============================================================

def test_credit_survival_probability_decreases():
    """
    Survival probability should decrease through time.
    """

    credit_curve = CreditCurve(
        hazard_rate=0.02,
        recovery_rate=0.40
    )

    times = np.asarray(
        [
            0.0,
            1.0,
            2.0,
            3.0
        ]
    )

    survival = (
        credit_curve
        .survival_probability(
            times
        )
    )

    assert survival[0] == pytest.approx(
        1.0
    )

    assert np.all(
        np.diff(
            survival
        )
        <=
        0.0
    )


def test_cva_and_dva_are_non_negative():
    """
    CVA and DVA should be reported as positive amounts.
    """

    times = np.asarray(
        [
            0.0,
            1.0,
            2.0
        ]
    )

    ee = np.asarray(
        [
            100.0,
            80.0,
            0.0
        ]
    )

    ene = np.asarray(
        [
            50.0,
            40.0,
            0.0
        ]
    )

    discount_factors = np.asarray(
        [
            1.0,
            0.97,
            0.94
        ]
    )

    counterparty_curve = CreditCurve(
        hazard_rate=0.02,
        recovery_rate=0.40
    )

    bank_curve = CreditCurve(
        hazard_rate=0.01,
        recovery_rate=0.40
    )

    cva = calculate_cva(
        times=times,
        expected_exposure=ee,
        discount_factors=discount_factors,
        counterparty_credit_curve=(
            counterparty_curve
        )
    )

    dva = calculate_dva(
        times=times,
        expected_negative_exposure=ene,
        discount_factors=discount_factors,
        bank_credit_curve=bank_curve
    )

    assert cva >= 0.0

    assert dva >= 0.0


def test_complete_xva_calculation():
    """
    Complete XVA calculation should return all major
    components.
    """

    model, simulation = (
        build_simple_simulation()
    )

    _, netting_set = (
        build_single_swap_netting_set()
    )

    exposure_result = simulate_portfolio_values(
        model=model,
        simulation=simulation,
        netting_set=netting_set
    )

    metrics = calculate_exposure_metrics(
        times=exposure_result.exposure_times,
        portfolio_values=(
            exposure_result.portfolio_values
        ),
        pfe_confidence_level=0.95
    )

    counterparty_curve = CreditCurve(
        hazard_rate=0.02,
        recovery_rate=0.40
    )

    bank_curve = CreditCurve(
        hazard_rate=0.012,
        recovery_rate=0.40
    )

    results = calculate_xva(
        model=model,
        exposure_metrics=metrics,
        counterparty_credit_curve=(
            counterparty_curve
        ),
        bank_credit_curve=bank_curve,
        borrowing_spread=0.01,
        lending_spread=0.002
    )

    expected_keys = {
        "CVA",
        "DVA",
        "FCA",
        "FBA",
        "FVA",
        "net_valuation_adjustment"
    }

    assert expected_keys == set(
        results.keys()
    )

    assert results["CVA"] >= 0.0

    assert results["DVA"] >= 0.0

    assert results["FCA"] >= 0.0

    assert results["FBA"] >= 0.0