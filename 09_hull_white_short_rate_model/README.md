# Chapter 09 — Hull-White Short Rate Model

# 9.1 Introduction

This chapter introduces the one-factor Hull-White short-rate model, one of the most widely used interest-rate models in fixed income and derivatives pricing.

Unlike the previous chapters, which focused primarily on yield curves, swaps, swaptions, implied volatility surfaces, Dupire local volatility, and SABR calibration, this chapter models the evolution of the entire interest-rate environment through a stochastic short-rate process.

The Hull-White model is popular because it:

* Fits the initial yield curve exactly
* Allows negative interest rates
* Produces analytical bond and bond-option pricing formulas
* Supports Monte Carlo, tree, and finite-difference implementations
* Serves as the foundation for callable bonds, Bermudan swaptions, and XVA frameworks

This chapter implements:

* Hull-White short-rate dynamics
* Curve-consistent drift calibration
* Zero-coupon bond pricing
* Monte Carlo simulation
* Bond option pricing
* Parameter calibration

## Model Dynamics

The one-factor Hull-White model assumes:

$$
dr_t=
\left(
\theta(t) - a r_t
\right)dt
+
\sigma dW_t
$$

where:

| Symbol      | Meaning               |
| ----------- | --------------------- |
| $r_t$       | Short rate            |
| $a$         | Mean reversion speed  |
| $\sigma$    | Short-rate volatility |
| $\theta(t)$ | Drift adjustment      |
| $W_t$       | Brownian motion       |

The model extends the Vasicek framework by allowing a time-dependent drift term $\theta(t)$, ensuring consistency with today's observed yield curve.


## Project Structure

```text
09_hull_white_short_rate_model/
│
├── python/
│   ├── curve.py
│   ├── market_data.py
│   ├── hull_white_model.py
│   ├── bond_pricing.py
│   ├── hull_white_simulation.py
│   ├── option_pricing.py
│   ├── calibration.py
│   ├── plotting.py
│   └── diagnostics.py
│
├── cpp/
│   ├── curve.hpp
│   ├── curve.cpp
│   ├── HullWhiteModel.hpp
│   ├── HullWhiteModel.cpp
│   ├── BondPricing.hpp
│   ├── BondPricing.cpp
│   ├── HullWhiteSimulation.hpp
│   ├── HullWhiteSimulation.cpp
│   ├── BondOptionPricing.hpp
│   ├── BondOptionPricing.cpp
│   └── main.cpp
│
├── data/
│   └── usd_zero_curve.csv
│
├── tests/
│   ├── test_hull_white_model.py
│   ├── test_bond_pricing.py
│   └── test_simulation.py
│
├── notebooks/
│   └── 09_hull_white_short_rate_model.ipynb
│
└── README.md
```

## Reused Components

This chapter reuses the yield curve infrastructure developed previously:

```text
Chapter 01
Yield Curve Construction
        ↓
Chapter 06
Swaption Pricing
        ↓
Chapter 07
Local Volatility
        ↓
Chapter 08
SABR Calibration
        ↓
Chapter 09
Hull-White Dynamics
```

Specifically:

* YieldCurve
* Discount factor interpolation
* Zero-rate extraction

remain unchanged.

---

# 9.2 Hull-White Functions

## B(t,T)

The Hull-White bond pricing formula uses:

$$
B(t,T)=
\frac{
1-e^{-a(T-t)}
}{a}
$$

This function measures the sensitivity of a bond price to the current short rate.

For small maturities:

$$
B(t,T)
\approx
T-t
$$

For large maturities:

$$
B(t,T)
\rightarrow
\frac1a
$$

showing the effect of mean reversion.


## Theta Function

The drift adjustment is:

$$
\theta(t)=\frac{\partial f(0,t)}{\partial t}
+
a f(0,t)
+
\frac{\sigma^2}{2a}
\left(
1-e^{-2at}
\right)
$$

where:

$$
f(0,t)=
-\frac{\partial \ln P(0,t)}{\partial t}
$$

is the instantaneous forward rate.

The purpose of $\theta(t)$ is to ensure:

$$
P_{HW}(0,T)=
P_{Market}(0,T)
$$

for all maturities.

---

# 9.3 Zero-Coupon Bond Pricing

