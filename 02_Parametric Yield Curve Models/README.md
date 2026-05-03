# Chapter 02 — Parametric Yield Curve Models

## Overview

This chapter introduces **parametric yield curve modeling**, one of the most important topics in fixed income quantitative finance.

Unlike bootstrapped curves, which exactly fit market instruments but can become noisy and unstable, parametric models provide:

- smooth yield curves
- stable forward rates
- interpretable economic factors
- robust risk sensitivities

This chapter implements:

- Nelson-Siegel model
- Svensson model
- parameter calibration
- forward rate extraction
- curve visualization
- calibration error minimization

Both **Python** and **C++** implementations are provided.

---

# Motivation

In real trading systems, raw market curves are often noisy due to:

- bid/ask spreads
- liquidity differences
- interpolation artifacts
- inconsistent quotes

Front-office trading desks therefore frequently use **parametric smoothing models** to:

- stabilize risk calculations
- improve scenario analysis
- generate smoother forward curves
- reduce arbitrage opportunities

---

# Nelson-Siegel Model

The Nelson-Siegel model represents the zero rate curve as:

$$
y(t)= \beta_0
+
\beta_1
\left(
\frac{1-e^{-t/\tau}}{t/\tau}
\right)
+
\beta_2
\left(
\frac{1-e^{-t/\tau}}{t/\tau} - e^{-t/\tau}
\right)
$$

where:

| Parameter | Interpretation |
|---|---|
| $$\beta_0$$ | Long-term level |
| $$\beta_1$$ | Short-end slope |
| $$\beta_2$$ | Medium-term curvature |
| $$\tau$$ | Decay / hump location |

---

# Economic Interpretation

## Long-Term Level — $$\beta_0$$

Controls the asymptotic level of the curve.

As maturity becomes large:

$$
\lim_{t \to \infty} y(t) = \beta_0
$$

This represents the market's long-run interest rate expectation.

---

## Slope Factor — $$\beta_1$$

Controls the steepness of the short end.

- negative values → upward sloping curve
- positive values → inverted curve

This factor is highly sensitive to:

- central bank policy
- monetary tightening
- liquidity conditions

---

## Curvature Factor — $$\beta_2$$

Controls the hump shape.

This factor affects:

- belly of the curve
- medium maturities
- forward curve dynamics

---

## Decay Parameter — $$\tau$$

Controls where the hump occurs.

Small $$\tau$$:
- hump appears earlier

Large $$\tau$$:
- hump shifts further out

---

# Svensson Extension

The Svensson model extends Nelson-Siegel with an additional curvature term:

$$
y(t) =
\beta_0
+
\beta_1 f_1(t)
+
\beta_2 f_2(t)
+
\beta_3 f_3(t)
$$

This additional flexibility improves fitting quality for:

- sovereign curves
- central bank curves
- long-dated swap curves

The Svensson model is widely used by:

- central banks
- macroeconomic institutions
- sovereign debt agencies

---

# Calibration

The model parameters are calibrated by minimizing the squared fitting error:

$$
\text{Error} = \sum_i
\left(
y_{\text{market}}(t_i) - y_{\text{model}}(t_i)
\right)^2
$$

Optimization is performed using numerical methods such as:

- Nelder-Mead
- Levenberg-Marquardt
- gradient-based optimization

---

# Discount Factors

Zero rates are converted into discount factors using:

$$
DF(t) = e^{-y(t)t}
$$

Discount factors are fundamental in pricing:

- swaps
- swaptions
- bonds
- FRAs
- futures

---

# Forward Rates

Forward rates are implied from discount factors:

$$
F(t_1,t_2)
= [\frac{DF(t_1)}{DF(t_2)} - 1] \cdot \frac{1}{t_2-t_1}
$$

Parametric models are especially useful because they generate:

- smoother forward curves
- more stable sensitivities
- lower numerical noise

---

# Why Front-Office Quants Care

## Stable Risk Sensitivities

