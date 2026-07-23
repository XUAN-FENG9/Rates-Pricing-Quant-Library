"""
test.py

Unit tests for Chapter 14:
LMM-SABR Hybrid Model.

This test file reuses Chapter 13 modules:

    market_data.py
    tenor_structure.py
    correlation.py
    volatility.py

Chapter 14 modules:

    sabr_parameters.py
    lmm_sabr_hybrid.py
    simulation.py
    pricing.py
    diagnostics.py

Run from the project root with:

    pytest 14_lmm_sabr_hybrid_model/tests/test.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest


# ============================================================
# 1. Project paths



CHAPTER14_PYTHON = Path(
    "../python"
)

CHAPTER13_PYTHON = Path(
    "../../13_gaussain_libor_market_model_lmm/python"
)

sys.path.append(
    str(
        CHAPTER13_PYTHON
    )
)

sys.path.append(
    str(
        CHAPTER14_PYTHON
    )
)

# ============================================================
# 2. Imports
# ============================================================

from market_data import load_curve_data

from tenor_structure import TenorStructure

from correlation import (
    exponential_correlation_matrix,
    principal_component_loadings
)

from volatility import (
    GaussianLMMVolatility
)

from sabr_parameters import (
    SABRParameters
)

from lmm_sabr_hybrid import (
    LMMSABRHybrid
)

from sabr_simulation import (
    build_time_grid,
    exact_time_index,
    simulate_lmm_sabr
)

from lmm_sabr_pricing import (
    bond_prices_from_forwards,
    swap_annuity_and_rate,
    price_caplet_mc,
    price_payer_swaption_mc
)

from sabr_diagnostics import (
    last_forward_drift_check,
    alpha_positivity_check,
    forward_validity_check
)


# ============================================================
# 3. Helper functions
# ============================================================

def build_test_model(
    nu=0.40,
    rho=-0.25,
    beta=0.50,
    alpha0=0.18,
    shift=0.03
):
    """
    Build a small LMM-SABR model for unit testing.

    A five-year semiannual tenor is used to keep tests fast.
    """

    curve_path = (
        "../data/usd_zero_curve.csv"
    )

    curve = load_curve_data(
        curve_path
    )

    tenor = TenorStructure(
        start=0.0,
        end=5.0,
        payment_frequency=2
    )

    initial_forwards = (
        tenor.initial_forward_rates(
            curve
        )
    )

    initial_discount_factors = (
        tenor.initial_discount_factors(
            curve
        )
    )

    reset_times = np.asarray(
        tenor.times[:-1],
        dtype=float
    )

    correlation_matrix = (
        exponential_correlation_matrix(
            reset_times,
            beta=0.10
        )
    )

    correlation_loadings = (
        principal_component_loadings(
            correlation_matrix,
            n_factors=3
        )
    )

    deterministic_volatility_model = (
        GaussianLMMVolatility(
            reset_times=reset_times,
            sigma_level=0.25,
            decay=0.05,
            floor=0.05
        )
    )

    number_of_forwards = len(
        initial_forwards
    )

    sabr_parameters = SABRParameters(
        number_of_forwards=number_of_forwards,
        alpha0=alpha0,
        beta=beta,
        rho=rho,
        nu=nu,
        shift=shift,
        alpha_floor=1.0e-8,
        alpha_cap=10.0
    )

    model = LMMSABRHybrid(
        tenor_structure=tenor,
        initial_forwards=initial_forwards,
        deterministic_volatility_model=(
            deterministic_volatility_model
        ),
        correlation_loadings=(
            correlation_loadings
        ),
        initial_discount_factors=(
            initial_discount_factors
        ),
        sabr_parameters=(
            sabr_parameters
        )
    )

    return model


def build_test_simulation(
    model,
    number_of_paths=300,
    seed=42
):
    """
    Build a small simulation for unit tests.
    """

    mandatory_times = np.asarray(
        [
            0.5,
            1.0,
            1.5,
            2.0
        ],
        dtype=float
    )

    simulation = simulate_lmm_sabr(
        model=model,
        simulation_end=2.0,
        number_of_steps=40,
        number_of_paths=number_of_paths,
        seed=seed,
        antithetic=True,
        mandatory_times=mandatory_times
    )

    return simulation


# ============================================================
# 4. SABR parameter tests
# ============================================================

def test_scalar_parameters_expand_to_vectors():
    """
    Scalar SABR inputs should be expanded to one value per forward.
    """

    parameters = SABRParameters(
        number_of_forwards=6,
        alpha0=0.20,
        beta=0.50,
        rho=-0.30,
        nu=0.40,
        shift=0.03
    )

    assert parameters.alpha0.shape == (
        6,
    )

    assert parameters.beta.shape == (
        6,
    )

    assert parameters.rho.shape == (
        6,
    )

    assert parameters.nu.shape == (
        6,
    )

    assert parameters.shift.shape == (
        6,
    )

    assert np.allclose(
        parameters.alpha0,
        0.20
    )

    assert np.allclose(
        parameters.beta,
        0.50
    )

    assert np.allclose(
        parameters.rho,
        -0.30
    )

    assert np.allclose(
        parameters.nu,
        0.40
    )

    assert np.allclose(
        parameters.shift,
        0.03
    )


def test_vector_parameters_are_preserved():
    """
    Forward-specific input vectors should be preserved.
    """

    alpha0 = np.asarray(
        [
            0.15,
            0.16,
            0.17
        ]
    )

    beta = np.asarray(
        [
            0.40,
            0.50,
            0.60
        ]
    )

    parameters = SABRParameters(
        number_of_forwards=3,
        alpha0=alpha0,
        beta=beta,
        rho=-0.25,
        nu=0.40,
        shift=0.03
    )

    assert np.allclose(
        parameters.alpha0,
        alpha0
    )

    assert np.allclose(
        parameters.beta,
        beta
    )


def test_invalid_beta_raises_error():
    """
    SABR beta must lie between zero and one.
    """

    with pytest.raises(
        ValueError
    ):

        SABRParameters(
            number_of_forwards=4,
            beta=1.20
        )


def test_invalid_rho_raises_error():
    """
    SABR rho must lie strictly between minus one and one.
    """

    with pytest.raises(
        ValueError
    ):

        SABRParameters(
            number_of_forwards=4,
            rho=1.0
        )


def test_negative_nu_raises_error():
    """
    Volatility of volatility cannot be negative.
    """

    with pytest.raises(
        ValueError
    ):

        SABRParameters(
            number_of_forwards=4,
            nu=-0.10
        )


def test_negative_shift_raises_error():
    """
    The displacement cannot be negative.
    """

    with pytest.raises(
        ValueError
    ):

        SABRParameters(
            number_of_forwards=4,
            shift=-0.01
        )


# ============================================================
# 5. Model construction tests
# ============================================================

def test_model_dimensions():
    """
    Model dimensions should agree with the tenor and PCA loadings.
    """

    model = build_test_model()

    assert model.number_of_forwards == len(
        model.initial_forwards
    )

    assert model.number_of_factors == 3

    assert model.correlation_loadings.shape == (
        model.number_of_forwards,
        model.number_of_factors
    )

    assert len(
        model.initial_discount_factors
    ) == (
        model.number_of_forwards + 1
    )


def test_initial_state_is_valid():
    """
    The initial forward and alpha state should satisfy all restrictions.
    """

    model = build_test_model()

    model.validate_state(
        model.initial_forwards,
        model.sabr_parameters.alpha0
    )


def test_factor_loading_dimensions():
    """
    Factor-loading matrix should have one row per forward
    and one column per retained rate factor.
    """

    model = build_test_model()

    loadings = model.factor_loadings(
        time=0.0,
        forwards=model.initial_forwards,
        alpha=model.sabr_parameters.alpha0
    )

    assert loadings.shape == (
        model.number_of_forwards,
        model.number_of_factors
    )

    assert np.all(
        np.isfinite(
            loadings
        )
    )


def test_covariance_matrix_is_symmetric():
    """
    Lambda multiplied by Lambda-transpose should be symmetric.
    """

    model = build_test_model()

    covariance = (
        model.instantaneous_covariance_matrix(
            time=0.0,
            forwards=model.initial_forwards,
            alpha=model.sabr_parameters.alpha0
        )
    )

    assert covariance.shape == (
        model.number_of_forwards,
        model.number_of_forwards
    )

    assert np.allclose(
        covariance,
        covariance.T,
        atol=1.0e-12
    )


def test_covariance_diagonal_is_non_negative():
    """
    All instantaneous variances must be non-negative.
    """

    model = build_test_model()

    covariance = (
        model.instantaneous_covariance_matrix(
            time=0.0,
            forwards=model.initial_forwards,
            alpha=model.sabr_parameters.alpha0
        )
    )

    assert np.all(
        np.diag(
            covariance
        )
        >=
        -1.0e-14
    )


# ============================================================
# 6. Terminal-measure drift tests
# ============================================================

def test_last_forward_drift_is_zero():
    """
    The final forward has zero drift under the terminal measure.
    """

    model = build_test_model()

    drift = model.terminal_measure_drift(
        time=0.0,
        forwards=model.initial_forwards,
        alpha=model.sabr_parameters.alpha0
    )

    assert abs(
        drift[-1]
    ) < 1.0e-12


def test_drift_vector_has_correct_dimension():
    """
    There should be one drift value per forward rate.
    """

    model = build_test_model()

    drift = model.terminal_measure_drift(
        time=0.0,
        forwards=model.initial_forwards,
        alpha=model.sabr_parameters.alpha0
    )

    assert drift.shape == (
        model.number_of_forwards,
    )

    assert np.all(
        np.isfinite(
            drift
        )
    )


def test_diagnostic_last_forward_drift():
    """
    The diagnostic helper should report a near-zero final drift.
    """

    model = build_test_model()

    result = last_forward_drift_check(
        model,
        time=0.0
    )

    assert result[
        "absolute_error"
    ] < 1.0e-12


# ============================================================
# 7. One-step evolution tests
# ============================================================

def test_one_step_evolution_dimensions():
    """
    One evolution step should return one forward vector
    and one alpha vector.
    """

    model = build_test_model()

    rate_shocks = np.zeros(
        model.number_of_factors
    )

    volatility_shocks = np.zeros(
        model.number_of_forwards
    )

    next_forwards, next_alpha = model.evolve(
        time=0.0,
        forwards=model.initial_forwards,
        alpha=model.sabr_parameters.alpha0,
        dt=0.01,
        rate_factor_shocks=rate_shocks,
        independent_volatility_shocks=(
            volatility_shocks
        )
    )

    assert next_forwards.shape == (
        model.number_of_forwards,
    )

    assert next_alpha.shape == (
        model.number_of_forwards,
    )


def test_zero_nu_keeps_alpha_constant():
    """
    When nu equals zero, stochastic volatility should remain constant.
    """

    model = build_test_model(
        nu=0.0
    )

    rate_shocks = np.asarray(
        [
            0.50,
            -0.20,
            0.80
        ]
    )

    volatility_shocks = np.ones(
        model.number_of_forwards
    )

    next_forwards, next_alpha = model.evolve(
        time=0.0,
        forwards=model.initial_forwards,
        alpha=model.sabr_parameters.alpha0,
        dt=0.05,
        rate_factor_shocks=rate_shocks,
        independent_volatility_shocks=(
            volatility_shocks
        )
    )

    assert np.allclose(
        next_alpha,
        model.sabr_parameters.alpha0,
        atol=1.0e-14
    )


def test_alpha_remains_positive_after_evolution():
    """
    The lognormal alpha step should preserve positivity.
    """

    model = build_test_model()

    rate_shocks = np.asarray(
        [
            1.0,
            -0.5,
            0.25
        ]
    )

    volatility_shocks = np.linspace(
        -1.0,
        1.0,
        model.number_of_forwards
    )

    next_forwards, next_alpha = model.evolve(
        time=0.0,
        forwards=model.initial_forwards,
        alpha=model.sabr_parameters.alpha0,
        dt=0.05,
        rate_factor_shocks=rate_shocks,
        independent_volatility_shocks=(
            volatility_shocks
        )
    )

    assert np.all(
        next_alpha > 0.0
    )


def test_fixed_forward_does_not_move():
    """
    A forward whose reset date has passed should remain fixed.
    """

    model = build_test_model()

    current_time = 1.0

    active = model.active_mask(
        current_time
    )

    rate_shocks = np.ones(
        model.number_of_factors
    )

    volatility_shocks = np.ones(
        model.number_of_forwards
    )

    next_forwards, next_alpha = model.evolve(
        time=current_time,
        forwards=model.initial_forwards,
        alpha=model.sabr_parameters.alpha0,
        dt=0.01,
        rate_factor_shocks=rate_shocks,
        independent_volatility_shocks=(
            volatility_shocks
        )
    )

    fixed_indices = np.where(
        active == False
    )[0]

    assert np.allclose(
        next_forwards[
            fixed_indices
        ],
        model.initial_forwards[
            fixed_indices
        ]
    )

    assert np.allclose(
        next_alpha[
            fixed_indices
        ],
        model.sabr_parameters.alpha0[
            fixed_indices
        ]
    )


# ============================================================
# 8. Time-grid tests
# ============================================================

def test_time_grid_contains_mandatory_dates():
    """
    Mandatory dates should appear exactly on the simulation grid.
    """

    mandatory_times = np.asarray(
        [
            0.5,
            1.0,
            1.75
        ]
    )

    times = build_time_grid(
        simulation_end=2.0,
        number_of_steps=10,
        mandatory_times=mandatory_times
    )

    for time in mandatory_times:

        index = exact_time_index(
            times,
            time
        )

        assert abs(
            times[index]
            -
            time
        ) < 1.0e-12


def test_exact_time_index_rejects_missing_time():
    """
    A time not represented on the grid should raise an error.
    """

    times = np.asarray(
        [
            0.0,
            0.5,
            1.0
        ]
    )

    with pytest.raises(
        ValueError
    ):

        exact_time_index(
            times,
            0.75
        )


# ============================================================
# 9. Simulation tests
# ============================================================

def test_simulation_dimensions():
    """
    Forward and alpha paths should have dimensions:

        path x time x forward.
    """

    model = build_test_model()

    simulation = build_test_simulation(
        model,
        number_of_paths=100
    )

    assert simulation.forward_paths.shape[0] == 100

    assert simulation.alpha_paths.shape[0] == 100

    assert simulation.forward_paths.shape[1] == len(
        simulation.times
    )

    assert simulation.forward_paths.shape[2] == (
        model.number_of_forwards
    )

    assert simulation.forward_paths.shape == (
        simulation.alpha_paths.shape
    )


def test_simulation_initial_state():
    """
    Every path should begin from the same initial forward
    and alpha vectors.
    """

    model = build_test_model()

    simulation = build_test_simulation(
        model,
        number_of_paths=100
    )

    expected_forwards = np.tile(
        model.initial_forwards,
        (
            simulation.get_number_of_paths(),
            1
        )
    )

    expected_alpha = np.tile(
        model.sabr_parameters.alpha0,
        (
            simulation.get_number_of_paths(),
            1
        )
    )

    assert np.allclose(
        simulation.forward_paths[
            :,
            0,
            :
        ],
        expected_forwards
    )

    assert np.allclose(
        simulation.alpha_paths[
            :,
            0,
            :
        ],
        expected_alpha
    )


def test_simulated_alpha_is_positive():
    """
    All simulated stochastic-volatility values should be positive.
    """

    model = build_test_model()

    simulation = build_test_simulation(
        model,
        number_of_paths=200
    )

    result = alpha_positivity_check(
        simulation
    )

    assert result[
        "all_positive"
    ]


def test_simulated_forward_denominators_are_positive():
    """
    All simulated states should satisfy:

        1 + delta * L > 0.
    """

    model = build_test_model()

    simulation = build_test_simulation(
        model,
        number_of_paths=200
    )

    result = forward_validity_check(
        model,
        simulation
    )

    assert result[
        "all_valid"
    ]


def test_simulation_is_reproducible():
    """
    Equal seeds should generate equal simulated paths.
    """

    model = build_test_model()

    simulation_1 = build_test_simulation(
        model,
        number_of_paths=60,
        seed=123
    )

    simulation_2 = build_test_simulation(
        model,
        number_of_paths=60,
        seed=123
    )

    assert np.allclose(
        simulation_1.forward_paths,
        simulation_2.forward_paths
    )

    assert np.allclose(
        simulation_1.alpha_paths,
        simulation_2.alpha_paths
    )


def test_nu_zero_produces_constant_alpha_paths():
    """
    When nu is zero, every alpha path should remain constant.
    """

    model = build_test_model(
        nu=0.0
    )

    simulation = build_test_simulation(
        model,
        number_of_paths=100
    )

    expected_alpha = np.tile(
        model.sabr_parameters.alpha0,
        (
            simulation.get_number_of_paths(),
            simulation.get_number_of_times(),
            1
        )
    )

    assert np.allclose(
        simulation.alpha_paths,
        expected_alpha,
        atol=1.0e-14
    )


# ============================================================
# 10. Discount-factor reconstruction tests
# ============================================================

def test_reconstructed_bonds_start_at_one():
    """
    At the valuation tenor date:

        P(T_k, T_k) = 1.
    """

    model = build_test_model()

    start_index = 2

    bonds = bond_prices_from_forwards(
        model.initial_forwards,
        model.tenor,
        start_index
    )

    assert abs(
        bonds[start_index]
        -
        1.0
    ) < 1.0e-14


def test_reconstructed_bonds_are_positive():
    """
    All reconstructed future discount factors should be positive.
    """

    model = build_test_model()

    start_index = 2

    bonds = bond_prices_from_forwards(
        model.initial_forwards,
        model.tenor,
        start_index
    )

    future_bonds = bonds[
        start_index:
    ]

    assert np.all(
        future_bonds > 0.0
    )


def test_model_and_pricing_bond_reconstruction_match():
    """
    Bond reconstruction in the model and pricing module
    should produce equal results.
    """

    model = build_test_model()

    start_index = 2

    model_bonds = (
        model.discount_factors_from_forwards(
            model.initial_forwards,
            start_index
        )
    )

    pricing_bonds = (
        bond_prices_from_forwards(
            model.initial_forwards,
            model.tenor,
            start_index
        )
    )

    assert np.allclose(
        model_bonds[
            start_index:
        ],
        pricing_bonds[
            start_index:
        ]
    )


# ============================================================
# 11. Swap-state tests
# ============================================================

def test_swap_annuity_is_positive():
    """
    The swap annuity must be positive.
    """

    model = build_test_model()

    annuity, swap_rate = (
        swap_annuity_and_rate(
            forwards=model.initial_forwards,
            tenor=model.tenor,
            swap_start_index=2,
            swap_end_index=8
        )
    )

    assert annuity > 0.0


def test_swap_rate_is_finite():
    """
    The par swap rate must be finite.
    """

    model = build_test_model()

    annuity, swap_rate = (
        swap_annuity_and_rate(
            forwards=model.initial_forwards,
            tenor=model.tenor,
            swap_start_index=2,
            swap_end_index=8
        )
    )

    assert np.isfinite(
        swap_rate
    )


# ============================================================
# 12. Pricing tests
# ============================================================

def test_caplet_price_is_non_negative():
    """
    A caplet price cannot be negative.
    """

    model = build_test_model()

    simulation = build_test_simulation(
        model,
        number_of_paths=400
    )

    result = price_caplet_mc(
        model=model,
        simulation=simulation,
        reset_time=1.0,
        strike=0.045,
        notional=1_000_000.0
    )

    assert result[
        "price"
    ] >= 0.0

    assert result[
        "standard_error"
    ] >= 0.0


def test_swaption_price_is_non_negative():
    """
    A European payer swaption price cannot be negative.
    """

    model = build_test_model()

    simulation = build_test_simulation(
        model,
        number_of_paths=400
    )

    result = price_payer_swaption_mc(
        model=model,
        simulation=simulation,
        expiry=1.0,
        swap_end=4.0,
        strike=0.045,
        notional=1_000_000.0
    )

    assert result[
        "price"
    ] >= 0.0

    assert result[
        "standard_error"
    ] >= 0.0


def test_caplet_price_decreases_with_strike():
    """
    A payer caplet should become less valuable
    when its strike increases.
    """

    model = build_test_model()

    simulation = build_test_simulation(
        model,
        number_of_paths=600
    )

    low_strike_result = price_caplet_mc(
        model=model,
        simulation=simulation,
        reset_time=1.0,
        strike=0.035,
        notional=1_000_000.0
    )

    high_strike_result = price_caplet_mc(
        model=model,
        simulation=simulation,
        reset_time=1.0,
        strike=0.055,
        notional=1_000_000.0
    )

    assert (
        low_strike_result[
            "price"
        ]
        >=
        high_strike_result[
            "price"
        ]
    )


def test_swaption_price_decreases_with_strike():
    """
    A payer swaption should become less valuable
    when its strike increases.
    """

    model = build_test_model()

    simulation = build_test_simulation(
        model,
        number_of_paths=600
    )

    low_strike_result = (
        price_payer_swaption_mc(
            model=model,
            simulation=simulation,
            expiry=1.0,
            swap_end=4.0,
            strike=0.035,
            notional=1_000_000.0
        )
    )

    high_strike_result = (
        price_payer_swaption_mc(
            model=model,
            simulation=simulation,
            expiry=1.0,
            swap_end=4.0,
            strike=0.055,
            notional=1_000_000.0
        )
    )

    assert (
        low_strike_result[
            "price"
        ]
        >=
        high_strike_result[
            "price"
        ]
    )


def test_zero_notional_produces_zero_caplet_price():
    """
    Zero notional should produce zero caplet value.
    """

    model = build_test_model()

    simulation = build_test_simulation(
        model,
        number_of_paths=100
    )

    result = price_caplet_mc(
        model=model,
        simulation=simulation,
        reset_time=1.0,
        strike=0.045,
        notional=0.0
    )

    assert abs(
        result[
            "price"
        ]
    ) < 1.0e-14


def test_zero_notional_produces_zero_swaption_price():
    """
    Zero notional should produce zero swaption value.
    """

    model = build_test_model()

    simulation = build_test_simulation(
        model,
        number_of_paths=100
    )

    result = price_payer_swaption_mc(
        model=model,
        simulation=simulation,
        expiry=1.0,
        swap_end=4.0,
        strike=0.045,
        notional=0.0
    )

    assert abs(
        result[
            "price"
        ]
    ) < 1.0e-14