\# Chapter 14 — LMM-SABR Hybrid Model



\## Stochastic Volatility, Forward-Curve Simulation, and Interest-Rate Option Pricing



This chapter extends the Gaussian LIBOR Market Model developed in Chapter 13 by introducing forward-specific SABR-style stochastic volatility.



The model retains the core LMM architecture:



\- an initial zero curve;

\- a discrete tenor structure;

\- forward rates as state variables;

\- cross-maturity correlation;

\- PCA-based rate factors;

\- terminal-measure drift;

\- Monte Carlo simulation;

\- caplet and European swaption pricing.



The main extension is that the volatility of each forward rate is no longer fully deterministic. Each forward rate is associated with its own stochastic volatility state.



\---



\# 1. Project Structure



The recommended directory structure is:



```text

14\_lmm\_sabr\_hybrid\_model/

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

│   └── 14\_lmm\_sabr\_hybrid\_model.ipynb

│

├── python/

│   ├── sabr\_parameters.py

│   ├── lmm\_sabr\_hybrid.py

│   ├── sabr\_simulation.py

│   ├── lmm\_sabr\_pricing.py

│   ├── sabr\_diagnostics.py

│   └── lmm\_sabr\_plotting.py

│

└── tests/

&#x20;   └── test.py

```



The Python implementation reuses the following Chapter 13 modules:



```text

13\_gaussain\_libor\_market\_model\_lmm/

└── python/

&#x20;   ├── market\_data.py

&#x20;   ├── tenor\_structure.py

&#x20;   ├── correlation.py

&#x20;   └── volatility.py

```



The Chapter 14 Python modules use distinct names to prevent import conflicts with files from Chapter 13.



\---



\# 2. Model Motivation



The Gaussian LMM in Chapter 13 models the evolution of a complete forward-rate curve.



For the forward rate applying over the period from \\(T\_i\\) to \\(T\_{i+1}\\), the Chapter 13 dynamics can be represented as:



$$

dL\_i(t)

=

\\mu\_i(t)\\,dt

\+

\\sigma\_i(t)b\_i\\cdot dW\_t.

$$



The volatility function is deterministic once the simulation time and forward maturity are known.



This structure is useful for:



\- modelling correlated curve movements;

\- understanding level, slope, and curvature factors;

\- testing terminal-measure dynamics;

\- pricing simple interest-rate options;

\- building a transparent Monte Carlo framework.



However, a deterministic-volatility Gaussian model has limited ability to reproduce:



\- volatility smiles;

\- volatility skews;

\- stochastic changes in option-market volatility;

\- asymmetric forward-rate distributions;

\- state-dependent tail behaviour.



The Chapter 14 model adds a stochastic volatility process for every forward rate.



The hybrid forward dynamics are:



$$

dL\_i(t)

=

\\mu\_i(t)\\,dt

\+

g\_i(t)\\alpha\_i(t)

\\left\[L\_i(t)+s\_i\\right]^{\\beta\_i}

b\_i\\cdot dW\_t.

$$



The associated stochastic-volatility process is:



$$

d\\alpha\_i(t)

=

\\nu\_i\\alpha\_i(t)\\,dZ\_i(t).

$$



The rate and volatility shocks are correlated:



$$

\\mathrm{Corr}

\\left(

dW\_i(t),

dZ\_i(t)

\\right)

=

\\rho\_i.

$$



The model therefore evolves both:



$$

L\_i(t)

$$



and:



$$

\\alpha\_i(t).

$$



\---



\# 3. Tenor Structure and Initial Forward Curve



Let the tenor dates be:



$$

0=T\_0<T\_1<\\cdots<T\_N.

$$



The accrual period for the \\(i\\)-th forward rate is:



$$

\\delta\_i

=

T\_{i+1}-T\_i.

$$



The forward rate \\(L\_i(t)\\) applies over:



$$

\[T\_i,T\_{i+1}].

$$



The initial zero curve provides discount factors:



$$

P(0,T).

$$



If continuously compounded zero rates are available, the discount factor is:



$$

P(0,T)

=

\\exp

