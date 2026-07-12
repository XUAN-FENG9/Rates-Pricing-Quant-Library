# Chapter 13 — Gaussian LIBOR Market Model

## Forward-Curve Dynamics, Correlation, Monte Carlo Simulation, and Interest-Rate Option Pricing

This chapter develops a compact Gaussian LIBOR Market Model (LMM) for simulating an entire forward-rate curve and pricing caplets and European swaptions.

Unlike a short-rate model, which describes the evolution of a single instantaneous short rate, the LMM directly models a collection of market forward rates. This makes the framework especially natural for pricing products whose values depend on several future interest-rate periods.

The chapter contains:

- a tenor-based forward-rate representation;
- initial forward-rate construction from a zero curve;
- exponential cross-maturity correlation;
- principal-component factor reduction;
- deterministic Gaussian forward volatility;
- terminal-measure drift adjustment;
- Euler Monte Carlo simulation;
- discount-bond reconstruction;
- caplet pricing;
- European payer swaption pricing;
- strike, volatility, and correlation sensitivity analysis;
- equivalent Python and C++ implementations.

---

## 1. Chapter Objectives

After completing this chapter, the reader should understand:

1. what a LIBOR Market Model simulates;
2. how forward rates are constructed from discount factors;
3. why an LMM simulates a vector of forward rates instead of one short rate;
4. how volatility and correlation jointly determine forward-curve dynamics;
5. why the drift depends on the choice of probability measure;
6. how the terminal measure simplifies joint forward-rate simulation;
7. how simulated forward curves are converted back into discount bonds;
8. how caplets and swaptions are priced by Monte Carlo;
9. how the Python and C++ implementations correspond to the model equations.

---

## 2. Project Structure

```text
13_gaussian_libor_market_model_lmm/
├── README.md
├── usd_zero_curve.csv
│
├── notebooks/
│   └── 13_gaussian_lmm.ipynb
│
├── python/
│   ├── market_data.py
│   ├── tenor_structure.py
│   ├── correlation.py
│   ├── volatility.py
│   ├── gaussian_lmm.py
│   ├── simulation.py
│   ├── pricing.py
│   ├── plotting.py
│   └── diagnostics.py
│
├── tests/
│   ├── test_tenor_structure.py
│   ├── test_lmm_simulation.py
│   └── test_lmm_pricing.py
│
└── cpp/
    ├── Matrix.hpp
    ├── ZeroCurve.hpp
    ├── ZeroCurve.cpp
    ├── TenorStructure.hpp
    ├── TenorStructure.cpp
    ├── Correlation.hpp
    ├── Correlation.cpp
    ├── GaussianLMMVolatility.hpp
    ├── GaussianLMMVolatility.cpp
    ├── GaussianLMM.hpp
    ├── GaussianLMM.cpp
    ├── LMMSimulation.hpp
    ├── LMMSimulation.cpp
    ├── LMMPricing.hpp
    ├── LMMPricing.cpp
    ├── Diagnostics.hpp
    ├── Diagnostics.cpp
    └── main.cpp
```

---

## 3. From Short-Rate Models to the LMM

A short-rate model starts from one state variable:

$$
r_t.
$$

From the short rate, the model derives discount factors, zero rates, forward rates, and derivative prices.

Examples include:

- Vasicek;
- Hull–White;
- Cox–Ingersoll–Ross;
- Black–Karasinski.

The LIBOR Market Model takes a different approach. It directly models a collection of discrete forward rates:

$$
L_0(t),L_1(t),\ldots,L_{N-1}(t).
$$

Each forward rate corresponds to one tenor interval:

$$
[T_i,T_{i+1}].
$$

The state vector is therefore:

$$
\mathbf{L}(t)
=
\left(
L_0(t),
L_1(t),
\ldots,
L_{N-1}(t)
\right).
$$

This is particularly useful for pricing products such as:

- caplets;
- caps;
- floorlets;
- floors;
- swaptions;
- callable swaps;
- Bermudan swaptions;
- structured interest-rate products.

---

## 4. Tenor Structure

Let the tenor grid be:

$$
0=T_0<T_1<\cdots<T_N.
$$

For a semiannual tenor structure:

```text
T0 = 0.0
T1 = 0.5
T2 = 1.0
T3 = 1.5
...
TN = 10.0
```

The accrual period for interval \(i\) is:

$$
\delta_i=T_{i+1}-T_i.
$$

With semiannual periods:

$$
\delta_i=0.5.
$$

The forward rate \(L_i(t)\) applies to the borrowing or lending interval:

$$
[T_i,T_{i+1}].
$$

For example:

```text
L0(t): forward rate for 0.0Y to 0.5Y
L1(t): forward rate for 0.5Y to 1.0Y
L2(t): forward rate for 1.0Y to 1.5Y
L3(t): forward rate for 1.5Y to 2.0Y
```

