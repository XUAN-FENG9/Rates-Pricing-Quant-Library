# Chapter 14 — LMM-SABR Hybrid Model

# 14.1 Stochastic Volatility, Forward-Curve Simulation, and Interest-Rate Option Pricing

This chapter extends the Gaussian LIBOR Market Model developed in Chapter 13 by introducing forward-specific SABR-style stochastic volatility.

The model retains the core LMM architecture:

- an initial zero curve;
- a discrete tenor structure;
- forward rates as state variables;
- cross-maturity correlation;
- PCA-based rate factors;
- terminal-measure drift;
- Monte Carlo simulation;
- caplet and European swaption pricing.

The main extension is that the volatility of each forward rate is no longer fully deterministic. Each forward rate is associated with its own stochastic volatility state.

---

# 14.2 Project Structure

The recommended directory structure is:

```text
14_lmm_sabr_hybrid_model/
├── cpp/
│   ├── Matrix.hpp
│   ├── SABRParameters.hpp
│   ├── SABRParameters.cpp
│   ├── LMMSABRHybrid.hpp
│   ├── LMMSABRHybrid.cpp
│   ├── SABRSimulation.hpp
│   ├── SABRSimulation.cpp
│   ├── LMMSABRPricing.hpp
│   ├── LMMSABRPricing.cpp
│   └── main.cpp
│
├── notebooks/
│   └── 14_lmm_sabr_hybrid_model.ipynb
│
├── python/
│   ├── sabr_parameters.py
│   ├── lmm_sabr_hybrid.py
│   ├── sabr_simulation.py
│   ├── lmm_sabr_pricing.py
│   ├── sabr_diagnostics.py
│   └── lmm_sabr_plotting.py
│
└── tests/
    └── test.py
```

The Python implementation reuses the following Chapter 13 modules:

```text
13_gaussain_libor_market_model_lmm/
└── python/
    ├── market_data.py
    ├── tenor_structure.py
    ├── correlation.py
    └── volatility.py
```

The Chapter 14 Python modules use distinct names to prevent import conflicts with files from Chapter 13.

---

# 14.3 Model Motivation

The Gaussian LMM in Chapter 13 models the evolution of a complete forward-rate curve.

For the forward rate applying over the period from $T_i$ to $T_{i+1}$, the Chapter 13 dynamics can be represented as:

$$
dL_i(t)=
\mu_i(t)\,dt
+
\sigma_i(t)b_i\cdot dW_t.
$$

The volatility function is deterministic once the simulation time and forward maturity are known.

This structure is useful for:

- modelling correlated curve movements;
- understanding level, slope, and curvature factors;
- testing terminal-measure dynamics;
- pricing simple interest-rate options;
- building a transparent Monte Carlo framework.

However, a deterministic-volatility Gaussian model has limited ability to reproduce:

- volatility smiles;
- volatility skews;
- stochastic changes in option-market volatility;
- asymmetric forward-rate distributions;
- state-dependent tail behaviour.

The Chapter 14 model adds a stochastic volatility process for every forward rate.

The hybrid forward dynamics are:

$$
dL_i(t)=
\mu_i(t)\,dt
+
g_i(t)\alpha_i(t)
\left[L_i(t)+s_i\right]^{\beta_i}
b_i\cdot dW_t.
$$

The associated stochastic-volatility process is:

$$
d\alpha_i(t)=
\nu_i\alpha_i(t)\,dZ_i(t).
$$

The rate and volatility shocks are correlated:

$$
\mathrm{Corr}
\left(
dW_i(t),
dZ_i(t)
\right)=
\rho_i.
$$

The model therefore evolves both:

$$
L_i(t)
$$

and:

$$
\alpha_i(t).
$$

---

# 14.4 Tenor Structure and Initial Forward Curve

Let the tenor dates be:

$$
0=T_0<T_1<\cdots<T_N.
$$

