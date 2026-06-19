# Chapter 08 — SABR Volatility Surface Calibration

# 8.1 Introduction
## Overview

This chapter introduces SABR volatility surface calibration for interest-rate swaptions.

Previous chapters built the pricing and volatility infrastructure:

```text
Yield Curve
        ↓
Forward Starting Swap
        ↓
Black / Bachelier Swaption Pricing
        ↓
Dupire Local Volatility Surface
        ↓
SABR Volatility Surface Calibration
```

The SABR model is widely used in interest-rate markets because it provides a stable and interpretable way to fit volatility smiles and skews.

This chapter implements:

- Hagan SABR Black volatility formula
- One-expiry smile calibration
- Full SABR surface calibration across expiries
- Warm-start calibration for parameter stability
- SABR fitted volatility surface
- Market vs SABR residual surface
- SABR-implied swaption pricing
- Python and C++ implementations


# Project Structure

```text
08_sabr_vol_surface_calibration/
│
├── python/
│   ├── curve.py (reuse from previous chapter)
│   ├── forward_swap.py (reuse from previous chapter)
│   ├── black_swaption.py (reuse from previous chapter)
│   ├── market_data.py
│   ├── sabr_model.py
│   ├── sabr_calibration.py
│   ├── sabr_surface.py
│   ├── sabr_pricing.py
│   ├── plotting.py
│   └── diagnostics.py
│
├── cpp/
│   ├── curve.hpp
│   ├── curve.cpp
│   ├── forward_swap.hpp
│   ├── forward_swap.cpp
│   ├── black_swaption.hpp
│   ├── black_swaption.cpp
│   ├── SABRModel.hpp
│   ├── SABRModel.cpp
│   ├── SABRCalibration.hpp
│   ├── SABRCalibration.cpp
│   ├── SABRPricer.hpp
│   ├── SABRPricer.cpp
│   └── main.cpp
│
├── data/
│   ├── curve_data.csv
│   └── swaption_vol_surface.csv
│
├── tests/
│   ├── test_sabr_model.py
│   ├── test_sabr_calibration.py
│   └── test_sabr_surface.py
│
├── notebooks/
│   └── 08_sabr_vol_surface_calibration.ipynb
│
└── README.md
```

---

# 8.2 SABR Model

The SABR model describes the joint dynamics of a forward rate and its stochastic volatility.

The dynamics are:

$$
dF_t =
\alpha_t F_t^\beta dW_t^{(1)}
$$

$$
d\alpha_t =
\nu \alpha_t dW_t^{(2)}
$$

with correlation:

$$
dW_t^{(1)}dW_t^{(2)} =
\rho dt
$$

where:

| Parameter | Meaning |
|---|---|
| $$F_t$$ | Forward swap rate |
| $$\alpha_t$$ | Stochastic volatility level |
| $$\beta$$ | Elasticity parameter |
| $$\rho$$ | Correlation between rate and volatility shocks |
| $$\nu$$ | Volatility of volatility |

---

# 8.3 Hagan SABR Black Volatility

In practice, SABR is usually calibrated using Hagan's Black implied volatility approximation:

$$
\sigma_{SABR} =
\sigma_{SABR}
\left(
F,K,T;
\alpha,\beta,\rho,\nu
\right)
$$

The model maps SABR parameters into Black implied volatilities across strikes.

The calibration target is:

$$
\sigma_{SABR}(K_i)
\approx
\sigma_{market}(K_i)
$$

for each quoted strike \(K_i\).

---

# 8.4 Calibration Objective

For each expiry slice, we calibrate SABR parameters by minimizing:

$$
\min_{\alpha,\rho,\nu}
\sum_i
\left(
\sigma_{SABR}(K_i) -
\sigma_{market}(K_i)
\right)^2
$$

The parameter $\beta$ is fixed.

In this chapter, the default is:

$$
\beta = 0.5
$$

Only:

$$
\alpha,\rho,\nu
$$

are calibrated.

---

# 8.5 Why Fix Beta?

The parameter \(\beta\) is difficult to identify from a single smile slice because it interacts strongly with \(\alpha\).