The Hull-White model belongs to the affine term-structure family.

Bond prices have the form:

$$
P(t,T)=
A(t,T)
\exp
\left(
-B(t,T)r_t
\right)
$$

where:

* $A(t,T)$ depends on the initial yield curve
* $B(t,T)$ captures short-rate sensitivity

This representation enables efficient pricing of many fixed-income derivatives.

---

# 9.4 Monte Carlo Simulation

The short rate evolves according to:

$$
r_{t+\Delta t}=
r_t +\left(\theta(t) a r_t\right)\Delta t
+
\sigma
\sqrt{\Delta t}
Z
$$

with:

$$
Z
\sim
N(0,1)
$$

The simulation workflow is:

```text
Initial Yield Curve
        ↓
Compute θ(t)
        ↓
Simulate Short Rate Paths
        ↓
Generate Discount Factors
        ↓
Price Interest Rate Products
```

## Discount Factors from Simulated Paths

For each path:

$$
D(0,T)=\exp
\left(
\int_0^T r_t dt
\right)
$$

Numerically:

$$
D(0,T)
\approx
\exp
\left(
\sum r_i \Delta t
\right)
$$

Monte Carlo bond prices are obtained by averaging pathwise discount factors.

---

# 9.5 Bond Option Pricing

This chapter implements European options on zero-coupon bonds.

The payoff is:

$$
\max
\left(
P(\tau,T)-K,
0
\right)
$$

for a call option.

Hull-White admits a closed-form solution for these products, analogous to Black-style formulas.

This makes the model attractive for:

* callable bonds
* Bermudan swaptions
* structured products

---

# 9.6 Calibration

The chapter includes a simple calibration framework.

Parameters:

$$
a
$$

and

$$
\sigma
$$

are fitted to observed option prices.

Workflow:

```text
Market Option Prices
        ↓
Hull-White Pricing
        ↓
Objective Function
        ↓
Optimizer
        ↓
Calibrated Parameters
```

The notebook uses synthetic market prices for demonstration.

In production, calibration is typically performed against:

* ATM swaption volatilities
* swaption cubes
* cap/floor volatilities

---

# 9.7 Why Hull-White?

Compared with Black or SABR:

| Model      | Dynamics    | Negative Rates | Yield Curve Consistency |
| ---------- | ----------- | -------------- | ----------------------- |
| Black      | No          | No             | No                      |
| SABR       | Smile Model | Limited        | No                      |
| Hull-White | Short Rate  | Yes            | Yes                     |

Hull-White captures the evolution of the interest-rate environment rather than merely fitting option smiles.

---
# 9.8 Summary
## Practical Applications

The model is widely used for:

* Callable bond pricing
* Bermudan swaption pricing
* Mortgage-backed securities
* Interest-rate risk management
* Exposure simulation
* XVA calculations

Many bank risk systems still rely on Hull-White or extensions thereof.

## Limitations

Although useful, the model has several weaknesses:

* Single-factor structure
* Constant volatility
* Limited smile generation
* Unrealistic long-term rate dynamics
* Weak fit to volatility surfaces

These limitations motivate stochastic-volatility extensions.

## Relationship to Previous Chapters

The progression of the library is now:

```text
01 Curve Construction
02 Parametric Curves
03 FRA Pricing
04 Swap Pricing
05 DV01 and Risk
06 Swaption Pricing
07 Local Volatility and Dupire
08 SABR Calibration
09 Hull-White Short Rate Model
```

Chapter 09 is the first model that describes the evolution of interest rates themselves.

Previous chapters primarily described prices and implied volatilities.


## Next Chapter

### Chapter 10 — Short Rate Models with Stochastic Volatility

Hull-White assumes:

$$
\sigma =constant
$$

which is often unrealistic.

Chapter 10 introduces stochastic volatility:

$$
dr_t =
\left(
\theta(t)-a r_t
\right)dt
+
v_t dW_t^r
$$

with:

$$
dv_t =
\kappa(\bar v-v_t)dt
+
\eta\sqrt{v_t}dW_t^v
$$

allowing volatility itself to evolve randomly through time.

This provides a bridge between:

* classical short-rate models
* stochastic volatility models
* modern interest-rate derivatives frameworks.
