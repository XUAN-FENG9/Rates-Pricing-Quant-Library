# Chapter 10 — Short Rate Models with Stochastic Volatility

# 10.1 Introduction
## Overview

This chapter extends the one-factor Hull-White model by allowing the volatility of the short rate itself to evolve randomly through time.

Chapter 09 assumed:

$$
dr_t =
\left(
\theta(t)-ar_t
\right)dt
+
\sigma dW_t
$$

where the volatility parameter \(\sigma\) is constant.

Although this assumption leads to analytical pricing formulas, empirical evidence suggests that interest-rate volatility is itself stochastic.

This chapter therefore replaces the constant volatility with a stochastic variance process, producing a more realistic description of future interest-rate dynamics.

The chapter implements:

- Hull-White model with stochastic volatility
- CIR-type variance dynamics
- Correlated Monte Carlo simulation
- Zero-coupon bond pricing
- Bond option pricing
- Scenario analysis for stochastic-volatility parameters
- Python and C++ implementations

---

# 10.2 Project Structure

```text
10_short_rate_models_with_stochastic_volatility/
│
├── python/
│   ├── stochastic_vol_model.py
│   ├── stochastic_vol_simulation.py
│   ├── pricing.py
│   ├── scenario_analysis.py
│   ├── plotting.py
│   └── diagnostics.py
│
├── cpp/
│   ├── StochasticVolModel.hpp
│   ├── StochasticVolModel.cpp
│   ├── StochasticVolSimulation.hpp
│   ├── StochasticVolSimulation.cpp
│   ├── StochasticVolPricing.hpp
│   ├── StochasticVolPricing.cpp
│   ├── ScenarioAnalysis.hpp
│   ├── ScenarioAnalysis.cpp
│   └── main.cpp
│
├── tests/
│   ├── test_stochastic_vol_model.py
│   ├── test_simulation.py
│   └── test_pricing.py
│
├── notebooks/
│   └── 10_short_rate_models_with_stochastic_volatility.ipynb
│
└── README.md
```

## Relationship to Previous Chapters

This chapter directly extends Chapter 09.

```text
Yield Curve
        ↓
Hull-White Short Rate Model
        ↓
Stochastic Volatility Extension
```

The following components are reused without modification:

- YieldCurve
- Market data loader
- Hull-White theta(t)
- Initial curve fitting

Only the volatility specification changes.

---

# 10.3 Model Dynamics

The short rate evolves according to

$$
dr_t =
\left(
\theta(t)-ar_t
\right)dt
+
\sqrt{v_t}\,dW_t^r
$$

where the variance process follows

$$
dv_t =
\kappa
\left(
v_\infty-v_t
\right)dt
+
\eta
\sqrt{v_t}
\,dW_t^v.
$$

The Brownian motions satisfy

$$
dW_t^r
\,dW_t^v =
\rho\,dt.
$$


## Model Parameters

| Parameter | Interpretation |
|------------|----------------|
| \(a\) | Short-rate mean reversion |
| \(\theta(t)\) | Drift fitted to today's yield curve |
| \(v_t\) | Instantaneous variance |
| \(\kappa\) | Variance mean-reversion speed |
| \(v_\infty\) | Long-run variance |
| \(\eta\) | Volatility of variance (vol-of-vol) |
| \(\rho\) | Correlation between rate and variance shocks |

---

# 10.4 Why Introduce Stochastic Volatility?

The Hull-White model assumes

$$
\sigma =
constant.
$$

In practice,

- volatility clusters through time,
- large market shocks are followed by elevated volatility,
- option prices depend on future volatility uncertainty.

Introducing stochastic volatility captures these important market features.

---

# 10.5 Simulation Scheme

The short rate is simulated using an Euler discretization:

$$
r_{t+\Delta t} =
r_t
+
\left(
\theta(t)-ar_t
\right)\Delta t
+
\sqrt{v_t}
\sqrt{\Delta t}
Z_r.
$$

The variance follows

$$
v_{t+\Delta t} =
v_t
+
\kappa
(v_\infty-v_t)\Delta t
+
\eta
\sqrt{v_t}
\sqrt{\Delta t}
Z_v.
$$