Common choices are:

| Beta | Interpretation |
|---|---|
| $$\beta=0$$ | Normal-like dynamics |
| $$\beta=0.5$$ | CEV-style dynamics |
| $$\beta=1$$ | Lognormal-like dynamics |

In market practice, $\beta$ is often fixed by convention or desk preference.

---

# 8.6 Market Data Convention

The market data file is:

```text
swaption_vol_surface.csv
```

with columns:

```text
expiry,tenor,strike_shift_bp,black_vol_bp
```

The convention used in this chapter is:

```text
black_vol_bp = Black vol × 10000
```

For example:

```text
black_vol_bp = 2500
```

means:

$$
\sigma = 0.25 = 25\%
$$

The strike is constructed as:

$$
K =
F
+
\frac{\text{strike shift bp}}{10000}
$$

where $F$ is the forward swap rate.

---

# 8.6 Market Smile Slice

For each expiry $T$, the market smile is:

$$
\sigma_{market}(K)
$$

For example:

```text
5Y expiry × 5Y underlying swap tenor
```

gives one smile slice.

SABR is calibrated independently to each expiry slice.

---

# 8.7 Full SABR Surface Calibration

The full SABR surface is built by calibrating each expiry:

```text
1Y smile  → alpha, rho, nu
2Y smile  → alpha, rho, nu
3Y smile  → alpha, rho, nu
...
30Y smile → alpha, rho, nu
```

The output is a parameter term structure:

```text
expiry → alpha
expiry → rho
expiry → nu
```

This creates a fitted SABR volatility surface:

$$
\sigma_{SABR}(T,K)
$$

## Warm-Start Calibration

A naive slice-by-slice calibration can produce unstable parameters.

For example, if every expiry starts from the same initial guess, the optimizer may jump between local minima.

To improve stability, this chapter uses warm-start calibration:

```text
1Y calibrated parameters
        ↓
used as initial guess for 2Y
        ↓
2Y calibrated parameters
        ↓
used as initial guess for 3Y
        ↓
...
```

This helps produce smoother SABR parameter term structures.

## Parameter Bounds

The calibration uses parameter bounds to avoid degenerate solutions.

Typical constraints are:

$$
\alpha > 0
$$

$$
-0.90 < \rho < 0.90
$$

$$
0.05 < \nu < 2.0
$$

These bounds prevent unstable outcomes such as:

```text
nu → 0
rho → ±1
```

which usually indicate poor identifiability or an unstable calibration.

---

# 8.8 Interpretation of Parameters

## Alpha

$\alpha$ controls the volatility level.

A higher $\alpha$ generally shifts the smile upward.

In practice, $\alpha$ is often adjusted more frequently than $\rho$ and $\nu$, because it mainly controls the ATM volatility level.


## Rho

$\rho$ controls smile skew.

If:

$$
\rho < 0
$$

low-strike volatilities tend to become richer.

If:

$$
\rho > 0
$$

high-strike volatilities may become richer.


## Nu

$\nu$ controls smile curvature.

Higher $\nu$ generally produces more curvature and fatter wings.

---

# 8.9 Practical Calibration Note: Alpha-Only Updates

In practical desk workflows, SABR parameters are not always updated with the same frequency.

A common approach is:

```text
beta = fixed by convention
rho and nu = updated less frequently
alpha = updated more frequently
```

This is because:

- $\alpha$ mainly controls the volatility level
- $\rho$ controls skew
- $\nu$ controls smile curvature

Therefore, a desk may perform alpha-only updates for daily or intraday marking while keeping structural smile parameters fixed.

---

# 8.10 Market Surface vs SABR Surface

This chapter plots three surfaces:

## Market Implied Volatility Surface

$$
\sigma_{market}(T,K)
$$

This is the observed volatility surface from market quotes.

## SABR Fitted Volatility Surface

$$
\sigma_{SABR}(T,K)
$$

This is generated by the calibrated SABR parameters.

## Residual Surface

$$
Error(T,K)
= \sigma_{SABR}(T,K) -
\sigma_{market}(T,K)
$$