The accrual period for the $i$-th forward rate is:

$$
\delta_i=
T_{i+1}-T_i.
$$

The forward rate $L_i(t)$ applies over:

$$
[T_i,T_{i+1}].
$$

The initial zero curve provides discount factors:

$$
P(0,T).
$$

If continuously compounded zero rates are available, the discount factor is:

$$
P(0,T)=
\exp
\left[
-z(0,T)T
\right].
$$

The initial simple forward rate is obtained from adjacent discount factors:

$$
L_i(0)=
\frac{1}{\delta_i}
\left[
\frac{P(0,T_i)}
{P(0,T_{i+1})}-
1
\right].
$$

The simulation begins from the market-consistent initial forward curve:

$$
L(0)=
\left[
L_0(0),
L_1(0),
\ldots,
L_{N-1}(0)
\right].
$$

---

# 14.5 SABR Parameter Structure

Each forward rate has its own SABR parameter set:

$$
\alpha_i(0),
\quad
\beta_i,
\quad
\rho_i,
\quad
\nu_i,
\quad
s_i.
$$

The parameters have different roles.

## Initial stochastic volatility

$$
\alpha_i(0)>0.
$$

The initial alpha level contributes to the overall volatility level of the forward rate.

## Elasticity parameter

$$
0\le \beta_i\le 1.
$$

The parameter $\beta_i$ controls how the absolute diffusion scale depends on the shifted forward level.

If:

$$
\beta_i=0,
$$

then:

$$
\left[L_i(t)+s_i\right]^{\beta_i}=1,
$$

which gives a more normal-style diffusion.

If:

$$
\beta_i=1,
$$

then:

$$
\left[L_i(t)+s_i\right]^{\beta_i}=
L_i(t)+s_i,
$$

which gives a displaced-lognormal-style diffusion.

## Rate-volatility correlation

$$
-1<\rho_i<1.
$$

The parameter $\rho_i$ controls the correlation between the forward-rate shock and the stochastic-volatility shock.

It is closely associated with the direction of the implied-volatility skew.

## Volatility of volatility

$$
\nu_i\ge 0.
$$

The parameter $\nu_i$ controls the variability of the stochastic-volatility process.

Larger values of $\nu_i$ generally produce more dispersed alpha paths and stronger smile curvature.

## Displacement

$$
s_i\ge 0.
$$

The shifted forward must satisfy:

$$
L_i(t)+s_i>0.
$$

The displacement makes the model compatible with low or moderately negative forward rates and permits fractional values of $\beta_i$.

---

# 14.6 Static Parameters and Dynamic State Variables

A key distinction is that not every SABR quantity changes during simulation.

The static model parameters are:

$$
\beta_i,
\quad
\rho_i,
\quad
\nu_i,
\quad
s_i.
$$

These are specified before the Monte Carlo simulation begins and remain fixed during one pricing run.

The dynamic state variables are:

$$
L_i(t)
$$

and:

$$
\alpha_i(t).
$$

At every simulation date and on every Monte Carlo path, the model updates:

```text
the complete forward curve
+
the complete stochastic-volatility curve
```

The complete model state is therefore:

$$
X(t)=
\left(
L_0(t),
\ldots,
L_{N-1}(t),
\alpha_0(t),
\ldots,
\alpha_{N-1}(t)
\right).
$$

This is the main difference from the Gaussian LMM in Chapter 13, where the forward curve is the principal simulated state.

---

# 14.7 Correlation and PCA Rate Factors

Forward rates across different maturities are strongly correlated.

The exponential correlation specification is:

$$
\rho_{ij}^{L}=
\exp
\left[
-\gamma
\left|
T_i-T_j
\right|
\right].
$$

A smaller value of $\gamma$ produces slower correlation decay.

A larger value of $\gamma$ produces faster correlation decay.

The full forward-rate correlation matrix may be decomposed as:

$$
\rho^{L}=
Q\Lambda Q^\top.
$$

