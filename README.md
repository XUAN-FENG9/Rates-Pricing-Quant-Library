# Rates Pricing Quant Library
## 📄 Companion Paper

This repository serves as an open Python/C++ computational companion to the following published survey article:

> **Feng, X., Huseynov, S. and Mavroyiannis, D. (2026).  
> “The Evolution of Interest-Rate Models: From the Yield Curve to the Swaption Cube.”  
> *Journal of Economic Surveys*.**  
> https://doi.org/10.1111/joes.70161

The paper develops the conceptual and historical framework for modern interest-rate modelling, while this repository provides transparent and reproducible implementations for selected components of that framework, including yield-curve construction, swap pricing and risk, swaption pricing, volatility modelling, term-structure models, Monte Carlo methods, and counterparty exposure/XVA.

The paper and repository are intended to be used together: **the article explains why the models evolved and how they fit into a modern pricing architecture; the code shows how selected parts of that architecture can be implemented and explored in practice.**

If you use this repository in academic work, please cite the companion paper.

---
A practical interest-rate quantitative finance library built in **Python and C++**, covering the full path from yield-curve construction to derivatives pricing, volatility modeling, Monte Carlo simulation, early-exercise products, counterparty exposure, and XVA.

The project is organized as a sequence of connected chapters. Each chapter introduces the financial intuition, derives the main equations, implements the model, and demonstrates how the output can be used in pricing or risk analysis.

The library is designed to answer a practical question:

> How can the main building blocks of an interest-rate pricing system be understood, implemented, tested, and connected into one coherent framework?

---

## 1. What This Project Does

The repository develops an interest-rate modeling stack progressively:

```text
Market quotes
    ↓
Yield curves and forward rates
    ↓
Linear rates products
    ↓
Risk sensitivities
    ↓
European options and volatility surfaces
    ↓
Short-rate and forward-rate models
    ↓
Bermudan optionality
    ↓
Monte Carlo exposure and XVA
```

The chapters cover:

- single-curve and multi-curve construction;
- Nelson–Siegel and Svensson curve models;
- forward rates and FRA pricing;
- interest-rate swaps and DV01;
- Black and Bachelier swaption pricing;
- Dupire local volatility;
- SABR calibration;
- Hull–White and stochastic-volatility short-rate models;
- Bermudan swaption pricing by trees and Least-Squares Monte Carlo;
- Gaussian LIBOR Market Model simulation;
- an LMM–SABR hybrid model;
- counterparty exposure, EE, EPE, PFE, CVA, DVA, and FVA.

---

## 2. Why This Project Matters

Interest-rate models are often studied separately: curve construction in one course, option pricing in another, and exposure or XVA much later.

In practice, these components are connected.

A swaption model requires an initial curve. A Monte Carlo model requires volatility and correlation assumptions. A counterparty exposure engine requires future market scenarios and future trade revaluation. A useful pricing library must therefore connect market data, mathematical models, numerical methods, and risk outputs.

For example, a simple forward rate is derived from discount factors through:

$$
L_i(0)=
\frac{1}{\delta_i}
\left[
\frac{P(0,T_i)}
{P(0,T_{i+1})}-
1
\right].
$$

The same forward curve may later become:

- an input to swap pricing;
- the underlying of a swaption;
- the initial state of an LMM;
- a simulated risk factor for future exposure.

The value of this repository lies not only in implementing individual formulas, but also in showing how the formulas fit together.

---

## 3. Who This Repository Is For

This project is suitable for:

- students learning fixed-income quantitative finance;
- junior quants preparing for pricing, model validation, or quantitative-development roles;
- practitioners moving from theory to implementation;
- researchers who need transparent reference implementations;
- developers learning how Python prototypes translate into C++;
- risk professionals who want to understand the pricing models behind sensitivities, exposure, and XVA.

The code emphasizes:

- financial intuition;
- explicit model assumptions;
- readable numerical workflows;
- modular Python and C++ implementations;
- diagnostics and tests;
- consistency between theory and implementation.

It is an educational library rather than a production trading system.

---

## 4. Python and C++

Python is used for:

- rapid model development;
- calibration;
- numerical experimentation;
- diagnostics;
- visualization;
- Jupyter notebooks.

C++ is used to demonstrate:

- typed model interfaces;
- reusable pricing components;
- faster simulation workflows;
- separation between data, model, simulation, and pricing layers;
- how research code can evolve toward a quantitative library architecture.

The Python and C++ implementations are intended to explain the same financial ideas rather than reproduce a large commercial pricing framework.

---

## 5. Core Quantitative Framework

The repository builds around several recurring objects.

### Discount factors

The value at time $0$ of one unit received at maturity $T$ is:

$$
P(0,T).
$$

### Forward rates

For accrual period $\delta_i$:

$$
1+\delta_iL_i(0)=
\frac{P(0,T_i)}
{P(0,T_{i+1})}.
$$

### Swap value

For a payer-fixed swap with notional $N$, fixed rate $K$, and annuity $A(0)$:

$$
V_{\mathrm{payer}}(0)=
N\left[
P(0,T_a)-
P(0,T_b)-
KA(0)
\right].
$$

### Option value

A European option is represented as a discounted expectation under an appropriate pricing measure:

$$
V(0)=
P(0,T)
\mathbb{E}^{T}
\left[
\mathrm{Payoff}(T)
\right].
$$

### Monte Carlo valuation

With $M$ simulated paths:

$$
V(0)
\approx
\frac{1}{M}
\sum_{m=1}^{M}
D^{(m)}(0,T)
\mathrm{Payoff}^{(m)}.
$$

### Counterparty exposure

Expected Exposure at time $t$ is:

$$
EE(t)=
\mathbb{E}
\left[
\max
\left(
V(t),0
\right)
\right].
$$

Potential Future Exposure at confidence level $q$ is:

$$
PFE_q(t)=
Q_q
\left[
\max
\left(
V(t),0
\right)
\right].
$$

These objects connect the early curve chapters to the later simulation, optionality, and XVA chapters.

---

## 6. Chapter Roadmap

### Chapter 01 — Yield Curve Bootstrapping

Builds single-curve and multi-curve term structures from market instruments. Introduces discount factors, zero rates, forward rates, OIS discounting, swap pricing, interpolation, and DV01.

### Chapter 02 — Parametric Yield Curve Models

Implements Nelson–Siegel and Svensson models. Focuses on curve smoothing, economically interpretable factors, calibration, forward-rate extraction, and comparison with directly bootstrapped curves.

### Chapter 03 — Forward Rates and FRA Pricing

Derives implied forward rates and prices Forward Rate Agreements. Connects discount curves to future borrowing and lending rates.

### Chapter 04 — Interest-Rate Swap Pricing

Builds fixed and floating cash-flow schedules, par swap rates, present values, and payer- and receiver-swap valuation.

### Chapter 05 — Swap Risk and Sensitivity

Extends swap valuation into risk analysis. Covers parallel DV01, key-rate DV01, curve shocks, steepeners, flatteners, and P&L interpretation.

### Chapter 06 — Black and Bachelier Swaption Pricing

Implements European swaption pricing under lognormal and normal assumptions. Includes annuity calculation, forward swap rates, implied volatility, negative-rate handling, and model comparison.

### Chapter 07 — Local Volatility and Dupire

Constructs an option-price surface and derives local volatility through the Dupire equation. Examines interpolation, numerical differentiation, surface diagnostics, and off-grid pricing.

### Chapter 08 — SABR Volatility-Surface Calibration

Implements SABR smile parameterization and calibration across expiry and tenor dimensions. Studies the roles of $ \alpha $, $ \beta $, $ \rho $, and $ \nu $ in controlling volatility level, elasticity, skew, and curvature.

### Chapter 09 — Hull–White Short-Rate Model

Implements a one-factor mean-reverting short-rate model, bond pricing, calibration concepts, simulation, and interest-rate derivative valuation.

### Chapter 10 — Short-Rate Models with Stochastic Volatility

Extends short-rate dynamics by allowing volatility itself to evolve stochastically. Examines the interaction between rate mean reversion, stochastic variance, correlation, and non-Gaussian risk.

### Chapter 11 — Bermudan Swaption Tree Pricing

Prices Bermudan swaptions through backward induction on a recombining short-rate tree. Introduces early-exercise decisions, continuation value, exercise boundaries, and lattice diagnostics.

### Chapter 12 — Bermudan Swaption Least-Squares Monte Carlo

Implements Longstaff–Schwartz regression for Bermudan optionality. Covers simulated state variables, basis functions, continuation-value estimation, exercise strategy, and lower-bound pricing.

### Chapter 13 — Gaussian LIBOR Market Model

Simulates a complete family of forward rates under a multi-factor Gaussian LMM. Includes tenor structure, deterministic normal volatility, correlation, PCA factor reduction, measure-consistent drift, Monte Carlo pricing, and diagnostics.

### Chapter 14 — LMM–SABR Hybrid Model

Extends the LMM by adding stochastic volatility and shifted CEV dynamics. The hybrid framework generates richer skew, smile, and tail behavior than a Gaussian forward-rate model.

### Chapter 15 — Interest-Rate Counterparty Exposure and XVA

Reuses the Chapter 13 Gaussian LMM paths to revalue interest-rate swaps at future dates. Builds netting-set mark-to-market distributions and calculates EE, ENE, EPE, PFE, CVA, DVA, and simplified FVA.

---

## 7. Suggested Learning Path

The chapters are designed to be studied in order, but they can also be grouped into four blocks.

### Foundations

```text
01 → 02 → 03 → 04 → 05
```

Curves, forwards, swaps, and risk.

### European optionality and volatility

```text
06 → 07 → 08
```

Swaption pricing, local volatility, and SABR.

### Dynamic interest-rate models and early exercise

```text
09 → 10 → 11 → 12
```

