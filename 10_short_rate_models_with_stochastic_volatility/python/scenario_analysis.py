"""
scenario_analysis.py

Scenario analysis utilities for Chapter 10.

This module studies how stochastic-volatility parameters affect:

- short-rate distributions
- volatility distributions
- zero-coupon bond prices
- bond option prices

This is more appropriate for Chapter 10 because the chapter's main
objective is to understand the impact of stochastic volatility.
"""

import numpy as np
import pandas as pd

from stochastic_vol_model import (
    StochasticVolShortRateModel
)

from stochastic_vol_simulation import (
    simulate_stochastic_vol_paths
)

from pricing import (
    monte_carlo_zero_coupon_bond_price,
    monte_carlo_bond_option_price
)


def run_single_scenario(
    base_hw_model,
    r0,
    kappa,
    v_bar,
    eta,
    rho,
    maturity,
    n_steps,
    n_paths,
    bond_maturity,
    option_expiry,
    option_bond_maturity,
    option_strike,
    seed=42
):
    """
    Run one stochastic-volatility scenario.

    Parameters
    ----------
    base_hw_model : HullWhiteModel
        Chapter 09 Hull-White model.

    r0 : float
        Initial short rate.

    kappa : float
        Variance mean reversion speed.

    v_bar : float
        Long-run variance.

    eta : float
        Volatility of variance.

    rho : float
        Correlation between short-rate and variance shocks.

    maturity : float
        Monte Carlo simulation horizon.

    n_steps : int
        Number of simulation time steps.

    n_paths : int
        Number of Monte Carlo paths.

    bond_maturity : float
        Maturity of the zero-coupon bond to price.

    option_expiry : float
        Bond option expiry.

    option_bond_maturity : float
        Maturity of the bond underlying the option.

    option_strike : float
        Bond option strike.

    seed : int
        Random seed.

    Returns
    -------
    dict
        Scenario summary results.
    """

    model = StochasticVolShortRateModel(
        base_hw_model=base_hw_model,
        kappa=kappa,
        v_bar=v_bar,
        eta=eta,
        rho=rho
    )

    times, rate_paths, variance_paths = simulate_stochastic_vol_paths(
        model=model,
        r0=r0,
        v0=v_bar,
        maturity=maturity,
        n_steps=n_steps,
        n_paths=n_paths,
        seed=seed
    )

    bond_price = monte_carlo_zero_coupon_bond_price(
        times=times,
        rate_paths=rate_paths,
        maturity=bond_maturity
    )

    option_price = monte_carlo_bond_option_price(
        times=times,
        rate_paths=rate_paths,
        option_expiry=option_expiry,
        bond_maturity=option_bond_maturity,
        strike=option_strike,
        option_type="call"
    )

    final_rates = rate_paths[:, -1]

    final_variances = variance_paths[:, -1]

    final_vols = np.sqrt(
        final_variances
    )

    return {
        "kappa": kappa,
        "v_bar": v_bar,
        "eta": eta,
        "rho": rho,
        "bond_price": bond_price,
        "bond_option_price": option_price,
        "terminal_rate_mean": final_rates.mean(),
        "terminal_rate_std": final_rates.std(),
        "terminal_rate_5pct": np.percentile(final_rates, 5),
        "terminal_rate_95pct": np.percentile(final_rates, 95),
        "terminal_vol_mean": final_vols.mean(),
        "terminal_vol_std": final_vols.std()
    }


def run_eta_scenarios(
    base_hw_model,
    r0,
    eta_values,
    kappa=1.0,
    v_bar=0.0001,
    rho=-0.30,
    maturity=10.0,
    n_steps=240,
    n_paths=5000,
    bond_maturity=5.0,
    option_expiry=2.0,
    option_bond_maturity=5.0,
    option_strike=0.90,
    seed=42
):
    """
    Run scenarios across different eta values.

    eta controls volatility-of-volatility.

    Higher eta means volatility itself becomes more unstable.
    """

    rows = []

    for eta in eta_values:

        result = run_single_scenario(
            base_hw_model=base_hw_model,
            r0=r0,
            kappa=kappa,
            v_bar=v_bar,
            eta=eta,
            rho=rho,
            maturity=maturity,
            n_steps=n_steps,
            n_paths=n_paths,
            bond_maturity=bond_maturity,
            option_expiry=option_expiry,
            option_bond_maturity=option_bond_maturity,
            option_strike=option_strike,
            seed=seed
        )

        rows.append(result)

    return pd.DataFrame(rows)


