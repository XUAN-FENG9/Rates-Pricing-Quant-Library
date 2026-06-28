# Chapter 11 — Bermudan Swaption Tree Pricing

# 11.1 Introduction
## Overview

This chapter introduces the pricing of Bermudan swaptions using a short-rate tree.

Unlike a European swaption, which may only be exercised on a single date, a Bermudan swaption can be exercised on multiple predetermined exercise dates. The pricing problem therefore becomes an optimal stopping problem requiring backward induction.

This chapter builds directly upon the Hull–White short-rate model developed in Chapter 09.

```text
Chapter 09
Hull-White Short Rate Model
        ↓
Chapter 11
Bermudan Swaption Tree Pricing
```

The implementation includes

- Bermudan exercise schedule
- market-style underlying swap definition
- Hull–White short-rate tree
- dynamic swap valuation
- backward induction
- exercise boundary analysis
- Python and C++ implementations

## Project Structure

```text
11_bermudan_swaption_tree_pricing/
│
├── python/
│   ├── swap_schedule.py
│   ├── bermudan_swaption.py
│   ├── hull_white_tree.py
│   ├── tree_pricer.py
│   ├── plotting.py
│   └── diagnostics.py
│
├── cpp/
│   ├── SwapSchedule.hpp
│   ├── SwapSchedule.cpp
│   ├── BermudanSwaption.hpp
│   ├── BermudanSwaption.cpp
│   ├── HullWhiteTree.hpp
│   ├── HullWhiteTree.cpp
│   ├── TreePricer.hpp
│   ├── TreePricer.cpp
│   └── main.cpp
│
├── tests/
│   ├── test_tree.py
│   └── test_bermudan.py
│
├── notebooks/
│   └── 11_bermudan_swaption_tree_pricing.ipynb
│
└── README.md
```

## Relationship to Previous Chapters

This chapter reuses several components developed earlier.

```text
Yield Curve
        ↓
Hull-White Model
        ↓
Zero-Coupon Bond Pricing
        ↓
Hull-White Tree
        ↓
Bermudan Swaption Pricing
```

The following modules are reused without modification:

- YieldCurve
- Market data loader
- HullWhiteModel
- Zero-coupon bond pricing

---

# 11.2 Bermudan Swaption Definition

The implementation follows the market convention.

If the option is exercised at time

$$
t,
$$

the holder enters into a new interest-rate swap beginning immediately at

$$
t
$$

and ending at

$$
t + \text{swap tenor}.
$$

For example,

```text
Option exercise dates:

1Y
2Y
3Y
4Y
5Y

Swap tenor:

5Y
```

implies

```text
Exercise at 1Y
↓

1Y → 6Y swap

----------------

Exercise at 2Y
↓

2Y → 7Y swap

----------------

Exercise at 5Y
↓

5Y → 10Y swap
```

Each exercise date therefore has its own payment schedule.

---

# 11.3 Underlying Swap Value

The underlying payer swap value is

$$
V_{\text{swap}} =
N
A(t)
\left(
S(t)-K
\right),
$$

where

- \(N\) is the notional,
- \(K\) is the fixed rate,
- \(S(t)\) is the forward swap rate,
- \(A(t)\) is the fixed-leg annuity.

The annuity is

$$
A(t) =
\sum_i
\Delta_i
P(t,T_i),
$$

and the forward swap rate is

$$
S(t) =
\frac{
1-P(t,T_N)
}{
A(t)
}.
$$

The immediate exercise value is therefore

$$
E(t,r) =
\max
\left(
V_{\text{swap}},
0
\right).
$$

---

# 11.4 Hull-White Tree

The short-rate process follows

$$
dr_t =
\left(
\theta(t)-ar_t
\right)dt
+
\sigma dW_t.
$$

This chapter uses an educational recombining binomial approximation.

The short-rate node is

$$
r(i,j) =
r_0
+
(2j-i)\Delta r,
$$

where

- $i$ is the time step,
- $j$ is the node index,
- $\Delta r$ is the node spacing.

The node spacing is