A tenor grid with 21 dates contains 20 forward rates.

---

## 5. Forward Rates and Discount Factors

Let:

$$
P(t,T)
$$

denote the time-\(t\) price of a zero-coupon bond paying one unit at maturity \(T\).

The simple-compounded forward rate for interval \([T_i,T_{i+1}]\) is defined by:

$$
1+\delta_iL_i(t)
=
\frac{P(t,T_i)}{P(t,T_{i+1})}.
$$

Therefore:

$$
L_i(t)
=
\frac{1}{\delta_i}
\left[
\frac{P(t,T_i)}{P(t,T_{i+1})}
-
1
\right].
$$

At time zero:

$$
L_i(0)
=
\frac{1}{\delta_i}
\left[
\frac{P(0,T_i)}{P(0,T_{i+1})}
-
1
\right].
$$

This means the initial forward curve is fully determined by the initial discount curve.

The implementation therefore follows:

```text
Zero rates
    ↓
Discount factors
    ↓
Initial forward rates
```

---

## 6. Interpretation of \(L_i(t)\)

The notation \(L_i(t)\) contains two different time concepts.

### Observation time

The variable \(t\) is the time at which the market is observed.

For example:

$$
t=2.
$$

means that the simulated economy has advanced to year 2.

### Forward interval

The index \(i\) identifies the future interval:

$$
[T_i,T_{i+1}].
$$

For example:

$$
L_4(2)
$$

may represent the forward rate observed at time 2 for the period:

$$
[2.0,2.5].
$$

Similarly:

$$
L_8(2)
$$

may represent the forward rate observed at time 2 for the period:

$$
[4.0,4.5].
$$

Therefore:

> \(t\) tells us when the forward curve is observed, while \(i\) tells us which future borrowing interval is being measured.

---

## 7. The Forward Curve at a Future Time

At time zero, the model stores:

$$
\left[
L_0(0),
L_1(0),
\ldots,
L_{N-1}(0)
\right].
$$

At a future time such as \(t=2\), one Monte Carlo path contains:

$$
\left[
L_0(2),
L_1(2),
\ldots,
L_{N-1}(2)
\right].
$$

This is the full forward-rate state stored by the program at time 2.

However, forwards whose reset dates are before or equal to time 2 have already fixed. They remain in the array to preserve a constant data structure, but they no longer evolve.

For a semiannual grid:

```text
L0: 0.0Y to 0.5Y
L1: 0.5Y to 1.0Y
L2: 1.0Y to 1.5Y
L3: 1.5Y to 2.0Y
L4: 2.0Y to 2.5Y
L5: 2.5Y to 3.0Y
...
```

At \(t=2\):

- \(L_0\) to \(L_3\) belong to past periods;
- \(L_4\) is fixing at time 2;
- \(L_5,L_6,\ldots\) remain future forward rates.

The code stores all positions, but only the relevant future segment is used for pricing.

---

## 8. Gaussian LMM Dynamics

A classical lognormal LMM is often written as:

$$
dL_i(t)
=
\mu_i(t)L_i(t)\,dt
+
L_i(t)\lambda_i(t)\cdot dW_t.
$$

The diffusion term is proportional to the forward-rate level.

This chapter instead uses an additive Gaussian LMM:

$$
dL_i(t)
=
\mu_i(t)\,dt
+
\lambda_i(t)\cdot dW_t.
$$

The diffusion is additive rather than multiplicative.

The Gaussian model is convenient because:

- it is simple to implement;
- it naturally permits negative forward rates;
- it connects to normal-volatility and Bachelier-style pricing;
- it provides a clean introduction to multi-forward modeling;
- the relationship between factor loadings and covariance is transparent.

The main limitation is that the Gaussian model does not enforce positive rates.

---

## 9. Volatility Structure

For each forward \(L_i\), the deterministic normal volatility is modeled as:

$$
\sigma_i(t)
=
\sigma_{\text{level}}
\exp
\left[
-d(T_i-t)
\right],
\qquad t<T_i.
$$

Here:

- \(\sigma_{\text{level}}\) controls the overall volatility level;
- \(d\) controls maturity decay;
- \(T_i-t\) is the remaining time to reset.

After the reset date:

$$
\sigma_i(t)=0,
\qquad t\ge T_i.
$$

This reflects the fact that once the forward rate has fixed, it should no longer evolve randomly.

A volatility floor may also be imposed:

$$
\sigma_i(t)
=
\max
\left[
\sigma_{\text{level}}
e^{-d(T_i-t)},
\sigma_{\text{floor}}
\right].
$$

The floor applies only before reset.

---

## 10. Interpreting Gaussian Volatility

In a Gaussian LMM, volatility is expressed in absolute rate units.

For example:

```text
sigma_level = 0.01
```

means approximately:

```text
1 percentage point
=
100 basis points
```

of annualized normal volatility.