\\left\[

\-z(0,T)T

\\right].

$$



The initial simple forward rate is obtained from adjacent discount factors:



$$

L\_i(0)

=

\\frac{1}{\\delta\_i}

\\left\[

\\frac{P(0,T\_i)}

{P(0,T\_{i+1})}

\-

1

\\right].

$$



The simulation begins from the market-consistent initial forward curve:



$$

L(0)

=

\\left\[

L\_0(0),

L\_1(0),

\\ldots,

L\_{N-1}(0)

\\right].

$$



\---



\# 4. SABR Parameter Structure



Each forward rate has its own SABR parameter set:



$$

\\alpha\_i(0),

\\quad

\\beta\_i,

\\quad

\\rho\_i,

\\quad

\\nu\_i,

\\quad

s\_i.

$$



The parameters have different roles.



\## Initial stochastic volatility



$$

\\alpha\_i(0)>0.

$$



The initial alpha level contributes to the overall volatility level of the forward rate.



\## Elasticity parameter



$$

0\\le \\beta\_i\\le 1.

$$



The parameter \\(\\beta\_i\\) controls how the absolute diffusion scale depends on the shifted forward level.



If:



$$

\\beta\_i=0,

$$



then:



$$

\\left\[L\_i(t)+s\_i\\right]^{\\beta\_i}=1,

$$



which gives a more normal-style diffusion.



If:



$$

\\beta\_i=1,

$$



then:



$$

\\left\[L\_i(t)+s\_i\\right]^{\\beta\_i}

=

L\_i(t)+s\_i,

$$



which gives a displaced-lognormal-style diffusion.



\## Rate-volatility correlation



$$

\-1<\\rho\_i<1.

$$



The parameter \\(\\rho\_i\\) controls the correlation between the forward-rate shock and the stochastic-volatility shock.



It is closely associated with the direction of the implied-volatility skew.



\## Volatility of volatility



$$

\\nu\_i\\ge 0.

$$



The parameter \\(\\nu\_i\\) controls the variability of the stochastic-volatility process.



Larger values of \\(\\nu\_i\\) generally produce more dispersed alpha paths and stronger smile curvature.



\## Displacement



$$

s\_i\\ge 0.

$$



The shifted forward must satisfy:



$$

L\_i(t)+s\_i>0.

$$



The displacement makes the model compatible with low or moderately negative forward rates and permits fractional values of \\(\\beta\_i\\).



\---



\# 5. Static Parameters and Dynamic State Variables



A key distinction is that not every SABR quantity changes during simulation.



The static model parameters are:



$$

\\beta\_i,

\\quad

\\rho\_i,

\\quad

\\nu\_i,

\\quad

s\_i.

$$



These are specified before the Monte Carlo simulation begins and remain fixed during one pricing run.



The dynamic state variables are:



$$

L\_i(t)

$$



and:



$$

\\alpha\_i(t).

$$



At every simulation date and on every Monte Carlo path, the model updates:



```text

the complete forward curve

\+

the complete stochastic-volatility curve

```



The complete model state is therefore:



$$

X(t)

=

\\left(

L\_0(t),

\\ldots,

L\_{N-1}(t),

\\alpha\_0(t),

\\ldots,

\\alpha\_{N-1}(t)

\\right).

$$



This is the main difference from the Gaussian LMM in Chapter 13, where the forward curve is the principal simulated state.



\---



\# 6. Correlation and PCA Rate Factors



Forward rates across different maturities are strongly correlated.



The exponential correlation specification is:



$$

\\rho\_{ij}^{L}

=

\\exp

\\left\[

\-\\gamma

\\left|

T\_i-T\_j

\\right|

\\right].

$$



A smaller value of \\(\\gamma\\) produces slower correlation decay.



A larger value of \\(\\gamma\\) produces faster correlation decay.



The full forward-rate correlation matrix may be decomposed as:



$$

\\rho^{L}

=

Q\\Lambda Q^\\top.

$$



A reduced \\(K\\)-factor representation is obtained using the largest eigenvalues and associated eigenvectors:



$$

B

=

Q\_K\\Lambda\_K^{1/2}.