The correlated shocks satisfy

$$
Z_v =
\rho Z_r
+
\sqrt{1-\rho^2}
Z_\perp.
$$

To guarantee positivity, the implementation uses full truncation:

$$
v_t =
\max(v_t,0).
$$

---

# 10.6 Monte Carlo Pricing

Because stochastic volatility destroys most analytical pricing formulas, derivatives are priced by Monte Carlo simulation.

For each simulated path,

$$
D(0,T) =
\exp
\left( -
\int_0^T r_tdt
\right)
$$

is computed numerically.

The zero-coupon bond price is

$$
P(0,T) =
E[D(0,T)].
$$

---

# 10.7 Bond Option Pricing

A European call option on a zero-coupon bond has payoff

$$
\max
\left(
P(\tau,T)-K,
0
\right).
$$

The pricing workflow is

```text
Simulate Short Rates
        ↓
Compute Pathwise Discount Factors
        ↓
Compute Bond Price at Option Expiry
        ↓
Evaluate Payoff
        ↓
Discount Back
        ↓
Average Across Paths
```

Unlike Chapter 09, no analytical pricing formula is used.

---

# 10.8 Scenario Analysis

Rather than calibrating the model to synthetic market prices, this chapter investigates how stochastic-volatility parameters affect pricing and risk.

Three scenario studies are included.

## Volatility of Volatility

Different values of

$$
\eta
$$

are tested to study how volatility uncertainty affects bond prices and bond option values.

## Rate–Volatility Correlation

Different values of

$$
\rho
$$

show how the interaction between interest-rate movements and volatility shocks changes derivative prices.


## Variance Mean Reversion

Different values of

$$
\kappa
$$

illustrate how quickly volatility returns toward its long-run level.

---
# 10.9 Implementation
## Python Implementation

The Python implementation includes

- stochastic-volatility model
- Monte Carlo simulation
- zero-coupon bond pricing
- bond option pricing
- scenario analysis
- visualization tools
- diagnostics

Python is primarily intended for

- research
- experimentation
- visualization
- validation

## C++ Implementation

The C++ implementation mirrors the Python workflow while reusing components from Chapter 09.

It includes

- stochastic-volatility short-rate model
- Monte Carlo simulation
- zero-coupon bond pricing
- bond option pricing
- scenario analysis

The C++ version is intentionally lightweight and dependency-free, making it suitable for educational purposes and future extensions.

---

# 10.10 Constant Volatility vs Stochastic Volatility

| Feature | Hull-White | Stochastic-Vol Extension |
|----------|------------|--------------------------|
| Mean reversion | ✓ | ✓ |
| Curve fitting | ✓ | ✓ |
| Constant volatility | ✓ | ✗ |
| Volatility clustering | ✗ | ✓ |
| Closed-form bond option pricing | ✓ | ✗ |
| Monte Carlo required | Optional | Yes |

---
# 10.11 Summary
## Practical Applications

Stochastic-volatility short-rate models are useful for

- callable bond pricing
- Bermudan swaptions
- XVA exposure simulation
- stress testing
- scenario analysis
- interest-rate risk management

Although simplified, the implementation captures the key ideas used in more advanced production models.

## Key Lessons

1. Interest-rate volatility is itself stochastic.
2. Monte Carlo simulation becomes essential once volatility evolves randomly.
3. Volatility uncertainty affects both pricing and risk.
4. The parameters \(\eta\), \(\rho\), and \(\kappa\) each have distinct economic interpretations.
5. Scenario analysis is often more informative than calibration when studying stochastic-volatility models.


## Relationship to Other Models

This model can be viewed as a bridge between

- Hull-White
- CIR variance dynamics
- Heston stochastic volatility
- modern stochastic interest-rate models

Many production interest-rate models build upon these same ideas using additional factors or more sophisticated volatility specifications.


## Extension

Multi-factor short-rate models.

Instead of describing the entire yield curve using a single short-rate factor, multiple factors are introduced to capture:

- level movements
- slope changes
- curvature dynamics

These extensions provide a richer description of the term structure and improve the pricing of complex interest-rate derivatives.