This is different from a lognormal model, where volatility is interpreted as a percentage of the forward-rate level.

---

## 11. Correlation Across Forward Rates

Forward rates at different maturities are not independent.

Nearby maturities often move together because they are influenced by common economic and monetary-policy shocks.

The chapter uses exponential correlation:

$$
\rho_{ij}
=
\exp
\left[
-\beta|T_i-T_j|
\right].
$$

The parameter \(\beta\) controls how rapidly correlation declines with maturity distance.

### Small \(\beta\)

A small value produces persistent correlation across the curve.

```text
Nearby forwards: highly correlated
Distant forwards: still substantially correlated
```

### Large \(\beta\)

A large value produces faster correlation decay.

```text
Nearby forwards: correlated
Distant forwards: much less correlated
```

The diagonal satisfies:

$$
\rho_{ii}=1.
$$

---

## 12. Pairwise Distance Matrix

In Python, the distance matrix is constructed by:

```python
distances = np.abs(
    reset_times[:, None]
    -
    reset_times[None, :]
)
```

If:

```python
reset_times = np.array(
    [0.5, 1.0, 1.5]
)
```

then:

```python
reset_times[:, None]
```

creates a column vector:

```text
[[0.5],
 [1.0],
 [1.5]]
```

and:

```python
reset_times[None, :]
```

creates a row vector:

```text
[[0.5, 1.0, 1.5]]
```

Broadcasting produces all pairwise differences:

```text
[[0.0, 0.5, 1.0],
 [0.5, 0.0, 0.5],
 [1.0, 0.5, 0.0]]
```

The corresponding correlation matrix is then:

$$
\rho_{ij}=e^{-\beta d_{ij}}.
$$

---

## 13. From Correlation to Correlated Shocks

Suppose:

$$
Z\sim N(0,I).
$$

If the correlation matrix satisfies:

$$
\rho=CC^\top,
$$

then:

$$
\varepsilon=CZ
$$

has covariance:

$$
\operatorname{Cov}(\varepsilon)
=
CC^\top
=
\rho.
$$

A Cholesky decomposition can therefore be used to generate correlated shocks.

The project also includes a numerically stable Cholesky routine that adds a small diagonal jitter when required.

---

## 14. Principal-Component Factor Reduction

A model with 20 forward rates could use 20 Brownian factors.

However, yield-curve movements are usually dominated by a small number of common directions:

1. level;
2. slope;
3. curvature.

The correlation matrix is decomposed as:

$$
\rho
=
Q\Lambda Q^\top.
$$

Keeping the largest \(m\) eigenvalues gives:

$$
B
=
Q_m\Lambda_m^{1/2}.
$$

Then:

$$
BB^\top
\approx
\rho.
$$

With 20 forward rates and 3 factors:

```text
Correlation matrix:
20 × 20

PCA loading matrix:
20 × 3
```

Each row of the loading matrix describes how one forward rate responds to the three common curve factors.

---

## 15. Combining Volatility and Correlation

Let:

$$
b_i
$$

denote the PCA loading vector for forward \(i\).

The final factor-loading vector is:

$$
\lambda_i(t)
=
\sigma_i(t)b_i.
$$

For a three-factor model:

$$
\lambda_i(t)
=
\left(
\lambda_{i1}(t),
\lambda_{i2}(t),
\lambda_{i3}(t)
\right).
$$

The instantaneous covariance between forward rates \(i\) and \(j\) is:

$$
\operatorname{Cov}
\left(
dL_i(t),
dL_j(t)
\right)
=
\lambda_i(t)\cdot\lambda_j(t)\,dt.
$$

The instantaneous covariance matrix is:

$$
\Sigma(t)
=
\Lambda(t)\Lambda(t)^\top.
$$

---

## 16. Why the Drift Depends on the Measure

A forward rate is naturally driftless under its own forward measure.

However, a joint simulation cannot conveniently simulate every forward under a different measure.

The chapter uses one common measure for all forward rates: the terminal measure associated with the final tenor date \(T_N\).

The numeraire is:

$$
N(t)=P(t,T_N).
$$

Under the terminal measure \(Q^{T_N}\), all forward rates can be simulated together, but their drift terms must be adjusted.

---

## 17. Terminal-Measure Dynamics

Under the terminal measure:

$$
dL_i(t)
=
\mu_i^{T_N}(t)\,dt
+
\lambda_i(t)\cdot dW_t^{T_N}.
$$

For the additive Gaussian LMM, the terminal-measure drift is:

$$
\mu_i^{T_N}(t)
=
-
\sum_{j=i+1}^{N-1}
\frac{
\delta_j
\lambda_i(t)\cdot\lambda_j(t)
}{
1+\delta_jL_j(t)
}.
$$

This formula shows that the drift of forward \(i\) depends on:

- later forward rates;
- accrual periods;
- cross-forward covariance;
- the current forward-curve state;
- the selected terminal numeraire.