$$



The \\(i\\)-th row of \\(B\\), denoted by \\(b\_i\\), contains the exposure of the \\(i\\)-th forward rate to the retained common rate factors.



A three-factor representation is commonly interpreted as:



1\. level;

2\. slope;

3\. curvature.



The reduced-factor approximation satisfies:



$$

BB^\\top

\\approx

\\rho^{L}.

$$



\---



\# 7. Hybrid LMM-SABR Factor Loadings



The instantaneous factor loading of forward \\(i\\) is:



$$

\\lambda\_i(t)

=

g\_i(t)

\\alpha\_i(t)

\\left\[

L\_i(t)+s\_i

\\right]^{\\beta\_i}

b\_i.

$$



This expression combines four components.



\## Deterministic maturity backbone



$$

g\_i(t).

$$



This term controls the broad maturity structure of forward volatility.



A typical specification is:



$$

g\_i(t)

=

g\_{\\mathrm{floor}}

\+

g\_{\\mathrm{level}}

\\exp

\\left\[

\-d(T\_i-t)

\\right].

$$



\## Stochastic volatility state



$$

\\alpha\_i(t).

$$



Two paths can have the same forward rate but different future risk because their alpha states may be different.



\## CEV-style level dependence



$$

\\left\[

L\_i(t)+s\_i

\\right]^{\\beta\_i}.

$$



This term allows absolute volatility to change with the forward-rate level.



\## Common rate-factor exposure



$$

b\_i.

$$



This term links each forward rate to the common level, slope, and curvature shocks.



The instantaneous covariance between forwards \\(i\\) and \\(j\\) is:



$$

\\lambda\_i(t)\\cdot\\lambda\_j(t).

$$



The complete forward covariance matrix is:



$$

\\Sigma(t)

=

\\Lambda(t)\\Lambda(t)^\\top,

$$



where \\(\\Lambda(t)\\) is the matrix whose rows are the factor-loading vectors.



\---



\# 8. Terminal-Measure Drift



The model uses the terminal zero-coupon bond:



$$

P(t,T\_N)

$$



as the numeraire.



Under the terminal measure, the forward-rate dynamics are:



$$

dL\_i(t)

=

\\mu\_i(t)\\,dt

\+

\\lambda\_i(t)\\cdot dW\_t^{T\_N}.

$$



The drift is:



$$

\\mu\_i(t)

=

\-

\\sum\_{j=i+1}^{N-1}

\\frac{

\\delta\_j

\\lambda\_i(t)\\cdot\\lambda\_j(t)

}{

1+\\delta\_jL\_j(t)

}.

$$



The drift of forward \\(i\\) depends only on forwards with later reset dates.



For the final forward:



$$

\\mu\_{N-1}(t)=0.

$$



This provides an important model diagnostic and unit test.



Although the drift formula has the same structure as the Gaussian LMM, the loadings in the hybrid model depend on both:



$$

L\_i(t)

$$



and:



$$

\\alpha\_i(t).

$$



The drift is therefore path-dependent through the stochastic covariance structure.



\---



\# 9. Stochastic-Volatility Evolution



The alpha process follows:



$$

d\\alpha\_i(t)

=

\\nu\_i\\alpha\_i(t)\\,dZ\_i(t).

$$



The implementation uses the exact lognormal update:



$$

\\alpha\_i(t+\\Delta t)

=

\\alpha\_i(t)

\\exp

\\left\[

\-\\frac{1}{2}\\nu\_i^2\\Delta t

\+

\\nu\_i\\sqrt{\\Delta t}\\,

Z\_i^\\alpha

\\right].

$$



This update preserves:



$$

\\alpha\_i(t)>0.

$$



The effective standardized forward shock is constructed from the factor loading:



$$

Z\_i^L

=

\\frac{

\\lambda\_i(t)\\cdot Z^L

}{

\\left\\|

\\lambda\_i(t)

\\right\\|

}.

$$



The correlated volatility shock is then:



$$

Z\_i^\\alpha

=

\\rho\_i Z\_i^L

\+

\\sqrt{

1-\\rho\_i^2

}