A good calibration should produce residuals that are small and stable across expiry and strike.

---

# 8.11 SABR vs Dupire

Chapter 07 used Dupire local volatility:

$$
\sigma_{loc}(T,K)
$$

Dupire is powerful because it can reproduce the vanilla option surface, but it is numerically fragile because it requires derivatives of option prices.

SABR is different.

It is a parametric stochastic-volatility model that produces a smooth smile through:

```text
alpha
rho
nu
```

Comparison:

| Feature | Dupire Local Vol | SABR |
|---|---|---|
| Input | Option price surface | Market vol smile |
| Output | Local vol surface | Parametric implied vol smile |
| Stability | Sensitive to derivatives | More stable |
| Interpretation | Less intuitive | Highly interpretable |
| Common rates use | Surface construction | Swaption smile calibration |

---

# 8.12 Swaption Pricing with SABR

SABR itself generates implied volatility.

The pricing workflow is:

```text
Expiry, tenor, strike
        ↓
Build forward-starting swap
        ↓
Compute forward swap rate
        ↓
Compute SABR Black vol
        ↓
Price with BlackSwaption
```

In this chapter, pricing reuses Chapter 06:

```text
ForwardStartingSwap
BlackSwaption
YieldCurve
```

This mirrors a common production structure:

```text
SABR = volatility model
Black = vanilla pricing formula
```

---
# 8.13 Summary
In the chapter, we have done:
### Python Implementation

The Python implementation includes:

- Hagan SABR volatility formula
- Slice calibration with scipy
- Full surface calibration
- Warm-start parameter calibration
- Alpha-only calibration extension
- Market / fitted / residual surface plotting
- SABR-implied swaption pricing

Python is used for:

```text
research
calibration
visual diagnostics
model validation
```

### C++ Implementation

The C++ implementation includes:

- Hagan SABR Black volatility formula
- SABR smile calibration
- Simple coordinate-search optimizer
- SABR fitted smile output
- SABR-implied Black swaption pricing

The C++ calibration demo uses a transparent coordinate-search optimizer.

It minimizes:

$$
\sum_i
\left(
\sigma_{SABR}(K_i) -
\sigma_{market}(K_i)
\right)^2
$$

The optimizer is intentionally simple and dependency-free for educational purposes.

In production, one would usually replace it with:

- Levenberg-Marquardt
- L-BFGS-B
- Nelder-Mead
- QuantLib optimizers
- internal desk calibration libraries

### Tests

The chapter includes tests for:

```text
test_sabr_model.py
test_sabr_calibration.py
test_sabr_surface.py
```

These verify:

- SABR volatility is positive
- one-slice calibration succeeds
- full-surface calibration runs end-to-end
- calibrated alpha and nu remain positive

## Key Lessons

1. SABR is a stochastic-volatility model for implied volatility smiles.
2. Hagan's approximation maps SABR parameters to Black implied volatilities.
3. \(\alpha\) controls volatility level.
4. \(\rho\) controls skew.
5. \(\nu\) controls curvature.
6. \(\beta\) is usually fixed.
7. Warm-start calibration improves parameter stability.
8. SABR is often more stable and interpretable than raw Dupire local volatility.
9. SABR vol can be passed into Black swaption pricing.
10. Calibration quality should be judged by both error and parameter stability.

## Quant Notes

A good SABR calibration is not only about minimizing RMSE.

A desk-quality calibration should also produce:

- stable parameter term structures
- plausible skew
- plausible curvature
- reasonable extrapolation
- low residual errors
- smooth behaviour across expiries

This is why surface diagnostics are essential.

The three most useful diagnostic plots are:

```text
Market Vol Surface
SABR Fitted Surface
Residual Surface
```

## Next Chapter

### Chapter 09 — Hull-White Short Rate Model

The next chapter moves from volatility smile calibration to interest-rate dynamics.

Topics include:

- one-factor Hull-White model
- mean reversion
- short-rate simulation
- zero-coupon bond pricing
- bond option pricing
- calibration to the initial yield curve

This is the first full short-rate dynamics model in the library.
