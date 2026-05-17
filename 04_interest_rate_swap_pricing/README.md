# Chapter 04 — Interest Rate Swap Pricing


# 4.1 Overview

This chapter introduces:

- fixed-for-floating swaps

- swap cashflows

- swap NPV

- par swap rates

- payer and receiver swaps


Interest rate swaps are among the most important products in fixed income markets.

---

# 4.2 Swap Structure

A plain vanilla swap exchanges:

- fixed coupons
- floating coupons


## Fixed Leg


$$
CF\_{fixed} = N \\times K \\times \\Delta
$$

## Floating Leg


$$
CF\_{float} = N \\times F \\times \\Delta
$$

---
# 4.3 Swap Valuation

- Payer swap:

$$
NPV = PV\_{float} - PV\_{fixed}
$$

- Receiver swap:

$$
NPV = PV\_{fixed} - PV\_{float} 
$$

---
# 4.4 Par Swap Rate

$$
K = \\frac{1 - DF(T)}{\\sum\_i \\Delta\_i DF(t\_i)}
$$

---
# 4.5 Key Quantitative Concepts


This chapter introduces:


- discounted cashflow pricing

- swap valuation

- forward projection

- par rates

- curve sensitivity



These concepts are foundational for:



- swaptions

- Bermudan products

- LMM models

- XVA systems


---
# 4.6 Project Structure



```text

04_interest_rate_swap_pricing/
│
├── python/
│   ├── curve.py
│   ├── fixed_leg.py
│   ├── floating_leg.py
│   ├── swap.py
│   ├── market_data.py
│   └── plotting.py
│
├── cpp/
│   ├── curve.hpp
│   ├── curve.cpp
│   ├── swap.hpp
│   ├── swap.cpp
│   └── main.cpp
│
├── notebooks/
│   └── 04_interest_rate_swap_pricing.ipynb
│
├── data/
│   └── usd_zero_curve.csv
│
├── tests/
│   └── test_swap.py
│
└── README.md

```

\---