Z\_i^\\perp,

$$



where:



$$

Z\_i^\\perp

$$



is independent of the common rate-factor shocks.



This construction ensures:



$$

\\mathrm{Corr}

\\left(

Z\_i^L,

Z\_i^\\alpha

\\right)

=

\\rho\_i.

$$



\---



\# 10. Numerical Evolution Scheme



The forward rates are advanced using an Euler step.



For each active forward:



$$

L\_i(t+\\Delta t)

=

L\_i(t)

\+

\\mu\_i(t)\\Delta t

\+

\\lambda\_i(t)\\cdot Z^L

\\sqrt{\\Delta t}.

$$



The alpha state is advanced using the exact lognormal step:



$$

\\alpha\_i(t+\\Delta t)

=

\\alpha\_i(t)

\\exp

\\left\[

\-\\frac{1}{2}\\nu\_i^2\\Delta t

\+

\\nu\_i

\\sqrt{\\Delta t}

Z\_i^\\alpha

\\right].

$$



A forward is active only before its reset date:



$$

t<T\_i.

$$



Once:



$$

t\\ge T\_i,

$$



the corresponding forward and alpha state are frozen.



The Euler step may occasionally cross the displaced SABR boundary. The implementation therefore enforces:



$$

L\_i(t)

\\ge

\-s\_i+\\varepsilon,

$$



where \\(\\varepsilon\\) is a small positive numerical constant.



The model also requires:



$$

1+\\delta\_iL\_i(t)>0.

$$



This second condition is necessary for converting forward rates into valid discount factors.



The displaced floor is a practical numerical safeguard. It is not an exact boundary-preserving discretization and may introduce a small truncation bias near the boundary.



\---



\# 11. Monte Carlo Simulation Architecture



The simulator stores two three-dimensional arrays.



The forward paths are stored as:



```text

forwardPaths\[path]\[time]\[forward]

```



The stochastic-volatility paths are stored as:



```text

alphaPaths\[path]\[time]\[forward]

```



For example:



```cpp

forwardPaths\[10]\[40]\[6]

```



represents:



```text

Monte Carlo path 10

simulation-time index 40

forward-rate index 6

```



The complete forward curve on one path at one time is:



```cpp

forwardPaths\[10]\[40]

```



The simulator performs the following steps:



```text

build the simulation grid

&#x20;       ↓

add mandatory reset and expiry dates

&#x20;       ↓

initialize all paths from the same market curve

&#x20;       ↓

generate common rate-factor shocks

&#x20;       ↓

generate forward-specific volatility shocks

&#x20;       ↓

call the model evolution function

&#x20;       ↓

store the next forward and alpha states

&#x20;       ↓

repeat across time and paths

```



Antithetic variates may be used by pairing:



$$

Z

$$



with:



$$

\-Z.

$$



This reduces Monte Carlo variance without changing the underlying distribution.



\---



\# 12. Discount-Factor and Swap Reconstruction



The model simulates forward rates directly, but option pricing requires discount factors, annuities, and swap rates.



The forward-discount relationship is:



$$

1+\\delta\_iL\_i(t)

=

\\frac{

P(t,T\_i)

}{

P(t,T\_{i+1})

}.

$$



Therefore:



$$

P(t,T\_{i+1})

=

\\frac{

P(t,T\_i)

}{

1+\\delta\_iL\_i(t)

}.

$$



At a simulation date \\(T\_k\\), reconstruction begins from:



$$

P(T\_k,T\_k)=1.

$$



The later discount factors are generated recursively.



For a swap beginning at \\(T\_k\\) and ending at \\(T\_m\\), the annuity is:



$$

A(T\_k)

=

\\sum\_{j=k}^{m-1}

\\delta\_jP(T\_k,T\_{j+1}).

$$



The par swap rate is:



$$

S(T\_k)

=

\\frac{

1-P(T\_k,T\_m)

}{

A(T\_k)

}.

$$



A caplet depends primarily on one forward rate.



A swaption depends on an entire segment of the forward curve because both the swap annuity and par swap rate require multiple discount factors.



\---