A reduced $K$-factor representation is obtained using the largest eigenvalues and associated eigenvectors:

$$
B=
Q_K\Lambda_K^{1/2}.
$$

The $i$-th row of $B$, denoted by $b_i$, contains the exposure of the $i$-th forward rate to the retained common rate factors.

A three-factor representation is commonly interpreted as:

1. level;
2. slope;
3. curvature.

The reduced-factor approximation satisfies:

$$
BB^\top
\approx
\rho^{L}.
$$

---

# 14.8 Hybrid LMM-SABR Factor Loadings

The instantaneous factor loading of forward $i$ is:

$$
\lambda_i(t)=
g_i(t)
\alpha_i(t)
\left[
L_i(t)+s_i
\right]^{\beta_i}
b_i.
$$

This expression combines four components.

## Deterministic maturity backbone

$$
g_i(t).
$$

This term controls the broad maturity structure of forward volatility.

A typical specification is:

$$
g_i(t)=
g_{\mathrm{floor}}
+
g_{\mathrm{level}}
\exp
\left[
-d(T_i-t)
\right].
$$

## Stochastic volatility state

$$
\alpha_i(t).
$$

Two paths can have the same forward rate but different future risk because their alpha states may be different.

## CEV-style level dependence

$$
\left[
L_i(t)+s_i
\right]^{\beta_i}.
$$

This term allows absolute volatility to change with the forward-rate level.

## Common rate-factor exposure

$$
b_i.
$$

This term links each forward rate to the common level, slope, and curvature shocks.

The instantaneous covariance between forwards $i$ and $j$ is:

$$
\lambda_i(t)\cdot\lambda_j(t).
$$

The complete forward covariance matrix is:

$$
\Sigma(t)=
\Lambda(t)\Lambda(t)^\top,
$$

where $\Lambda(t)$ is the matrix whose rows are the factor-loading vectors.

---

# 14.9 Terminal-Measure Drift

The model uses the terminal zero-coupon bond:

$$
P(t,T_N)
$$

as the numeraire.

Under the terminal measure, the forward-rate dynamics are:

$$
dL_i(t)=
\mu_i(t)\,dt
+
\lambda_i(t)\cdot dW_t^{T_N}.
$$

The drift is:

$$
\mu_i(t)=-
\sum_{j=i+1}^{N-1}
\frac{
\delta_j
\lambda_i(t)\cdot\lambda_j(t)
}{
1+\delta_jL_j(t)
}.
$$

The drift of forward $i$ depends only on forwards with later reset dates.

For the final forward:

$$
\mu_{N-1}(t)=0.
$$

This provides an important model diagnostic and unit test.

Although the drift formula has the same structure as the Gaussian LMM, the loadings in the hybrid model depend on both:

$$
L_i(t)
$$

and:

$$
\alpha_i(t).
$$

The drift is therefore path-dependent through the stochastic covariance structure.

---

# 14.10 Stochastic-Volatility Evolution

The alpha process follows:

$$
d\alpha_i(t)=
\nu_i\alpha_i(t)\,dZ_i(t).
$$

The implementation uses the exact lognormal update:

$$
\alpha_i(t+\Delta t)=
\alpha_i(t)
\exp
\left[
-\frac{1}{2}\nu_i^2\Delta t
+
\nu_i\sqrt{\Delta t}\,
Z_i^\alpha
\right].
$$

This update preserves:

$$
\alpha_i(t)>0.
$$

The effective standardized forward shock is constructed from the factor loading:

$$
Z_i^L=
\frac{
\lambda_i(t)\cdot Z^L
}{
\left\|
\lambda_i(t)
\right\|
}.
$$

The correlated volatility shock is then:

$$
Z_i^\alpha=
\rho_i Z_i^L
+
\sqrt{
1-\rho_i^2
}
Z_i^\perp,
$$

where:

$$
Z_i^\perp
$$

