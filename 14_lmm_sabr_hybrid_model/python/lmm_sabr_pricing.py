"""
lmm_sabr_pricing.py

Terminal-measure Monte Carlo pricing for the LMM-SABR hybrid.

The pricing formula is:

    V(0)
        =
        P(0, T_N)
        E under Q^{T_N}
        [
            V(T) / P(T, T_N)
        ]

The module prices:

    caplets
    European payer swaptions
"""

import numpy as np

from sabr_simulation import exact_time_index


def bond_prices_from_forwards(
    forwards,
    tenor,
    start_forward_index
):
    """
    Reconstruct discount bonds from forward rates.
    """

    forwards = np.asarray(
        forwards,
        dtype=float
    )

    accruals = np.asarray(
        tenor.accruals,
        dtype=float
    )

    number_of_forwards = len(
        forwards
    )

    if len(accruals) != number_of_forwards:

        raise ValueError(
            "Tenor and forward dimensions are inconsistent."
        )

    if (
        start_forward_index < 0
        or
        start_forward_index > number_of_forwards
    ):

        raise ValueError(
            "start_forward_index is invalid."
        )

    bonds = np.full(
        number_of_forwards + 1,
        np.nan
    )

    bonds[start_forward_index] = 1.0

    running_bond = 1.0

    for j in range(
        start_forward_index,
        number_of_forwards
    ):

        denominator = (
            1.0
            +
            accruals[j]
            *
            forwards[j]
        )

        if denominator <= 0.0:

            raise RuntimeError(
                "Invalid forward state "
                "in bond reconstruction."
            )

        running_bond /= denominator

        bonds[j + 1] = running_bond

    return bonds


def swap_annuity_and_rate(
    forwards,
    tenor,
    swap_start_index,
    swap_end_index
):
    """
    Calculate the swap annuity and par swap rate.
    """

    if swap_end_index <= swap_start_index:

        raise ValueError(
            "swap_end_index must exceed "
            "swap_start_index."
        )

    bonds = bond_prices_from_forwards(
        forwards,
        tenor,
        swap_start_index
    )

    accruals = np.asarray(
        tenor.accruals,
        dtype=float
    )

    annuity = 0.0

    for j in range(
        swap_start_index,
        swap_end_index
    ):

        annuity += (
            accruals[j]
            *
            bonds[j + 1]
        )

    if annuity <= 0.0:

        raise RuntimeError(
            "Swap annuity must be positive."
        )

    swap_rate = (
        1.0
        -
        bonds[swap_end_index]
    ) / annuity

    return (
        float(
            annuity
        ),
        float(
            swap_rate
        )
    )


def price_caplet_mc(
    model,
    simulation,
    reset_time,
    strike,
    notional=1_000_000.0
):
    """
    Price a caplet using terminal-measure Monte Carlo.
    """

    forward_index = model.tenor.time_index(
        reset_time
    )

    if forward_index >= model.number_of_forwards:

        raise ValueError(
            "reset_time does not correspond "
            "to a forward reset."
        )

    simulation_index = exact_time_index(
        simulation.times,
        reset_time
    )

    accrual = model.get_accruals()[
        forward_index
    ]

    path_forwards = (
        simulation.forward_paths[
            :,
            simulation_index,
            :
        ]
    )

    fixing_forwards = (
        path_forwards[
            :,
            forward_index
        ]
    )

    payment_payoffs = (
        notional
        *
        accrual
        *
        np.maximum(
            fixing_forwards
            -
            strike,
            0.0
        )
    )

    reset_date_values = (
        payment_payoffs
        /
        (
            1.0
            +
            accrual
            *
            fixing_forwards
        )
    )

    number_of_paths = (
        simulation.get_number_of_paths()
    )

    numeraire_values = np.empty(
        number_of_paths
    )

    for path_index in range(
        number_of_paths
    ):

        terminal_bond = (
            model.terminal_bond_from_forwards(
                path_forwards[
                    path_index
                ],
                forward_index
            )
        )

        numeraire_values[
            path_index
        ] = (
            reset_date_values[
                path_index
            ]
            /
            terminal_bond
        )

    initial_terminal_bond = (
        model.initial_terminal_discount_factor()
    )

    price = (
        initial_terminal_bond
        *
        np.mean(
            numeraire_values
        )
    )

    standard_error = (
        initial_terminal_bond
        *
        np.std(
            numeraire_values,
            ddof=1
        )
        /
        np.sqrt(
            number_of_paths
        )
    )

    return {
        "price":
            float(
                price
            ),

        "standard_error":
            float(
                standard_error
            )
    }


def price_payer_swaption_mc(
    model,
    simulation,
    expiry,
    swap_end,
    strike,
    notional=1_000_000.0
):
    """
    Price a European payer swaption.
    """

    expiry_index = model.tenor.time_index(
        expiry
    )

    swap_end_index = model.tenor.time_index(
        swap_end
    )

    if swap_end_index <= expiry_index:

        raise ValueError(
            "swap_end must be after expiry."
        )

    simulation_index = exact_time_index(
        simulation.times,
        expiry
    )

    path_forwards = (
        simulation.forward_paths[
            :,
            simulation_index,
            :
        ]
    )

    number_of_paths = (
        simulation.get_number_of_paths()
    )

    numeraire_values = np.empty(
        number_of_paths
    )

    swap_rates = np.empty(
        number_of_paths
    )

    annuities = np.empty(
        number_of_paths
    )

    for path_index in range(
        number_of_paths
    ):

        annuity, swap_rate = (
            swap_annuity_and_rate(
                path_forwards[
                    path_index
                ],
                model.tenor,
                expiry_index,
                swap_end_index
            )
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

        terminal_bond = (
            model.terminal_bond_from_forwards(
                path_forwards[
                    path_index
                ],
                expiry_index
            )
        )

        numeraire_values[
            path_index
        ] = (
            payoff
            /
            terminal_bond
        )

        swap_rates[
            path_index
        ] = swap_rate

        annuities[
            path_index
        ] = annuity

    initial_terminal_bond = (
        model.initial_terminal_discount_factor()
    )

    price = (
        initial_terminal_bond
        *
        np.mean(
            numeraire_values
        )
    )

    standard_error = (
        initial_terminal_bond
        *
        np.std(
            numeraire_values,
            ddof=1
        )
        /
        np.sqrt(
            number_of_paths
        )
    )

    return {
        "price":
            float(
                price
            ),

        "standard_error":
            float(
                standard_error
            ),

        "mean_expiry_swap_rate":
            float(
                np.mean(
                    swap_rates
                )
            ),

        "mean_expiry_annuity":
            float(
                np.mean(
                    annuities
                )
            )
    }