The final forward has zero drift because there are no later forwards:

$$
\mu_{N-1}^{T_N}(t)=0.
$$

This is an important diagnostic check.

---

## 18. Active and Fixed Forward Rates

Forward \(L_i\) remains stochastic only before its reset date.

The active condition is:

$$
t<T_i.
$$

Once:

$$
t\ge T_i,
$$

the forward is fixed and its volatility is set to zero.

The program preserves the full forward vector at every time point, but fixed forwards stop changing.

This fixed-size representation simplifies:

- storage;
- path simulation;
- indexing;
- pricing;
- diagnostics.

---

## 19. Euler Discretization

The continuous-time dynamics are approximated using Euler discretization:

$$
L_i(t+\Delta t)
=
L_i(t)
+
\mu_i(t)\Delta t
+
\lambda_i(t)\cdot Z\sqrt{\Delta t},
$$

where:

$$
Z\sim N(0,I).
$$

In vector form:

$$
\mathbf{L}_{t+\Delta t}
=
\mathbf{L}_t
+
\boldsymbol{\mu}_t\Delta t
+
\Lambda_tZ\sqrt{\Delta t}.
$$

If:

```text
Lambda shape = number of forwards × number of factors
Z shape      = number of factors
```

then:

```text
Lambda × Z
```

produces one diffusion shock for every forward rate.

---

## 20. Monte Carlo Path Structure

The simulation stores:

```text
path × time × forward
```

In Python:

```python
forward_paths[path_index, time_index, forward_index]
```

In C++:

```cpp
forwardPaths[pathIndex][timeIndex][forwardIndex]
```

For example:

```text
5000 paths
101 simulation times
20 forward rates
```

produces:

```text
5000 × 101 × 20
```

values.

A useful interpretation is:

```text
5000 books
101 pages per book
20 forward rates on every page
```

- one book is one Monte Carlo path;
- one page is one simulation time;
- one row of 20 numbers is the forward curve at that time.

---

## 21. Slicing the Three-Dimensional Path Array

### Fix one path

```cpp
forwardPaths[pathIndex]
```

returns:

```text
time × forward
```

This is the complete evolution of one simulated forward curve.

### Fix one path and one time

```cpp
forwardPaths[pathIndex][timeIndex]
```

returns:

```text
forward
```

This is the complete forward curve on one path at one time.

### Fix one path, one time, and one forward

```cpp
forwardPaths[pathIndex][timeIndex][forwardIndex]
```

returns one number:

$$
L_i(t).
$$

---

## 22. Meaning of “Take the Forward Curve at \(t=2\)”

Suppose the simulation time step is:

$$
\Delta t=0.05.
$$

Then time index 40 corresponds to:

$$
40\times0.05=2.
$$

The C++ expression:

```cpp
simulation.forwardPaths[path][40]
```

returns the entire stored forward vector on that path at time 2:

$$
\left[
L_0(2),
L_1(2),
\ldots,
L_{N-1}(2)
\right].
$$

This does not mean one single “2-year forward rate.”

It means:

> the complete forward-rate state observed when the simulated economy reaches year 2.

A caplet may use one component of this curve.

A swaption uses several components.

---

## 23. Antithetic Variates

To reduce Monte Carlo noise, the simulation may pair each shock \(Z\) with \(-Z\).

For example:

```text
Path A:
[0.8, -0.3, 1.2]

Path B:
[-0.8, 0.3, -1.2]
```

The estimator remains unbiased, while symmetric simulation noise may partially cancel.

The C++ call:

```cpp
simulateGaussianLMM(
    model,
    5.0,
    100,
    5000,
    42,
    true
);
```

uses:

```text
simulation horizon = 5 years
time steps         = 100
paths              = 5000
random seed        = 42
antithetic         = true
```

---

## 24. Reconstructing Discount Bonds

At a tenor date \(T_k\):

$$
P(T_k,T_k)=1.
$$

The forward relation gives:

$$
P(T_k,T_{j+1})
=
\frac{
P(T_k,T_j)
}{
1+\delta_jL_j(T_k)
}.
$$

Therefore:

$$
P(T_k,T_j)
=
\prod_{m=k}^{j-1}
\frac{1}{
1+\delta_mL_m(T_k)
}.
$$

This reconstruction converts a simulated forward curve into discount-bond prices.

The condition:

$$
1+\delta_iL_i(t)>0
$$

must hold to ensure valid positive bond prices.

---

## 25. Swap Annuity

Consider a swap beginning at \(T_k\) and ending at \(T_m\).

The fixed-leg annuity is:

$$
A(T_k)
=
\sum_{j=k}^{m-1}
\delta_jP(T_k,T_{j+1}).
$$

The annuity is the present value of one unit of fixed coupon paid on each payment date.

---

## 26. Par Swap Rate