Short-rate dynamics, stochastic volatility, trees, and Least-Squares Monte Carlo.

### Forward-rate simulation and counterparty risk

```text
13 → 14 → 15
```

LMM simulation, stochastic-volatility extensions, and exposure/XVA.

Readers interested primarily in front-office linear rates can begin with Chapters 01–06. Readers focused on model validation or exotic derivatives should continue through Chapters 07–14. Readers interested in counterparty risk and XVA should study Chapters 04, 05, 13, and 15 together.

---

## 8. Design Philosophy

The repository follows several principles:

1. **Theory before machinery**  
   Each model begins with its economic purpose and mathematical structure.

2. **Transparent assumptions**  
   Simplified conventions are stated rather than hidden behind a framework.

3. **Connected chapters**  
   Later chapters reuse curves, products, and simulation concepts developed earlier.

4. **Python for exploration, C++ for structure**  
   Both languages serve different parts of the learning process.

5. **Risk as a first-class output**  
   The project does not stop at present value. It also examines sensitivities, scenarios, exercise behavior, exposure, and valuation adjustments.

6. **Numerical diagnostics matter**  
   Calibration error, arbitrage conditions, simulation stability, convergence, and boundary behavior are treated as part of model implementation.

---

## 9. Scope and Limitations

The repository is designed for education, research, and interview preparation.

It does not attempt to include every production requirement, such as:

- complete market conventions and holiday calendars;
- all day-count and business-day rules;
- production curve stripping across every instrument class;
- full collateral and clearing specifications;
- industrial calibration infrastructure;
- distributed Monte Carlo;
- automatic differentiation;
- production P&L explain;
- regulatory capital engines;
- full MVA and KVA frameworks.

The simplified structure makes the model logic visible. A production implementation would require additional market conventions, numerical safeguards, calibration controls, performance engineering, governance, and testing.

---

## 10. Overall Project Structure

```text
Rates-Pricing-Quant-Library/
│
├── 01_yield_curve_bootstrap/
│   └── Single-curve and multi-curve construction, forwards,
│       swap pricing, interpolation, and DV01
│
├── 02_parametric_yield_curve_models/
│   └── Nelson–Siegel and Svensson calibration and smoothing
│
├── 03_forward_rates_and_fra_pricing/
│   └── Forward-rate extraction and FRA valuation
│
├── 04_interest_rate_swap_pricing/
│   └── Fixed and floating legs, par rates, and swap valuation
│
├── 05_swap_risk_sensitivity/
│   └── Parallel DV01, key-rate risk, and curve scenarios
│
├── 06_black_swaption_pricing/
│   └── Black, Bachelier, implied volatility, and swaption pricing
│
├── 07_local_volatility_and_dupire/
│   └── Option-price surfaces, Dupire local volatility,
│       interpolation, and off-grid pricing
│
├── 08_SABR_vol_surface_calibration/
│   └── SABR smile modeling and volatility-surface calibration
│
├── 09_hull_white_short_rate_model/
│   └── Hull–White dynamics, simulation, bonds, and derivatives
│
├── 10_short_rate_models_with_stochastic_volatility/
│   └── Mean-reverting rates with stochastic volatility
│
├── 11_bermudan_swaption_tree_pricing/
│   └── Recombining trees, backward induction, and early exercise
│
├── 12_bermudan_swaption_lsm_pricing/
│   └── Least-Squares Monte Carlo and continuation-value regression
│
├── 13_gaussain_libor_market_model_lmm/
│   └── Multi-factor Gaussian LMM simulation, PCA, pricing,
│       and diagnostics
│
├── 14_lmm_sabr_hybrid_model/
│   └── LMM with shifted CEV dynamics and stochastic volatility
│
├── 15_Interest-Rate Counterparty Exposure and XVA/
│   └── Future swap revaluation, netting-set exposure,
│       EE, EPE, PFE, CVA, DVA, and FVA
│
├── .gitattributes
├── .gitignore
└── README.md
```

Within most chapters, the internal structure follows:

```text
chapter/
├── python/       # Core Python implementation
├── cpp/          # C++ implementation
├── notebooks/    # Guided numerical walkthrough
├── tests/        # Unit and consistency tests
├── data/         # Sample market data where required
└── README.md     # Theory, workflow, and limitations
```

---

## 11. Final Perspective

This repository is not a collection of disconnected pricing formulas.

It is a progressive implementation of an interest-rate quantitative workflow:

```text
construct the curve
        ↓
extract tradable rates
        ↓
price linear products
        ↓
measure sensitivities
        ↓
price optionality
        ↓
calibrate volatility
        ↓
simulate the term structure
        ↓
model early exercise
        ↓
measure counterparty exposure
        ↓
calculate valuation adjustments
```

The aim is to make interest-rate quantitative finance understandable at three levels simultaneously:

- the financial intuition;
- the mathematical model;
- the working implementation.

The result is a structured learning and reference library for anyone who wants to move from fixed-income theory toward practical quantitative pricing, model validation, risk management, or front-office development.
