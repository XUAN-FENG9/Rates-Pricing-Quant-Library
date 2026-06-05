# Chapter 07 — Local Volatility and Dupire

# 7.1 Introduction

## Overview

This chapter introduces the construction of a local volatility surface for interest rate derivatives using Dupire's formula.

Starting from market swaption volatility quotes, we build:

```text
Market Swaption Quotes
        ↓
Implied Volatility Surface
        ↓
Swaption Price Surface
        ↓
Dupire Local Volatility Surface
        ↓
Off-Grid Volatility Interpolation
```

The implementation reuses the pricing infrastructure developed in previous chapters:

- Yield Curve Construction (Chapter 01)
- Forward Starting Swaps (Chapter 04)
- Black Swaption Pricing (Chapter 06)

The objective is to demonstrate how market option prices can be transformed into a state-dependent volatility model suitable for advanced pricing frameworks.

## Learning Objectives

By completing this chapter, readers should understand:

- the difference between implied volatility and local volatility
- how market swaption quotes are transformed into a volatility surface
- how Dupire's formula extracts local volatility
- why local volatility depends on both time and strike
- how interpolation is used for non-standard expiries and strikes
- why numerical stability is a major challenge in local volatility modelling

## Project Structure

```text
07_local_volatility_and_dupire/
│
├── python/
│   ├── market_data.py
│   ├── vol_surface.py
│   ├── swaption_price_surface.py
│   ├── dupire_builder.py
│   ├── local_vol_surface.py
│   └── plotting.py
│
├── cpp/
│   ├── VolSurface.hpp
│   ├── VolSurface.cpp
│   ├── SwaptionPriceSurface.hpp
│   ├── SwaptionPriceSurface.cpp
│   ├── DupireBuilder.hpp
│   ├── DupireBuilder.cpp
│   ├── LocalVolSurface.hpp
│   ├── LocalVolSurface.cpp
│   └── main.cpp
│
├── data/
│   ├── curve_data.csv
│   └── swaption_vol_surface.csv
│
├── tests/
│   ├── test_dupire_workflow.py
│   └── test_off_grid_local_vol_pricing.py
│
├── notebooks/
│   └── 07_local_volatility_and_dupire.ipynb
│
└── README.md
```

---

# 7.2 Implied Volatility Surface

The market provides swaption quotes as Black implied volatilities.

The implied volatility surface is represented as:

$$
\sigma_{imp}(T,K)
$$

where:

- \(T\) = option expiry
- \(K\) = strike

These volatilities are not model parameters.

Instead, they are market observations extracted from traded swaption prices.

---

# 7.3 Building the Option Price Surface

Dupire's formula requires option prices rather than implied volatilities.

Using the Chapter 06 Black swaption pricer, we convert:

$$
\sigma_{imp}(T,K)
$$

into:

$$
C(T,K)
$$

where:

$$
C(T,K)
$$

denotes the swaption price surface.

For each grid point:

1. Construct a forward-starting swap
2. Compute the forward swap rate
3. Obtain the implied volatility
4. Price the swaption using Black's model

---

# 7.4 Dupire Local Volatility

Dupire's formula converts the option price surface into a local volatility surface:

$$
\sigma_{loc}^{2}(T,K) =
\frac{
\frac{\partial C}{\partial T}
}{
\frac12 K^2
\frac{\partial^2 C}{\partial K^2}
}
$$

where:

- $$\frac{\partial C}{\partial T}$$ measures sensitivity to expiry
- $$\frac{\partial^2 C}{\partial K^2}$$ measures strike convexity

The resulting local volatility surface is:

$$
\sigma_{loc}(T,K)
$$

Unlike implied volatility, local volatility is a model quantity rather than a market quote.

---

# 7.5 From Calibration to Simulation

One of the most important concepts in local volatility modelling is understanding how a volatility surface calibrated in quote space becomes a volatility function used during simulation.

Calibration is performed in:

$$
(T,K)
$$

space.

The resulting local volatility surface is:

$$
\sigma_{loc}(T,K)
$$

However, during simulation the model evolves according to:

$$
dF_t =
\sigma_{loc}(t,F_t)
F_t
dW_t
$$

where:

- \(F_t\) is the forward swap rate
- \(t\) is simulation time

Consequently:

$$
\sigma_{loc}(T,K)
$$

and

$$
\sigma_{loc}(t,F_t)
$$

represent the same surface viewed from two different perspectives.

This observation explains why local volatility models can reproduce the market vanilla option surface exactly after calibration.

---

# 7.6 From Market Quotes to Stochastic Dynamics

One of the most important conceptual steps in local volatility modelling is understanding how a surface defined in market quote space becomes a volatility function used inside a stochastic process.

## Step 1: Market Quote Space

Market swaption quotes are observed as a function of:

$$
(T,K)
$$

where:

- \(T\) = option expiry
- \(K\) = strike

For example:

| Expiry | Strike | Market Black Vol |
|----------|----------|----------|
| 1Y | 4.0% | 1100bp |
| 5Y | 4.0% | 1500bp |
| 10Y | 4.0% | 1850bp |

These market observations define the implied volatility surface:

$$
\sigma_{imp}(T,K)
$$