is independent of the common rate-factor shocks.

This construction ensures:

$$
\mathrm{Corr}
\left(
Z_i^L,
Z_i^\alpha
\right)=
\rho_i.
$$

---

# 14.11 Numerical Evolution Scheme

The forward rates are advanced using an Euler step.

For each active forward:

$$
L_i(t+\Delta t)=
L_i(t)
+
\mu_i(t)\Delta t
+
\lambda_i(t)\cdot Z^L
\sqrt{\Delta t}.
$$

The alpha state is advanced using the exact lognormal step:

$$
\alpha_i(t+\Delta t)=
\alpha_i(t)
\exp
\left[
-\frac{1}{2}\nu_i^2\Delta t
+
\nu_i
\sqrt{\Delta t}
Z_i^\alpha
\right].
$$

A forward is active only before its reset date:

$$
t<T_i.
$$

Once:

$$
t\ge T_i,
$$

the corresponding forward and alpha state are frozen.

The Euler step may occasionally cross the displaced SABR boundary. The implementation therefore enforces:

$$
L_i(t)
\ge
-s_i+\varepsilon,
$$

where $\varepsilon$ is a small positive numerical constant.

The model also requires:

$$
1+\delta_iL_i(t)>0.
$$

This second condition is necessary for converting forward rates into valid discount factors.

The displaced floor is a practical numerical safeguard. It is not an exact boundary-preserving discretization and may introduce a small truncation bias near the boundary.

---

# 14.12 Monte Carlo Simulation Architecture

The simulator stores two three-dimensional arrays.

The forward paths are stored as:

```text
forwardPaths[path][time][forward]
```

The stochastic-volatility paths are stored as:

```text
alphaPaths[path][time][forward]
```

For example:

```cpp
forwardPaths[10][40][6]
```

represents:

```text
Monte Carlo path 10
simulation-time index 40
forward-rate index 6
```

The complete forward curve on one path at one time is:

```cpp
forwardPaths[10][40]
```

The simulator performs the following steps:

```text
build the simulation grid
        ↓
add mandatory reset and expiry dates
        ↓
initialize all paths from the same market curve
        ↓
generate common rate-factor shocks
        ↓
generate forward-specific volatility shocks
        ↓
call the model evolution function
        ↓
store the next forward and alpha states
        ↓
repeat across time and paths
```

Antithetic variates may be used by pairing:

$$
Z
$$

with:

$$
-Z.
$$

This reduces Monte Carlo variance without changing the underlying distribution.

---

# 14.13 Discount-Factor and Swap Reconstruction

The model simulates forward rates directly, but option pricing requires discount factors, annuities, and swap rates.

The forward-discount relationship is:

$$
1+\delta_iL_i(t)=
\frac{
P(t,T_i)
}{
P(t,T_{i+1})
}.
$$

Therefore:

$$
P(t,T_{i+1})=
\frac{
P(t,T_i)
}{
1+\delta_iL_i(t)
}.
$$

At a simulation date $T_k$, reconstruction begins from:

$$
P(T_k,T_k)=1.
$$

The later discount factors are generated recursively.

For a swap beginning at $T_k$ and ending at $T_m$, the annuity is:

$$
A(T_k)=
\sum_{j=k}^{m-1}
\delta_jP(T_k,T_{j+1}).
$$

The par swap rate is:

$$
S(T_k)=
\frac{
1-P(T_k,T_m)
}{
A(T_k)
}.
$$

A caplet depends primarily on one forward rate.

A swaption depends on an entire segment of the forward curve because both the swap annuity and par swap rate require multiple discount factors.

---

# 14.14 Caplet Pricing

Consider a caplet that fixes at $T_i$ and pays at $T_{i+1}$.

Its payment-date payoff is:

$$
\mathrm{Payoff}_{T_{i+1}}=
N\delta_i
\max
\left[
L_i(T_i)-K,
0
\right].
$$