\# 13. Caplet Pricing



Consider a caplet that fixes at \\(T\_i\\) and pays at \\(T\_{i+1}\\).



Its payment-date payoff is:



$$

\\mathrm{Payoff}\_{T\_{i+1}}

=

N\\delta\_i

\\max

\\left\[

L\_i(T\_i)-K,

0

\\right].

$$



The value at the fixing date is:



$$

V(T\_i)

=

\\frac{

N\\delta\_i

\\max

\\left\[

L\_i(T\_i)-K,

0

\\right]

}{

1+\\delta\_iL\_i(T\_i)

}.

$$



Under the terminal measure:



$$

V(0)

=

P(0,T\_N)

\\mathbb{E}^{T\_N}

\\left\[

\\frac{

V(T\_i)

}{

P(T\_i,T\_N)

}

\\right].

$$



The Monte Carlo estimator is:



$$

\\widehat{V}(0)

=

P(0,T\_N)

\\frac{1}{M}

\\sum\_{m=1}^{M}

\\frac{

V^{(m)}(T\_i)

}{

P^{(m)}(T\_i,T\_N)

}.

$$



The implementation also reports a Monte Carlo standard error.



\---



\# 14. European Payer Swaption Pricing



Consider a European payer swaption expiring at \\(T\_k\\) on a swap ending at \\(T\_m\\).



The expiry payoff is:



$$

\\mathrm{Payoff}\_{T\_k}

=

N

A(T\_k)

\\max

\\left\[

S(T\_k)-K,

0

\\right].

$$



The swap annuity is:



$$

A(T\_k)

=

\\sum\_{j=k}^{m-1}

\\delta\_jP(T\_k,T\_{j+1}).

$$



The par swap rate is:



$$

S(T\_k)

=

\\frac{

1-P(T\_k,T\_m)

}{

A(T\_k)

}.

$$



Under the terminal measure:



$$

V(0)

=

P(0,T\_N)

\\mathbb{E}^{T\_N}

\\left\[

\\frac{

\\mathrm{Payoff}\_{T\_k}

}{

P(T\_k,T\_N)

}

\\right].

$$



The Monte Carlo estimator is:



$$

\\widehat{V}(0)

=

P(0,T\_N)

\\frac{1}{M}

\\sum\_{m=1}^{M}

\\frac{

\\mathrm{Payoff}\_{T\_k}^{(m)}

}{

P^{(m)}(T\_k,T\_N)

}.

$$



The payer swaption becomes more valuable when simulated par swap rates exceed the strike.



\---



\# 15. Compilation, Execution, and Limitations



\## C++ compilation



From the `cpp` directory, compile with:



```bash

g++ -std=c++17 -O2 SABRParameters.cpp LMMSABRHybrid.cpp SABRSimulation.cpp LMMSABRPricing.cpp main.cpp -o lmm\_sabr\_demo

```



On Windows PowerShell:



```bash

g++ -std=c++17 -O2 SABRParameters.cpp LMMSABRHybrid.cpp SABRSimulation.cpp LMMSABRPricing.cpp main.cpp -o lmm\_sabr\_demo.exe

```



Run on Windows:



```bash

.\\lmm\_sabr\_demo.exe

```



Run on Linux or macOS:



```bash

./lmm\_sabr\_demo

```



\## Python tests



From the project root:



```bash

pytest 14\_lmm\_sabr\_hybrid\_model/tests/test.py -v

```



Alternatively, from the Chapter 14 `tests` directory:



```bash

pytest test.py -v

```



\## Model limitations



This implementation is designed for education, prototyping, and model-architecture study.



It does not yet include:



\- calibration to market caplet smiles;

\- calibration to a swaption volatility cube;

\- predictor-corrector LMM discretization;

\- exact displaced-forward simulation;

\- smooth parameter regularization;

\- stochastic correlation;

\- local or stochastic displacement;

\- Bermudan exercise;

\- adjoint differentiation;

\- production Greeks;

\- multi-curve discounting and forwarding;

\- collateral and funding conventions;

\- calibration Jacobians;

\- production-level performance optimization.



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