Using Black's model, we convert the implied volatility surface into an option price surface:

$$
C(T,K)
$$

Dupire's formula then produces the local volatility surface:

$$
\sigma_{loc}(T,K)
$$

At this stage, the surface still lives entirely in quote space.

## Step 2: Local Volatility Model

The local volatility model assumes that the forward swap rate evolves according to:

$$
dF_t =
\sigma_{loc}(t,F_t)
\,F_t\,dW_t
$$

Unlike Black's model, volatility is no longer constant.

Instead, volatility depends on:

- current simulation time $t$
- current forward swap rate level $F_t$

## Step 3: Connecting the Two Views

At first sight, the two surfaces appear different:

Quote Space:

$$
\sigma_{loc}(T,K)
$$

Simulation Space:

$$
\sigma_{loc}(t,F_t)
$$

However, they are actually the same object.

The strike variable \(K\) used during calibration becomes the state variable \(F_t\) during simulation.

Conceptually:

```text
Market Quotes
        ↓
σloc(T,K)
        ↓
Calibration Complete
        ↓
Monte Carlo Simulation
        ↓
σloc(t,Ft)
```

The surface is simply being viewed from two different perspectives.

## Example

Suppose Dupire calibration produces:

$$
\sigma_{loc}(5,4%) =
25%
$$

This means:

```text
Expiry = 5 years
Strike = 4%
```

was associated with a local volatility of 25%.

Later, during a Monte Carlo simulation, one path reaches:

$$
t=5
$$

and

$$
F_t=4\%
$$

At that moment the simulation will query:

$$
\sigma_{loc}(5,4%)
$$

and obtain:

$$
25%
$$

The exact same surface value that was previously calibrated from market option prices.

## Why This Matters

This observation explains why Dupire local volatility perfectly reproduces the market vanilla option surface.

The model is calibrated so that every point on the local volatility surface is consistent with observed market option prices.

As a result:

- calibration is performed in quote space $(T,K)$
- simulation is performed in state space $(t,F_t)$

but both use the same local volatility function.

Understanding this connection is one of the key conceptual steps in moving from option market data to stochastic volatility modelling.

---

# 7.7 Off-Grid Interpolation

Market quotes only exist at a finite set of expiries and strikes.

For example:

```text
1Y × 5Y
2Y × 5Y
3Y × 5Y
5Y × 5Y
7Y × 5Y
10Y × 5Y
```

A trader may request pricing for:

```text
4Y × 5Y
```

which does not exist directly in the market data.

To support such requests, the local volatility surface is interpolated using:

```python
LinearNDInterpolator
```

in Python.

The C++ implementation uses bilinear interpolation.

---

# 7.8 Numerical Stability

Local volatility surfaces are significantly more sensitive than implied volatility surfaces.

Dupire requires numerical differentiation:

$$
\frac{\partial C}{\partial T}
$$

and

$$
\frac{\partial^2 C}{\partial K^2}
$$

Small pricing noise may therefore generate large local volatility fluctuations.

Common production solutions include:

- surface smoothing
- arbitrage filtering
- monotone interpolation
- regularization
- parametric volatility models

This is one reason why SABR models are frequently preferred in interest rate markets.

---

# 7.9 Cross-Language Validation

The Python implementation uses:

```python
LinearNDInterpolator
```

while the C++ implementation uses:

```text
Bilinear Interpolation
```

As a result, interpolated local volatility values may differ slightly even when:

- market data are identical
- option prices are identical
- Dupire calculations are identical

A validation experiment shows that when Python is forced to use bilinear interpolation, the resulting local volatility values match the C++ implementation to approximately:

$$
10^{-6}
$$

This confirms that the observed discrepancies originate from interpolation methodology rather than modelling differences.

---

# 7.10 Test Cases

## End-to-End Dupire Workflow

```python
test_dupire_workflow.py
```

Validates:

```text
Curve
    ↓
Vol Surface
    ↓
Price Surface
    ↓
Dupire Surface
```

and verifies that finite local volatility values are produced.

---

## Off-Grid Local Volatility Pricing

```python
test_off_grid_local_vol_pricing.py
```

Demonstrates:

- local volatility interpolation
- non-standard expiry handling
- integration with the Chapter 06 swaption pricer

The resulting price is intended as a workflow validation rather than a production local-volatility pricing engine.

---

# 7.11 Summary
## Quant Notes

This chapter introduces a core idea used throughout quantitative derivatives modelling:

> Market prices imply a volatility surface, and the volatility surface implies a stochastic process.

Understanding this connection is essential for:

- local volatility models
- stochastic volatility models
- SABR calibration
- Monte Carlo simulation
- finite difference pricing

The next chapter extends these ideas using the SABR model, which provides a more realistic description of interest rate volatility smiles and skews.

## Next Chapter

### Chapter 08 — SABR Volatility Surface Calibration

Topics include:

- SABR dynamics
- volatility smile generation
- skew modelling
- parameter calibration
- swaption volatility surface fitting
- market calibration techniques

```text
Local Volatility
        ↓
SABR
        ↓
Market Smile Calibration
```

This chapter serves as the bridge between classical local volatility models and modern interest-rate volatility modelling frameworks.
