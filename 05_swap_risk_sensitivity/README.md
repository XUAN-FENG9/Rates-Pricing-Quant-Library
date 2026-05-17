# Chapter 05 — Swap Risk Sensitivity

# 5.1 Overview

This chapter introduces:

- DV01

- PV01

- key rate risk

- curve shocks

- steepener trades

- flattener trades

- scenario analysis



This chapter moves from:

> pricing
to:
> risk management and trading analytics.

---

# 5.2 Why Risk Matters

Interest rate swaps are highly sensitive to:

- level shifts

- steepening

- flattening

- forward curve changes


Rates desks continuously monitor:

- DV01

- key rate duration

- bucketed risk

- hedge ratios

---

# 5.3 DV01



DV01 measures:

> the dollar change in instrument value

> for a 1bp parallel move in rates.

Formula:

$$
DV01 = PV(r+1bp)-PV(r)
$$

---


# 5.4 PV01

PV01 is the absolute magnitude of DV01.

$$
PV01 = |DV01|
$$

---



# 5.5 Key Rate Risk

Key rate DV01 measures sensitivity to:

- specific maturities

- curve buckets

Example:

- 2Y sensitivity

- 5Y sensitivity

- 10Y sensitivity

---



# 5.6 Curve Scenarios

We implement:

## Steepener

Long-end rates rise more than short-end.

Typical macro interpretation:

- inflation fears

- higher term premium


## Flattener

Short-end rates rise more than long-end.

Typical macro interpretation:

- central bank tightening

- recession fears


---

# 5.6 Project Structure

```text

05_swap_risk_sensitivity/
│
├── python/
│   ├── curve.py
│   ├── swap.py
│   ├── risk.py
│   ├── key_rate_risk.py
│   ├── scenario_analysis.py
│   ├── market_data.py
│   └── plotting.py
│
├── cpp/
│   ├── curve.hpp
│   ├── curve.cpp
│   ├── swap.hpp
│   ├── swap.cpp
│   ├── risk.hpp
│   ├── risk.cpp
│   └── main.cpp
│
├── notebooks/
│   └── 05_swap_risk_sensitivity.ipynb
│
├── data/
│   └── usd_zero_curve.csv
│
├── tests/
│   └── test_risk.py
│
└── README.md

```

---

# 5.7 Key Quantitative Concepts

This chapter introduces:

- bump-and-reprice

- sensitivity analysis

- scenario stress testing

- curve risk decomposition

These concepts are foundational for:

- XVA

- VaR

- Monte Carlo risk

- balance sheet management

- trading analytics

---


# 5.9 Python vs C++

## Python

Used for:

- prototyping

- research

- analytics

- visualization

---


## C++



Used for:

- production risk engines

- overnight risk runs

- low-latency pricing

- large-scale portfolio analytics


---



# 5.10 From Next Chapter

Chapter 06 introduces:

# Black Swaption Pricing

We will build:

- Black's model

- swaption pricing

- implied volatility

- Greeks

- volatility smiles


This moves us from:

> linear rates products

to:

> nonlinear volatility derivatives.

