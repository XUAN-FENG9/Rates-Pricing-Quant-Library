# 01 - Yield Curve Bootstrapping & Multi-Curve Framework

## 1.1 Overview

This module implements a full yield curve construction framework, starting from market instruments and building both:

* **Single-curve (legacy) framework**
* **Multi-curve (modern market standard)**

It also includes:

* Forward rate extraction
* DV01 (interest rate sensitivity)
* Multi-curve swap pricing

---

## 1.2 Why This Matters (FO Perspective)

Yield curves are the **foundation of all interest rate products**.

In modern markets:

* Discounting is based on **OIS (collateral rate)**
* Forward rates are derived from **LIBOR / term rates**

This leads to a **multi-curve framework**, which is essential for:

* Accurate pricing
* Risk management
* Hedging

---

## 1.3 Key Concepts

### 1. Discount Factor (DF)

Represents the present value of 1 unit of currency received in the future.

Used to discount all cash flows.


### 2. Bootstrapping

Sequentially constructing discount factors from market instruments:

* OIS → short end (direct DF)
* IRS → long end (solve for DF)


### 3. Forward Rates

Implied future interest rates derived from the curve:

$$F(t_1, t_2) = (\frac{DF(t_1)}{DF(t_2)} - 1) \cdot \frac{1}{t_2 - t_1}$$


### 4. Multi-Curve Framework

Modern pricing uses:

* **OIS curve → discounting**
* **LIBOR curve → forward rates**


### 5. Swap Pricing Equation

$$K * Σ DF(t_i) = 1 - DF(T)$$


### 6. DV01

Measures sensitivity of price to a 1 basis point move in rates.

---

## 1.4 Project Structure

```bash
python/
  instruments.py          # market instrument definitions
  interpolation.py       # log-linear interpolation
  curve.py               # curve object (DF, forward, zero)
  bootstrap_single_curve.py
  bootstrap_multi_curve.py
  pricer.py              # swap pricing
  risk.py                # DV01

cpp/
  curve.hpp / curve.cpp  # C++ implementation
  pricer.cpp
  main.cpp

notebooks/
  01_bootstrap_and_multicurve.ipynb

data/
  market_data_sample.csv

tests/
  test_curve.py
```

---

## 1.5 What This Module Demonstrates

* Building a yield curve from market data
* Understanding the difference between discounting and forwarding
* Implementing forward rate calculations
* Performing sensitivity analysis (DV01)
* Applying multi-curve pricing

---

## 1.6 Example Workflow

1. Load market data
2. Bootstrap OIS curve
3. Bootstrap LIBOR curve
4. Compute forward rates
5. Price swap under multi-curve
6. Compute DV01

---

## 1.7 FO Insights

* Curve smoothness is critical → impacts forward rates
* Mis-specified curves lead to incorrect hedging
* Multi-curve is required due to collateralization
* DV01 is one of the most important risk metrics

---

## 1.8 Limitations (Simplifications)

* No day count conventions
* Simplified accrual assumptions
* LIBOR curve approximated using IRS only
* No calendar adjustments

---

## 1.9 Author Notes

This module is designed to reflect how yield curves are used in a **Front Office quant environment**, with a focus on:

* clarity
* correctness
* financial intuition