The value of the floating leg at the swap start date is:

$$
1-P(T_k,T_m).
$$

The par swap rate is therefore:

$$
S(T_k)
=
\frac{
1-P(T_k,T_m)
}{
A(T_k)
}.
$$

This is the fixed rate that makes the swap value equal to zero at \(T_k\).

---

## 27. Terminal-Numeraire Pricing

The general numeraire pricing identity is:

$$
V(0)
=
N(0)
\mathbb{E}^{N}
\left[
\frac{V(T)}{N(T)}
\right].
$$

With terminal bond numeraire:

$$
N(t)=P(t,T_N),
$$

the pricing formula becomes:

$$
V(0)
=
P(0,T_N)
\mathbb{E}^{T_N}
\left[
\frac{
V(T)
}{
P(T,T_N)
}
\right].
$$

In Monte Carlo form:

$$
V(0)
\approx
P(0,T_N)
\frac{1}{M}
\sum_{p=1}^{M}
\frac{
V^{(p)}(T)
}{
P^{(p)}(T,T_N)
}.
$$

This explains why the pricing code divides each path payoff by the terminal bond and then multiplies the average by the initial terminal discount factor.

---

## 28. Caplet Pricing

A caplet on \(L_i\) fixes at \(T_i\) and pays at \(T_{i+1}\).

The payment is:

$$
N\delta_i
\max
\left(
L_i(T_i)-K,
0
\right),
$$

where:

- \(N\) is the notional;
- \(K\) is the strike;
- \(\delta_i\) is the accrual period.

Because the payment occurs at \(T_{i+1}\), its value at the reset date \(T_i\) is:

$$
V(T_i)
=
\frac{
N\delta_i
\max(L_i(T_i)-K,0)
}{
1+\delta_iL_i(T_i)
}.
$$

The time-zero value is:

$$
V(0)
=
P(0,T_N)
\mathbb{E}^{T_N}
\left[
\frac{
V(T_i)
}{
P(T_i,T_N)
}
\right].
$$

Although the caplet payoff depends on one forward rate, the complete forward curve is still used to reconstruct the terminal bond.

---

## 29. European Payer Swaption Pricing

A payer swaption gives the holder the right to:

```text
pay fixed
receive floating
```

Suppose the option expires at \(T_k\), and the underlying swap ends at \(T_m\).

The expiry payoff is:

$$
N A(T_k)
\max
\left(
S(T_k)-K,
0
\right).
$$

For each simulated path:

1. take the forward curve at expiry;
2. reconstruct discount bonds;
3. calculate the swap annuity;
4. calculate the par swap rate;
5. calculate the payer payoff;
6. divide by the terminal bond;
7. average across paths;
8. multiply by \(P(0,T_N)\).

The Monte Carlo price is:

$$
V(0)
\approx
P(0,T_N)
\frac{1}{M}
\sum_{p=1}^{M}
\frac{
N A^{(p)}(T_k)
\max
\left(
S^{(p)}(T_k)-K,
0
\right)
}{
P^{(p)}(T_k,T_N)
}.
$$

---

## 30. Why a Swaption Uses Several Forward Rates

A caplet depends mainly on one forward rate.

A swaption depends on a complete segment of the forward curve.

For a 2Y expiry and a 2Y-to-7Y underlying swap, the required forwards are approximately:

```text
2.0Y to 2.5Y
2.5Y to 3.0Y
3.0Y to 3.5Y
...
6.5Y to 7.0Y
```

These forwards determine:

- discount factors from 2Y to 7Y;
- the swap annuity;
- the par swap rate;
- the swaption payoff.

This is why correlation is particularly important for swaption pricing.

---

## 31. Python Module Responsibilities

### `market_data.py`

Loads the initial zero curve and creates a curve object.

Main responsibilities:

- read CSV data;
- validate maturity and rate columns;
- construct the initial yield curve;
- export selected curve points for inspection.

---

### `tenor_structure.py`

Creates the tenor grid and accrual periods.

Main responsibilities:

- build \(T_0,\ldots,T_N\);
- calculate \(\delta_i\);
- construct initial forward rates;
- construct initial discount factors;
- map calendar times to tenor indices.

---

### `correlation.py`

Builds the forward-rate correlation structure.

Main responsibilities:

- exponential correlation matrix;
- pairwise maturity-distance matrix;
- stable Cholesky decomposition;
- PCA factor reduction.

---

### `volatility.py`

Defines deterministic Gaussian forward volatility.

Main responsibilities:

- calculate \(\sigma_i(t)\);
- turn volatility off after reset;
- combine volatility with correlation loadings.

---

### `gaussian_lmm.py`

Contains the core LMM dynamics.

Main responsibilities:

- active-forward identification;
- factor-loading calculation;
- instantaneous covariance;
- terminal-measure drift;
- Euler evolution;
- discount-factor reconstruction;
- terminal-bond calculation.