The value at the fixing date is:

$$
V(T_i)=
\frac{
N\delta_i
\max
\left[
L_i(T_i)-K,
0
\right]
}{
1+\delta_iL_i(T_i)
}.
$$

Under the terminal measure:

$$
V(0)=
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

The Monte Carlo estimator is:

$$
\widehat{V}(0)=
P(0,T_N)
\frac{1}{M}
\sum_{m=1}^{M}
\frac{
V^{(m)}(T_i)
}{
P^{(m)}(T_i,T_N)
}.
$$

The implementation also reports a Monte Carlo standard error.

---

# 14.15 European Payer Swaption Pricing

Consider a European payer swaption expiring at $T_k$ on a swap ending at $T_m$.

The expiry payoff is:

$$
\mathrm{Payoff}_{T_k}=
N
A(T_k)
\max
\left[
S(T_k)-K,
0
\right].
$$

The swap annuity is:

$$
A(T_k)=
\sum_{j=k}^{m-1}
\delta_jP(T_k,T_{j+1}).
$$

The par swap rate is:

$$
S(T_k)=
\frac{
1-P(T_k,T_m)
}{
A(T_k)
}.
$$

Under the terminal measure:

$$
V(0)=
P(0,T_N)
\mathbb{E}^{T_N}
\left[
\frac{
\mathrm{Payoff}_{T_k}
}{
P(T_k,T_N)
}
\right].
$$

The Monte Carlo estimator is:

$$
\widehat{V}(0)
=P(0,T_N)
\frac{1}{M}
\sum_{m=1}^{M}
\frac{
\mathrm{Payoff}_{T_k}^{(m)}
}{
P^{(m)}(T_k,T_N)
}.
$$

The payer swaption becomes more valuable when simulated par swap rates exceed the strike.

---

# 14.16 Compilation, Execution, and Limitations

## C++ compilation

From the `cpp` directory, compile with:

```bash
g++ -std=c++17 -O2 SABRParameters.cpp LMMSABRHybrid.cpp SABRSimulation.cpp LMMSABRPricing.cpp main.cpp -o lmm_sabr_demo
```

On Windows PowerShell:

```bash
g++ -std=c++17 -O2 SABRParameters.cpp LMMSABRHybrid.cpp SABRSimulation.cpp LMMSABRPricing.cpp main.cpp -o lmm_sabr_demo.exe
```

Run on Windows:

```bash
.\lmm_sabr_demo.exe
```

Run on Linux or macOS:

```bash
./lmm_sabr_demo
```

## Python tests

From the project root:

```bash
pytest 14_lmm_sabr_hybrid_model/tests/test.py -v
```

Alternatively, from the Chapter 14 `tests` directory:

```bash
pytest test.py -v
```

## Model limitations

This implementation is designed for education, prototyping, and model-architecture study.

It does not yet include:

- calibration to market caplet smiles;
- calibration to a swaption volatility cube;
- predictor-corrector LMM discretization;
- exact displaced-forward simulation;
- smooth parameter regularization;
- stochastic correlation;
- local or stochastic displacement;
- Bermudan exercise;
- adjoint differentiation;
- production Greeks;
- multi-curve discounting and forwarding;
- collateral and funding conventions;
- calibration Jacobians;
- production-level performance optimization.

The parameters used in the examples are illustrative rather than market calibrated.

In production, the typical interpretation is:

```text
alpha
primarily controls the ATM volatility level

beta
controls rate-level elasticity

rho
primarily controls skew

nu
primarily controls smile curvature

shift
supports low or negative rates
```

Beta and shift are often fixed by model convention, while alpha, rho, and nu are calibrated subject to smoothness and stability constraints.

The main learning objective is to understand how a deterministic-volatility Gaussian LMM can be extended into a stochastic-volatility forward-rate model while preserving the LMM tenor, correlation, measure, simulation, and pricing architecture.
