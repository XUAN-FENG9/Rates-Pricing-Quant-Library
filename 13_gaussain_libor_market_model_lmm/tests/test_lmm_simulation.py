# ✝ In memory of my beloved grandfather - Heshun Feng (冯和顺), who passed away today (11th July 2026)
# His love and encouragement will forever inspire me.


import sys

sys.path.append("../python")


from market_data import load_curve_data
from tenor_structure import TenorStructure

from correlation import (
    exponential_correlation_matrix,
    principal_component_loadings
)

from volatility import (
    GaussianLMMVolatility
)

from gaussian_lmm import (
    GaussianLMM
)

from simulation import (
    simulate_gaussian_lmm
)


def test_simulation_shape():

    curve = load_curve_data(
        "../data/usd_zero_curve.csv"
    )

    tenor = TenorStructure(
        start=0.0,
        end=10.0,
        payment_frequency=2
    )

    forwards = tenor.initial_forward_rates(
        curve
    )

    correlation = exponential_correlation_matrix(
        tenor.times[:-1],
        beta=0.10
    )

    loadings = principal_component_loadings(
        correlation,
        n_factors=3
    )

    vol_model = GaussianLMMVolatility(
        tenor.times[:-1],
        sigma_level=0.01,
        decay=0.05
    )

    model = GaussianLMM(
        tenor_structure=tenor,
        initial_forwards=forwards,
        volatility_model=vol_model,
        correlation_loadings=loadings,
        initial_discount_factors=tenor.initial_discount_factors(
            curve
        )
    )

    times, paths = simulate_gaussian_lmm(
        model=model,
        simulation_end=5.0,
        n_steps=100,
        n_paths=200,
        seed=42
    )

    assert paths.shape == (
        200,
        101,
        20
    )