---

### `simulation.py`

Generates Monte Carlo forward-rate paths.

Main responsibilities:

- create the simulation time grid;
- generate Gaussian factor shocks;
- apply antithetic variates;
- repeatedly call the model evolution function;
- store the three-dimensional path array.

---

### `pricing.py`

Prices interest-rate options.

Main responsibilities:

- reconstruct discount bonds;
- compute swap annuity and par swap rate;
- price caplets;
- price European payer swaptions;
- apply terminal-numeraire pricing.

---

### `plotting.py`

Creates graphical diagnostics.

Typical plots:

- initial forward curve;
- correlation matrix;
- selected forward-rate paths;
- terminal forward distributions;
- mean forward surface;
- strike and volatility sensitivity.

---

### `diagnostics.py`

Provides model checks and summary tables.

Typical diagnostics:

- forward-curve table;
- correlation-matrix checks;
- simulation moments;
- drift checks;
- pricing summaries.

---

## 32. C++ Module Responsibilities

### `Matrix.hpp`

Defines the common matrix type:

```cpp
using Matrix =
    std::vector<
        std::vector<double>
    >;
```

---

### `ZeroCurve.hpp` and `ZeroCurve.cpp`

Implement:

- zero-rate interpolation;
- discount-factor calculation.

---

### `TenorStructure.hpp` and `TenorStructure.cpp`

Implement:

- tenor-grid construction;
- accrual periods;
- initial forward rates;
- initial discount factors;
- tenor indexing.

---

### `Correlation.hpp` and `Correlation.cpp`

Implement:

- exponential correlation;
- Cholesky decomposition;
- PCA factor reduction;
- matrix multiplication;
- matrix transpose.

---

### `GaussianLMMVolatility.hpp` and `GaussianLMMVolatility.cpp`

Implement:

- deterministic Gaussian volatility;
- volatility decay;
- reset-date deactivation;
- final factor loadings.

---

### `GaussianLMM.hpp` and `GaussianLMM.cpp`

Implement:

- model validation;
- active-forward masks;
- factor loadings;
- covariance matrices;
- terminal-measure drift;
- Euler evolution;
- bond reconstruction;
- terminal-bond calculation.

---

### `LMMSimulation.hpp` and `LMMSimulation.cpp`

Implement:

- simulation result structure;
- time-grid construction;
- random-number generation;
- antithetic shocks;
- path evolution.

---

### `LMMPricing.hpp` and `LMMPricing.cpp`

Implement:

- discount-bond reconstruction;
- swap annuity;
- par swap rate;
- caplet pricing;
- payer swaption pricing.

---

### `Diagnostics.hpp` and `Diagnostics.cpp`

Implement console output for:

- initial forward curve;
- correlation summary;
- simulation summary;
- pricing results.

---

### `main.cpp`

Coordinates the full workflow:

```text
1. Build the zero curve
2. Build the tenor structure
3. Construct initial forward rates
4. Construct the correlation matrix
5. Reduce correlation to three factors
6. Build the volatility model
7. Build the Gaussian LMM
8. Inspect terminal-measure drift
9. Run Monte Carlo simulation
10. Price a caplet
11. Price a payer swaption
12. Run sensitivity analysis
```

---

## 33. Minimal Python Workflow

```python
import sys
from pathlib import Path

PROJECT_ROOT = Path(
    r"C:\Users\YourName\Desktop\Rates-Pricing-Quant-Library"
)

CHAPTER13 = (
    PROJECT_ROOT
    /
    "13_gaussian_libor_market_model_lmm"
)

sys.path.append(
    str(
        CHAPTER13
        /
        "python"
    )
)

from market_data import load_curve_data
from tenor_structure import TenorStructure
from correlation import (
    exponential_correlation_matrix,
    principal_component_loadings
)
from volatility import GaussianLMMVolatility
from gaussian_lmm import GaussianLMM
from simulation import simulate_gaussian_lmm
from pricing import (
    price_caplet_mc,
    price_payer_swaption_mc
)

curve = load_curve_data(
    CHAPTER13
    /
    "usd_zero_curve.csv"
)

tenor = TenorStructure(
    start=0.0,
    end=10.0,
    payment_frequency=2
)

initial_forwards = tenor.initial_forward_rates(
    curve
)

initial_discount_factors = tenor.initial_discount_factors(
    curve
)

correlation_matrix = exponential_correlation_matrix(
    tenor.times[:-1],
    beta=0.10
)

correlation_loadings = principal_component_loadings(
    correlation_matrix,
    n_factors=3
)

volatility_model = GaussianLMMVolatility(
    reset_times=tenor.times[:-1],
    sigma_level=0.01,
    decay=0.05,
    floor=0.001
)

model = GaussianLMM(
    tenor_structure=tenor,
    initial_forwards=initial_forwards,
    volatility_model=volatility_model,
    correlation_loadings=correlation_loadings,
    initial_discount_factors=initial_discount_factors
)

times, forward_paths = simulate_gaussian_lmm(
    model=model,
    simulation_end=5.0,
    n_steps=100,
    n_paths=5000,
    seed=42,
    antithetic=True
)

caplet_price = price_caplet_mc(
    model=model,
    times=times,
    forward_paths=forward_paths,
    reset_time=2.0,
    strike=0.045,
    notional=1_000_000
)

swaption_price = price_payer_swaption_mc(
    model=model,
    times=times,
    forward_paths=forward_paths,
    expiry=2.0,
    swap_end=7.0,
    strike=0.045,
    notional=1_000_000
)

print(
    "Caplet price:",
    caplet_price
)

print(
    "Payer swaption price:",
    swaption_price
)
```