$$
\Delta r =
\sigma
\sqrt{\Delta t}.
$$

---

# 11.5 Why Is Node Spacing Only σ√Δt?

A common question is why the node spacing is

$$
\Delta r =
\sigma\sqrt{\Delta t}
$$

instead of

$$
(\theta-ar)\Delta t
+
\sigma\sqrt{\Delta t}.
$$

The reason is that the tree separates variance and drift.

The node spacing controls the local variance,

$$
Var(\Delta r) =
\sigma^2
\Delta t,
$$

while the Hull-White drift is incorporated through the transition probability.

The expected tree movement satisfies

$$
E[\Delta r] =
(2p-1)\Delta r =
(\theta-ar)\Delta t,
$$

which leads to

$$
p =
\frac12
+
\frac{
(\theta-ar)\Delta t
}{
2\Delta r
}.
$$

Thus,

```text
Node spacing
↓

Variance

Transition probability
↓

Drift
```

This separation preserves a recombining tree.

---

# 11.6 Backward Induction

Pricing proceeds backward through the tree.

At each node,

the continuation value is

$$
C(t,r) =
e^{-r\Delta t}
\left[
pV_u
+
(1-p)V_d
\right].
$$

If the node is an exercise date,

the option value becomes

$$
V(t,r) =
\max
\left(
E(t,r),
C(t,r)
\right).
$$

Otherwise,

$$
V(t,r) =
C(t,r).
$$

---

# 11.7 Four Trees Stored During Pricing

Unlike production implementations that often keep only the option value tree, this educational implementation stores four trees.

## Option Value Tree

$$
V(t,r)
$$

Stores the final option value after comparing exercise and continuation.



## Exercise Value Tree

$$
E(t,r)
$$

Stores the immediate exercise value.



## Continuation Value Tree

$$
C(t,r)
$$

Stores the discounted continuation value.


## Exercise Flag Tree

Stores a Boolean decision

```text
True
```

if

$$
E(t,r)
>
C(t,r),
$$

otherwise

```text
False.
```

This makes the exercise boundary easy to visualize and is particularly useful for teaching.

---

# 11.8 Implementation
## Python Implementation

The Python implementation includes

- Bermudan swaption definition
- dynamic payment schedule generation
- Hull-White tree construction
- backward induction
- exercise boundary visualization
- pricing diagnostics
- sensitivity analysis

## C++ Implementation

The C++ implementation mirrors the Python workflow.

It reuses

- YieldCurve
- HullWhiteModel
- ZeroCouponBondPricing

from previous chapters while implementing

- Bermudan swaption instrument
- Hull-White tree
- backward induction
- four-tree storage
- pricing example

The implementation intentionally avoids external libraries and is suitable for educational use.

---

# 11.9 Summary
## Educational vs Production Trees

This implementation is intentionally simplified.

Production Bermudan swaption models typically use

- Hull-White calibrated trinomial trees,
- state-price calibration,
- finite-difference methods,
- or Longstaff-Schwartz Monte Carlo.

The present implementation focuses on illustrating the early-exercise logic as clearly as possible.


## Practical Applications

Tree-based Bermudan pricing is widely used for

- Bermudan swaptions
- callable bonds
- callable swaps
- structured interest-rate products
- early-exercise interest-rate derivatives


## Key Lessons

1. Bermudan swaptions require optimal stopping.
2. Backward induction naturally solves the exercise decision.
3. Immediate exercise and continuation values are compared at every exercise node.
4. Node spacing controls local variance, while transition probabilities capture the Hull-White drift.
5. Storing separate exercise and continuation trees greatly improves model transparency and debugging.


## Next Chapter

The next chapter prices Bermudan swaptions using Longstaff-Schwartz Monte Carlo.

Instead of backward induction on a tree, the continuation value will be estimated through regression on simulated paths.

```text
Tree

↓

Dynamic Programming

===================

LSM

↓

Monte Carlo + Regression
```

Together, Chapters 11 and 12 provide two of the most widely used numerical approaches for pricing Bermudan-style interest-rate derivatives.
