# Chapter 06 — Black Swaption Pricing


# 6.1 Overview


This chapter introduces:

- European swaptions

- Black's model

- implied volatility

- volatility smiles

- swaption Greeks

- volatility risk



We now move from:

> linear interest rate products

to:

> nonlinear volatility derivatives.

---

# 6.2 What is a Swaption?

A swaption is:

> an option on an interest rate swap.

The holder has the right, but not the obligation, to enter into a swap at a future date.


## Types of Swaptions

### Payer Swaption

Right to:

- pay fixed

- receive floating

Benefits when rates rise.

### Receiver Swaption

Right to:

- receive fixed

- pay floating

Benefits when rates fall.

---

# 6.3 Black's Model

Market standard swaption pricing model.

The Black formula prices swaptions using:

- forward swap rates

- implied volatility

- swap annuity

## Black Formula

For payer swaptions:

$$
Price = N \\times A \\times \\left(F N(d\_1) - K N(d\_2)\\right)
$$

where:
$$
d\_1 = \\frac{\\ln(F/K) + \\frac12 \\sigma^2 T}{\\sigma \\sqrt{T}}
$$

$$
d\_2 = d\_1 - \\sigma\\sqrt{T}
$$

---

# 6.4 Important Concepts

## Forward Swap Rate

The underlying state variable.

## Annuity

Present value of swap fixed-leg accruals.

## Implied Volatility

Volatility implied by market swaption prices.

## Volatility Smile

Market implied volatilities vary by strike.

This creates:

- volatility smiles

- volatility skews

Black's model cannot fully explain this phenomenon.

This motivates:

- SABR

- stochastic volatility

- local volatility models

---

# 6.5 Greeks

This chapter introduces:

- Vega
- 
- volatility sensitivity

Later chapters extend this to:

- Delta

- Gamma

- cross-greeks

---

# 6.6 Project Structure

```text

06\_black\_swaption\_pricing/
│
├── python/
│   ├── curve.py
│   ├── forward\_swap.py
│   ├── black\_swaption.py
│   ├── bachelier\_swaption.py
│   ├── implied\_vol.py
│   ├── greeks.py
│   ├── plotting.py
│   └── market\_data.py
│
├── cpp/
│   ├── curve.hpp
│   ├── curve.cpp
│   ├── forward\_swap.hpp
│   ├── forward\_swap.cpp
│   ├── black\_swaption.hpp
│   ├── black\_swaption.cpp
│   ├── bachelier\_swaption.hpp
│   ├── bachelier\_swaption.cpp
│   └── main.cpp
│
├── notebooks/
│   └── 06\_black\_swaption\_pricing.ipynb
│
└── README.md

```

---

# 6.7 Summary

## Quant Perspective

Swaptions are among the most important rates derivatives globally.

Used heavily for:

- macro trading

- callable structures

- Bermudan products

- structured rates desks

## Engineering Insight

Production swaption systems require:

- volatility surfaces

- SABR calibration

- interpolation

- smile dynamics

- Monte Carlo engines

This chapter introduces the first layer of rates volatility modeling.

---

# 6.8 Python vs C++

## Python

Used for:

- prototyping

- research

- calibration

- analytics

## C++

Used for:

- production pricing

- real-time volatility systems

- risk infrastructure

- large-scale Monte Carlo

---

# 6.9 Next Chapter

## Chapter 07: Local Volatility and Dupire Model

In this chapter we move beyond the assumption of a single constant volatility and introduce:

- local volatility surfaces
- strike-dependent volatility
- maturity-dependent volatility
- implied volatility surface construction
- Dupire's local volatility framework

We will learn how to extract a local volatility surface from market option prices and understand the relationship between:

- market implied volatility
- local volatility
- option smile dynamics

This chapter serves as the bridge between simple Black-style models and more advanced stochastic volatility models.

## Then Chapter 08： SABR Volatility Surface Calibration

After building the local volatility framework, we introduce the industry-standard SABR model.

Topics include:

- SABR dynamics
- volatility smile generation
- volatility skew behavior
- parameter calibration
- market swaption surface fitting
- extrapolation beyond liquid strikes

We will calibrate:

$$
(\alpha,\beta,\rho,\nu)
$$

to market swaption volatilities and compare SABR-generated smiles against observed market smiles.

## Roadmap

```text
Yield Curves
    ↓
Forward Rates
    ↓
Swaps
    ↓
Risk Sensitivities
    ↓
Black / Bachelier Swaptions
    ↓
Local Volatility & Dupire      (Chapter 07)
    ↓
SABR Calibration              (Chapter 08)
    ↓
Short Rate Models
    ↓
LMM Monte Carlo
    ↓
Bermudan Swaptions
```

This moves us from:

> flat volatility

to:

> realistic volatility modeling.

## Key Takeaway

Chapter 06 introduced:

- forward-starting swaps
- Black swaption pricing
- Bachelier pricing
- implied volatility
- volatility smiles
- vega risk

Chapter 07 will answer:

> If the market volatility smile is real, what local volatility surface is implied by those option prices?

Chapter 08 will answer:

> How can we fit a realistic parametric model to the entire swaption volatility surface?

Together, Chapters 07 and 08 form the foundation of modern interest-rate volatility modeling used on front-office rates derivatives desks.
