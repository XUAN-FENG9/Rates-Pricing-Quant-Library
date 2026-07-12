# ✝ In memory of my beloved grandfather - Heshun Feng (冯和顺), who passed away today (11th July 2026)
# His love and encouragement will forever inspire me.


"""
pricing.py

Monte Carlo pricing under the Gaussian LMM terminal measure.

The terminal discount bond P(0,T_N) is used as numeraire.

For a payoff V(T) at time T:

    V(0)
    =
    P(0,T_N)
    E^{T_N}
    [
        V(T) / P(T,T_N)
    ]
"""

import numpy as np

from simulation import (
    nearest_simulation_index
)


def bond_prices_from_forwards(
    forward_rates,
    tenor_structure,
    start_forward_index
):
    """
    Compute tenor-date discount bonds from a forward-rate state.

    At time T_k:

        P(T_k,T_j)
        =
        product_{m=k}^{j-1}
        1 / (1 + delta_m L_m)

    Parameters
    ----------
    forward_rates : np.ndarray
        Forward-rate vector at the valuation time.

    tenor_structure : TenorStructure
        Tenor grid.

    start_forward_index : int
        Index k corresponding to current tenor date T_k.

    Returns
    -------
    np.ndarray
        Bond prices:

            [P(T_k,T_k), ..., P(T_k,T_N)]
    """

    n_times = len(
        tenor_structure.times
    )

    bonds = np.ones(
        n_times
    )

    running = 1.0

    for j in range(
        start_forward_index,
        tenor_structure.n_forwards
    ):

        denominator = (
            1.0
            +
            tenor_structure.accruals[j]
            *
            forward_rates[j]
        )

        if denominator <= 0.0:
            raise ValueError(
                "Invalid forward state: "
                "1 + delta * L must remain positive."
            )

        running /= denominator

        bonds[j + 1] = running

    return bonds


def swap_annuity_and_rate(
    forward_rates,
    tenor_structure,
    swap_start_index,
    swap_end_index
):
    """
    Compute swap annuity and par swap rate.

    Swap starts at T_k and ends at T_m.

    Annuity:

        A(T_k)
        =
        sum_{j=k}^{m-1}
        delta_j P(T_k,T_{j+1})

    Swap rate:

        S(T_k)
        =
        [1 - P(T_k,T_m)] / A(T_k)
    """

    if swap_end_index <= swap_start_index:
        raise ValueError(
            "swap_end_index must exceed swap_start_index."
        )

    bonds = bond_prices_from_forwards(
        forward_rates,
        tenor_structure,
        swap_start_index
    )

    annuity = 0.0

    for j in range(
        swap_start_index,
        swap_end_index
    ):

        annuity += (
            tenor_structure.accruals[j]
            *
            bonds[j + 1]
        )

    if annuity <= 0.0:
        return 0.0, 0.0

    swap_rate = (
        1.0
        -
        bonds[swap_end_index]
    ) / annuity

    return annuity, swap_rate


def price_payer_swaption_mc(
    model,
    times,
    forward_paths,
    expiry,
    swap_end,
    strike,
    notional=1_000_000
):
    """
    Price a physically settled payer swaption under terminal measure.

    Payoff at expiry T_k:

        N A(T_k) max(S(T_k)-K, 0)

    Terminal-measure valuation:

        V(0)
        =
        P(0,T_N)
        E^{T_N}
        [
            payoff / P(T_k,T_N)
        ]
    """

    tenor = model.tenor

    expiry_index = tenor.time_index(
        expiry
    )

    swap_end_index = tenor.time_index(
        swap_end
    )

    simulation_index = nearest_simulation_index(
        times,
        expiry
    )

    terminal_df = model.initial_discount_factors[
        -1
    ] if hasattr(
        model,
        "initial_discount_factors"
    ) else None

    if terminal_df is None:
        raise ValueError(
            "Model must contain initial_discount_factors."
        )

    discounted_numeraire_payoffs = []

    for path in range(
        forward_paths.shape[0]
    ):

        forwards = forward_paths[
            path,
            simulation_index,
            :
        ]

        annuity, swap_rate = swap_annuity_and_rate(
            forwards,
            tenor,
            expiry_index,
            swap_end_index
        )

        payoff = (
            notional
            *
            annuity
            *
            max(
                swap_rate
                -
                strike,
                0.0
            )
        )

        bonds = bond_prices_from_forwards(
            forwards,
            tenor,
            expiry_index
        )

        terminal_bond = bonds[-1]

        discounted_numeraire_payoffs.append(
            payoff
            /
            terminal_bond
        )

    return (
        terminal_df
        *
        float(
            np.mean(
                discounted_numeraire_payoffs
            )
        )
    )


def price_caplet_mc(
    model,
    times,
    forward_paths,
    reset_time,
    strike,
    notional=1_000_000
):
    """
    Price a caplet using terminal-measure Monte Carlo.

    The caplet pays at T_{i+1}:

        N delta_i max(L_i(T_i)-K, 0)

    Its value at reset T_i is:

        N delta_i max(L_i-K,0)
        /
        [1 + delta_i L_i]

    This reset-time value is then converted using the terminal numeraire.
    """

    tenor = model.tenor

    forward_index = tenor.forward_index(
        reset_time
    )

    simulation_index = nearest_simulation_index(
        times,
        reset_time
    )

    terminal_df = model.initial_discount_factors[
        -1
    ]

    adjusted_payoffs = []

    for path in range(
        forward_paths.shape[0]
    ):

        forwards = forward_paths[
            path,
            simulation_index,
            :
        ]

        forward = forwards[
            forward_index
        ]

        delta = tenor.accruals[
            forward_index
        ]

        reset_value = (
            notional
            *
            delta
            *
            max(
                forward
                -
                strike,
                0.0
            )
            /
            (
                1.0
                +
                delta
                *
                forward
            )
        )

        bonds = bond_prices_from_forwards(
            forwards,
            tenor,
            forward_index
        )

        terminal_bond = bonds[
            -1
        ]

        adjusted_payoffs.append(
            reset_value
            /
            terminal_bond
        )

    return (
        terminal_df
        *
        float(
            np.mean(
                adjusted_payoffs
            )
        )
    )