def run_rho_scenarios(
    base_hw_model,
    r0,
    rho_values,
    kappa=1.0,
    v_bar=0.0001,
    eta=0.20,
    maturity=10.0,
    n_steps=240,
    n_paths=5000,
    bond_maturity=5.0,
    option_expiry=2.0,
    option_bond_maturity=5.0,
    option_strike=0.90,
    seed=42
):
    """
    Run scenarios across different rho values.

    rho controls correlation between rate shocks and volatility shocks.
    """

    rows = []

    for rho in rho_values:

        result = run_single_scenario(
            base_hw_model=base_hw_model,
            r0=r0,
            kappa=kappa,
            v_bar=v_bar,
            eta=eta,
            rho=rho,
            maturity=maturity,
            n_steps=n_steps,
            n_paths=n_paths,
            bond_maturity=bond_maturity,
            option_expiry=option_expiry,
            option_bond_maturity=option_bond_maturity,
            option_strike=option_strike,
            seed=seed
        )

        rows.append(result)

    return pd.DataFrame(rows)


def run_kappa_scenarios(
    base_hw_model,
    r0,
    kappa_values,
    v_bar=0.0001,
    eta=0.20,
    rho=-0.30,
    maturity=10.0,
    n_steps=240,
    n_paths=5000,
    bond_maturity=5.0,
    option_expiry=2.0,
    option_bond_maturity=5.0,
    option_strike=0.90,
    seed=42
):
    """
    Run scenarios across different kappa values.

    kappa controls how quickly volatility mean-reverts.
    """

    rows = []

    for kappa in kappa_values:

        result = run_single_scenario(
            base_hw_model=base_hw_model,
            r0=r0,
            kappa=kappa,
            v_bar=v_bar,
            eta=eta,
            rho=rho,
            maturity=maturity,
            n_steps=n_steps,
            n_paths=n_paths,
            bond_maturity=bond_maturity,
            option_expiry=option_expiry,
            option_bond_maturity=option_bond_maturity,
            option_strike=option_strike,
            seed=seed
        )

        rows.append(result)

    return pd.DataFrame(rows)


def plot_scenario_metric(
    scenario_df,
    x_col,
    y_col,
    title,
    ylabel
):
    """
    Generic scenario plot.

    Parameters
    ----------
    scenario_df : pandas.DataFrame
        Scenario result table.

    x_col : str
        Column used on x-axis.

    y_col : str
        Column used on y-axis.

    title : str
        Plot title.

    ylabel : str
        Y-axis label.
    """

    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))

    plt.plot(
        scenario_df[x_col],
        scenario_df[y_col],
        marker="o"
    )

    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(ylabel)
    plt.grid()
    plt.show()


def plot_eta_scenario_summary(
    eta_df
):
    """
    Plot key metrics from eta scenario analysis.
    """

    plot_scenario_metric(
        eta_df,
        "eta",
        "bond_option_price",
        "Bond Option Price vs Vol-of-Vol",
        "Bond Option Price"
    )

    plot_scenario_metric(
        eta_df,
        "eta",
        "terminal_rate_std",
        "Terminal Rate Dispersion vs Vol-of-Vol",
        "Terminal Rate Std"
    )

    plot_scenario_metric(
        eta_df,
        "eta",
        "terminal_vol_mean",
        "Terminal Volatility vs Vol-of-Vol",
        "Terminal Vol Mean"
    )


def plot_rho_scenario_summary(
    rho_df
):
    """
    Plot key metrics from rho scenario analysis.
    """

    plot_scenario_metric(
        rho_df,
        "rho",
        "bond_option_price",
        "Bond Option Price vs Rate-Vol Correlation",
        "Bond Option Price"
    )

    plot_scenario_metric(
        rho_df,
        "rho",
        "terminal_rate_5pct",
        "Lower-Tail Rate Outcome vs Rate-Vol Correlation",
        "Terminal Rate 5th Percentile"
    )

    plot_scenario_metric(
        rho_df,
        "rho",
        "terminal_rate_95pct",
        "Upper-Tail Rate Outcome vs Rate-Vol Correlation",
        "Terminal Rate 95th Percentile"
    )


def plot_kappa_scenario_summary(
    kappa_df
):
    """
    Plot key metrics from kappa scenario analysis.
    """

    plot_scenario_metric(
        kappa_df,
        "kappa",
        "bond_option_price",
        "Bond Option Price vs Variance Mean Reversion",
        "Bond Option Price"
    )

    plot_scenario_metric(
        kappa_df,
        "kappa",
        "terminal_vol_std",
        "Terminal Volatility Dispersion vs Variance Mean Reversion",
        "Terminal Vol Std"
    )