---

## 34. Minimal C++ Workflow

```cpp
#include <iostream>
#include <vector>

#include "Matrix.hpp"
#include "ZeroCurve.hpp"
#include "TenorStructure.hpp"
#include "Correlation.hpp"
#include "GaussianLMMVolatility.hpp"
#include "GaussianLMM.hpp"
#include "LMMSimulation.hpp"
#include "LMMPricing.hpp"

int main(){

    std::vector<double> maturities = {
        0.0,
        0.5,
        1.0,
        2.0,
        3.0,
        5.0,
        7.0,
        10.0
    };

    std::vector<double> zeroRates = {
        0.0450,
        0.0455,
        0.0458,
        0.0460,
        0.0458,
        0.0450,
        0.0443,
        0.0435
    };

    ZeroCurve curve(
        maturities,
        zeroRates
    );

    TenorStructure tenor(
        0.0,
        10.0,
        2
    );

    std::vector<double> initialForwards =
        tenor.initialForwardRates(
            curve
        );

    std::vector<double> initialDiscountFactors =
        tenor.initialDiscountFactors(
            curve
        );

    std::vector<double> resetTimes(
        tenor.times().begin(),
        tenor.times().end() - 1
    );

    Matrix correlationMatrix =
        exponentialCorrelationMatrix(
            resetTimes,
            0.10
        );

    Matrix correlationLoadings =
        principalComponentLoadings(
            correlationMatrix,
            3
        );

    GaussianLMMVolatility volatilityModel(
        resetTimes,
        0.01,
        0.05,
        0.001
    );

    GaussianLMM model(
        tenor,
        initialForwards,
        volatilityModel,
        correlationLoadings,
        initialDiscountFactors
    );

    LMMSimulationResult simulation =
        simulateGaussianLMM(
            model,
            5.0,
            100,
            5000,
            42,
            true
        );

    double capletPrice =
        priceCapletMonteCarlo(
            model,
            simulation,
            2.0,
            0.045,
            1000000.0
        );

    double swaptionPrice =
        pricePayerSwaptionMonteCarlo(
            model,
            simulation,
            2.0,
            7.0,
            0.045,
            1000000.0
        );

    std::cout
        << "Caplet price: "
        << capletPrice
        << std::endl;

    std::cout
        << "Payer swaption price: "
        << swaptionPrice
        << std::endl;

    return 0;
}
```

---

## 35. C++ Compilation

From the `cpp` directory:

```bash
g++ -std=c++17 ZeroCurve.cpp TenorStructure.cpp Correlation.cpp GaussianLMMVolatility.cpp GaussianLMM.cpp LMMSimulation.cpp LMMPricing.cpp Diagnostics.cpp main.cpp -O2 -o gaussian_lmm_demo.exe
```

Run:

```bash
gaussian_lmm_demo.exe
```

In Code::Blocks, add all `.cpp` files to the project and then use:

```text
Build
→ Clean

Build
→ Rebuild
```

---

## 36. Python Tests

Run from the project root:

```bash
pytest 13_gaussian_libor_market_model_lmm/tests -v
```

The tests cover:

- initial forward-rate construction;
- tenor-grid consistency;
- simulation dimensions;
- last-forward drift;
- caplet pricing;
- swaption pricing;
- basic monotonicity properties.

---

## 37. Important Model Checks

### Initial curve consistency

Forward rates reconstructed from discount factors should reproduce the original discount curve.

### Last-forward drift

Under the terminal measure:

$$
\mu_{N-1}^{T_N}=0.
$$

### Positive discount recursion

For every active forward:

$$
1+\delta_iL_i(t)>0.
$$

### Strike monotonicity

For payer options:

```text
higher strike
→ lower option value
```

### Volatility monotonicity

In general:

```text
higher volatility
→ higher option value
```

### Simulation convergence

Increasing the number of paths should stabilize the Monte Carlo price.

---

## 38. Strike Sensitivity

For a payer caplet or payer swaption:

$$
\max(X-K,0)
$$

decreases as \(K\) increases.

Therefore:

```text
Low strike
→ high payer option value

High strike
→ low payer option value
```

The implementation evaluates several strikes using the same simulated paths, which reduces noise in the comparison.

---

## 39. Volatility Sensitivity

Higher Gaussian volatility increases the dispersion of future forward rates.

Because option payoffs are convex:

$$
\mathbb{E}
\left[
\max(X-K,0)
\right]
$$

generally increases with volatility.

The chapter rebuilds and resimulates the model for several values of:

```text
sigma_level
```

and compares caplet and swaption prices.

---

## 40. Correlation Sensitivity

Correlation is especially important for swaptions.

A swap rate depends on multiple forwards, so the joint movement of these forwards affects the variance of the swap rate.

The exponential correlation parameter is:

$$
\beta.
$$

Smaller \(\beta\) means stronger long-range correlation.

Larger \(\beta\) means faster correlation decay.

The pricing impact depends on:

- swap maturity;
- curve shape;
- volatility term structure;
- factor truncation;
- strike;
- option expiry.

---

## 41. Numerical and Modeling Limitations

This chapter is an educational implementation, not a production front-office system.

Main limitations include:

1. additive Gaussian dynamics;
2. deterministic volatility;
3. exponential correlation;
4. approximate PCA factor reduction;
5. Euler discretization;
6. no market calibration;
7. no volatility smile;
8. no stochastic volatility;
9. no displaced diffusion;
10. no predictor-corrector scheme;
11. no adjoint differentiation;
12. no calibration to caplet or swaption volatility surfaces.

---

## 42. Production Extensions

A more advanced LMM implementation may include:

- shifted-lognormal dynamics;
- displaced diffusion;
- predictor-corrector simulation;
- frozen-drift approximation;
- caplet-volatility calibration;
- swaption-volatility calibration;
- stochastic volatility;
- SABR-style smile dynamics;
- local volatility;
- stochastic correlation;
- Bermudan swaption pricing;
- regression-based early exercise;
- GPU or parallel Monte Carlo;
- automatic differentiation;
- full risk and Greek calculation.

---

## 43. Key Conceptual Takeaways

### The LMM simulates forward rates directly

The state variables are:

$$
L_0(t),L_1(t),\ldots,L_{N-1}(t).
$$

### One simulation time contains a complete forward curve

At time \(t\), each path stores:

$$
\left[
L_0(t),L_1(t),\ldots,L_{N-1}(t)
\right].
$$

### Volatility and correlation have different roles

```text
Volatility:
how much each forward moves

Correlation:
how different forwards move together
```

### The drift depends on the measure

Using the terminal measure makes joint simulation possible, but introduces the terminal-measure drift correction.

### Caplets and swaptions use the curve differently

```text
Caplet:
mainly one fixing forward

Swaption:
a complete segment of the future forward curve
```

### Forward curves reconstruct discount bonds

The relationship:

$$
1+\delta_iL_i(t)
=
\frac{P(t,T_i)}{P(t,T_{i+1})}
$$

connects the simulated forward state to bond prices.

### Terminal-numeraire pricing is essential

Under \(Q^{T_N}\):

$$
V(0)
=
P(0,T_N)
\mathbb{E}^{T_N}
\left[
\frac{V(T)}{P(T,T_N)}
\right].
$$

---

## 44. Chapter Summary

The chapter builds a complete Gaussian LMM workflow:

```text
Initial zero curve
        ↓
Initial discount factors
        ↓
Initial forward curve
        ↓
Forward-rate correlation
        ↓
PCA factor reduction
        ↓
Gaussian volatility
        ↓
Terminal-measure drift
        ↓
Euler Monte Carlo simulation
        ↓
Future forward curves
        ↓
Discount-bond reconstruction
        ↓
Caplet and swaption pricing
```

The most important conceptual shift is that the LMM does not simulate one interest rate.

It simulates an entire forward-rate vector.

Each Monte Carlo path therefore represents the evolution of a complete forward curve through time.

---

## 45. Next Chapter — LMM-SABR Hybrid Model

The Gaussian LMM developed here captures:

- multiple forward rates;
- tenor-dependent volatility;
- cross-maturity correlation;
- terminal-measure drift;
- Monte Carlo option pricing.

However, the volatility is deterministic and Gaussian.

It cannot reproduce the volatility smile and skew observed in caplet and swaption markets.

The next chapter introduces SABR-style stochastic volatility:

```text
Gaussian LMM
    +
SABR stochastic volatility
    ↓
LMM-SABR hybrid model
```

The next extension studies how:

- stochastic volatility;
- forward-rate correlation;
- volatility smile;
- skew dynamics;
- interest-rate option pricing

can be combined in a richer multi-factor framework.

---

## Disclaimer

This repository is provided for educational and research purposes only.

It is not intended to provide investment advice, trading recommendations, valuation opinions, or production-ready risk-management infrastructure.