Raw bootstrapped curves can generate unstable:

- DV01
- bucket risk
- forward sensitivities

Parametric smoothing improves stability.

---

## Better Forward Curves

Forward rates are extremely sensitive to interpolation noise.

Nelson-Siegel models help produce:

- smoother forwards
- more realistic term structures
- lower arbitrage risk

---

## Scenario Analysis

Parametric models allow intuitive macro shocks:

| Shock | Interpretation |
|---|---|
| Increase $$\beta_0$$ | Parallel shift |
| Increase $$\beta_1$$ | Steepening |
| Increase $$\beta_2$$ | Belly hump |

This is highly useful in:

- stress testing
- macro trading
- risk management

---

# Typical Front-Office Applications

## Rates Trading

Used for:

- curve trading
- steepener/flatteners
- macro RV strategies

---

## XVA Systems

Smooth curves improve:

- exposure calculations
- Monte Carlo stability
- sensitivity consistency

---

## Risk Management

Parametric curves are widely used in:

- VaR systems
- stress scenarios
- economic capital models

---

# Limitations

Despite their advantages, parametric models also have limitations.

## Underfitting

They may fail to perfectly fit all market instruments.

---

## Local Structure Loss

Fine-grained market features may disappear.

---

## Calibration Instability

Poor initial guesses can lead to:

- local minima
- unstable parameters
- unrealistic shapes

---

# Project Structure

```text
02_parametric_yield_curve_models/
│
├── python/
│   ├── nelson_siegel.py
│   ├── svensson.py
│   ├── calibration.py
│   ├── market_curve.py
│   └── plotting.py
│
├── cpp/
│   ├── nelson_siegel.hpp
│   ├── nelson_siegel.cpp
│   ├── calibration.cpp
│   └── main.cpp
│
├── notebooks/
│   └── 02_nelson_siegel_model.ipynb
│
├── data/
│   └── usd_zero_curve_sample.csv
│
├── tests/
│   └── test_nelson_siegel.py
│
└── README.md
```

---

# Python Dependencies

Install required packages:

```bash
pip install numpy pandas matplotlib scipy
```

---

# Running the Notebook

Launch Jupyter Notebook:

```bash
jupyter notebook
```

Open:

```text
notebooks/02_nelson_siegel_model.ipynb
```

---

# Example Workflow

## Load Market Data

```python
curve = MarketCurve(
    "../data/usd_zero_curve_sample.csv"
)
```

---

## Calibrate Model

```python
params = calibrate_nelson_siegel(
    curve.times,
    curve.rates
)
```

---

## Build Curve

```python
model = NelsonSiegelCurve(*params)
```

---

## Plot Curve

```python
plot_curve(
    curve.times,
    curve.rates,
    model
)
```

---

# Expected Results

The fitted curve should:

- remain smooth
- avoid oscillations
- capture overall market structure
- generate stable forward rates

---

# Key Quantitative Finance Concepts

This chapter introduces several core quantitative finance concepts:

- term structure modeling
- curve calibration
- nonlinear optimization
- factor interpretation
- forward rate dynamics
- curve smoothing

These concepts are foundational for:

- swaption modeling
- SABR calibration
- HJM models
- LMM frameworks
- XVA systems

---

# Suggested Extensions

Possible future improvements:

- constrained optimization
- arbitrage-free smoothing
- dynamic Nelson-Siegel models
- Kalman filtering
- PCA factor analysis
- stochastic term structure models

---

# References

## Academic

- Nelson, C. and Siegel, A. (1987)
- Svensson, L. (1994)

---

## Industry

- Fixed Income Modeling — Damiano Brigo
- Interest Rate Models — Rebonato
- QuantLib documentation

---

# Author Notes

This chapter focuses on:

- intuition
- implementation
- front-office relevance
- numerical stability

The objective is not only to fit curves, but to understand:

- why traders use parametric models
- how curve shape impacts risk
- how smoothing affects pricing systems
