# Chapter 12 — Least-Squares Monte Carlo

## American-Style Exercise, Continuation Values, and Bermudan Swaption Pricing

This chapter introduces the Least-Squares Monte Carlo method, commonly abbreviated as LSM.

LSM is designed for derivatives with early-exercise rights.

Examples include:

- American options;
- Bermudan swaptions;
- callable bonds;
- cancellable swaps;
- mortgage-style products;
- structured products with issuer call features;
- real options.

The central difficulty is that, at each exercise date, the holder must compare:

```text
Exercise now
vs
Continue holding the option
```

The immediate exercise value is usually observable from the current simulated state.

The continuation value is not directly observable because it depends on future uncertain cash flows.

LSM solves this problem by using regression to estimate the conditional expected continuation value from Monte Carlo paths.

The method combines:

```text
Monte Carlo simulation
        +
Backward induction
        +
Regression
        ↓
Approximate optimal exercise strategy
```

---

## 1. Chapter Objectives

After completing this chapter, the reader should understand:

1. why early-exercise derivatives are more difficult than European derivatives;
2. what an exercise value is;
3. what a continuation value is;
4. how backward induction works;
5. why regression is required;
6. how polynomial basis functions approximate continuation values;
7. how LSM determines the exercise rule;
8. how Bermudan swaption cash flows are represented;
9. how discounting is handled across exercise dates;
10. how Python and C++ implementations correspond to the mathematical algorithm.

---

## 2. Project Structure

```text
12_least_squares_monte_carlo/
├── README.md
│
├── notebooks/
│   └── 12_least_squares_monte_carlo.ipynb
│
├── python/
│   ├── market_data.py
│   ├── short_rate_model.py
│   ├── simulation.py
│   ├── swap.py
│   ├── bermudan_swaption.py
│   ├── basis_functions.py
│   ├── regression.py
│   ├── lsm.py
│   ├── diagnostics.py
│   └── plotting.py
│
├── tests/
│   ├── test_basis_functions.py
│   ├── test_regression.py
│   ├── test_bermudan_swaption.py
│   └── test_lsm_pricing.py
│
└── cpp/
    ├── BasisFunctions.hpp
    ├── BasisFunctions.cpp
    ├── Regression.hpp
    ├── Regression.cpp
    ├── BermudanSwaption.hpp
    ├── BermudanSwaption.cpp
    ├── LSMEngine.hpp
    ├── LSMEngine.cpp
    ├── Diagnostics.hpp
    ├── Diagnostics.cpp
    └── main.cpp
```

The exact filenames may differ slightly depending on the repository structure, but the logical roles remain the same.

---

## 3. European and American-Style Exercise

A European option can be exercised only once, at maturity.

Its time-zero value is:

$$
V(0) =
\mathbb{E}^{Q}
\left[
D(0,T)\,
\Pi(T)
\right],
$$

where:

- $D(0,T)$ is the discount factor;
- $\Pi(T)$ is the maturity payoff;
- $Q$ is the pricing measure.

A Bermudan option can be exercised at a finite set of dates:

$$
t_1<t_2<\cdots<t_M.
$$

At every exercise date $t_m$, the holder decides whether to:

- exercise immediately;
- continue to the next exercise date.

The value therefore depends on an optimal stopping problem.

---

## 4. The Optimal Stopping Problem

Let:

$$
E_m
$$

denote the immediate exercise value at exercise date $t_m$.

Let:

$$
C_m
$$

denote the continuation value at the same date.

The option value at $t_m$ is:

$$
V_m =
\max
\left(
E_m,
C_m
\right).
$$

The optimal exercise decision is:

$$
\text{Exercise at }t_m
\quad\text{if}\quad
E_m>C_m.
$$

Otherwise:

$$
\text{Continue at }t_m
\quad\text{if}\quad
E_m\le C_m.
$$

The immediate exercise value is usually easy to calculate.

The continuation value is difficult because it is a conditional expectation of future optimal cash flows.

---

## 5. Continuation Value

Suppose the model state at time $t_m$ is:

$$
X_m.
$$

The continuation value is:

$$
C_m =
\mathbb{E}^{Q}
\left[
D(t_m,t_{m+1})V_{m+1}
\mid
X_m
\right].
$$

This means:

> Given the information available at time $t_m$, what is the expected discounted value of continuing?

The problem is that this conditional expectation is not directly known.

LSM estimates it through cross-sectional regression across Monte Carlo paths.

---

## 6. Main Idea of Least-Squares Monte Carlo

Suppose $N$ Monte Carlo paths have been simulated.

At exercise date $t_m$, each path provides:

- a current state variable $X_m^{(n)}$;
- an immediate exercise value $E_m^{(n)}$;
- a realized discounted future cash flow $Y_m^{(n)}$.

LSM approximates the continuation value as:

$$
C_m
\approx
\widehat{C}_m(X_m).
$$

A regression model is fitted:

$$
Y_m^{(n)} =
\sum_{k=0}^{K}
\beta_k
\phi_k
\left(
X_m^{(n)}
\right)
+
\varepsilon_m^{(n)}.
$$

Here:

- $\phi_k$ are basis functions;
- $\beta_k$ are regression coefficients;
- $\varepsilon_m^{(n)}$ is the regression residual.

The estimated continuation value is:

$$
\widehat{C}_m(x) =
\sum_{k=0}^{K}
\widehat{\beta}_k
\phi_k(x).
$$

The exercise rule becomes:

$$
E_m^{(n)} >
\widehat{C}_m
\left(
X_m^{(n)}
\right).
$$

---

## 7. Why Regression Works

Monte Carlo paths provide many examples of:

```text
Current state
→ Future discounted payoff
```

The regression uses these examples to estimate how future value depends on the current state.

For example:

```text
Current swap rate
Current annuity
Current short rate
Current discount factor
Current intrinsic value
```

may help explain the future value of a Bermudan swaption.

The fitted regression approximates the conditional expectation:

$$
\mathbb{E}^{Q}
\left[
Y_m
\mid
X_m=x
\right].
$$

This conditional expectation is the continuation value.

---

## 8. Backward Induction

LSM works backward from the final exercise date.

Suppose the exercise dates are:

$$
t_1<t_2<t_3.
$$

The algorithm proceeds in reverse:

```text
Start at t3
    ↓
Determine payoff at final exercise date
    ↓
Move backward to t2
    ↓
Estimate continuation value
    ↓
Decide exercise or continue
    ↓
Move backward to t1
    ↓
Estimate continuation value
    ↓
Decide exercise or continue
    ↓
Discount final optimal cash flows to time 0
```

At the last exercise date $t_M$, there is no later continuation opportunity.

Therefore:

$$
V_M =
E_M.
$$

At each earlier exercise date:

$$
V_m =
\max
\left(
E_m,
\widehat{C}_m
\right).
$$

---

## 9. Cash-Flow Representation

A practical LSM implementation usually maintains, for each Monte Carlo path:

- the currently selected future cash flow;
- the date on which that cash flow occurs;
- whether the option has already been exercised.

Suppose path $n$ currently has a future optimal cash flow:

$$
CF^{(n)}
$$

paid at time:

$$
\tau^{(n)}.
$$

At exercise date $t_m$, the continuation target is the discounted future cash flow:

$$
Y_m^{(n)} =
D
\left(
t_m,\tau^{(n)}
\right)
CF^{(n)}.
$$

The regression estimates:

$$
\mathbb{E}
\left[
Y_m
\mid
X_m
\right].
$$

If immediate exercise is optimal, the stored cash flow is replaced by:

$$
CF^{(n)} =
E_m^{(n)},
$$

and the cash-flow time becomes:

$$
\tau^{(n)}=t_m.
$$

---

## 10. Exercise Value for a Bermudan Payer Swaption

A payer swaption gives the holder the right to:

```text
pay fixed
receive floating
```

At exercise date $t_m$, the intrinsic value is:

$$
E_m =
N A_m
\max
\left(
S_m-K,
0
\right),
$$

where:

- $N$ is the notional;
- $A_m$ is the swap annuity;
- $S_m$ is the par swap rate;
- $K$ is the fixed strike.

The annuity is:

$$
A_m =
\sum_{j=m}^{J-1}
\delta_j
P
\left(
t_m,T_{j+1}
\right).
$$

The par swap rate is:

$$
S_m =
\frac{P(t_m,T_m) -
P(t_m,T_J)
}{
A_m
}.
$$

At an exercise date:

$$
P(t_m,T_m)=1,
$$

so:

$$
S_m =
\frac{
1-P(t_m,T_J)
}{
A_m
}.
$$

For a receiver swaption:

$$
E_m =
N A_m
\max
\left(
K-S_m,
0
\right).
$$

---

## 11. In-the-Money Paths

In many LSM implementations, regression is performed only on paths that are currently in the money.

For a payer swaption:

$$
E_m^{(n)}>0.
$$

These are the paths for which immediate exercise is economically relevant.

Out-of-the-money paths have zero immediate exercise value, so they are usually continued automatically.

Using only in-the-money paths may improve the regression because the model focuses on the region where the exercise decision matters.

The logic is:

```text
Out of the money
→ Do not exercise
→ Continue

In the money
→ Compare exercise value with continuation value
```

---

## 12. Basis Functions

The continuation value is approximated using basis functions.

A simple polynomial basis is:

$$
\phi_0(x)=1,
$$

$$
\phi_1(x)=x,
$$

$$
\phi_2(x)=x^2,
$$

$$
\phi_3(x)=x^3.
$$

The continuation approximation becomes:

$$
\widehat{C}(x) =
\beta_0
+
\beta_1x
+
\beta_2x^2
+
\beta_3x^3.
$$

For a two-dimensional state vector:

$$
X=(x_1,x_2),
$$

possible basis functions include:

$$
1,
$$

$$
x_1,
\quad
x_2,
$$

$$
x_1^2,
\quad
x_2^2,
$$

$$
x_1x_2.
$$

A multivariate approximation may be:

$$
\widehat{C}(x_1,x_2) =
\beta_0
+
\beta_1x_1
+
\beta_2x_2
+
\beta_3x_1^2
+
\beta_4x_2^2
+
\beta_5x_1x_2.
$$

---

## 13. Choice of State Variables

The state variables should contain enough information to explain future option value.

For a Bermudan swaption, common choices include:

- par swap rate;
- swap annuity;
- intrinsic value;
- short rate;
- selected discount factors;
- one or more yield-curve factors;
- underlying swap value.

A simple one-factor implementation may use:

$$
X_m=S_m.
$$

A richer implementation may use:

$$
X_m=
\left(
S_m,
A_m
\right).
$$

Another possibility is:

$$
X_m=
\left(
S_m,
r_m,
A_m
\right).
$$

More state variables can improve approximation power, but they also increase regression instability and data requirements.

---

## 14. Ordinary Least Squares

Let the regression matrix be:

$$
\Phi =
\begin{bmatrix}
\phi_0(X^{(1)}) & \phi_1(X^{(1)}) & \cdots & \phi_K(X^{(1)}) \\
\phi_0(X^{(2)}) & \phi_1(X^{(2)}) & \cdots & \phi_K(X^{(2)}) \\
\vdots & \vdots & \ddots & \vdots \\
\phi_0(X^{(N)}) & \phi_1(X^{(N)}) & \cdots & \phi_K(X^{(N)})
\end{bmatrix}.
$$

Let:

$$
Y =
\begin{bmatrix}
Y^{(1)} \\
Y^{(2)} \\
\vdots \\
Y^{(N)}
\end{bmatrix}.
$$

The least-squares problem is:

$$
\widehat{\beta} =
\arg\min_{\beta}
\left\|
\Phi\beta-Y
\right\|^2.
$$

The normal-equation solution is:

$$
\widehat{\beta} =
\left(
\Phi^\top\Phi
\right)^{-1}
\Phi^\top Y.
$$

In production code, direct matrix inversion is usually avoided.

More stable methods include:

- QR decomposition;
- singular-value decomposition;
- ridge regression;
- orthogonal polynomial bases.

---

## 15. Standardization of State Variables

Polynomial regression can become unstable when state variables have very different scales.

For example:

```text
swap rate   ≈ 0.04
annuity     ≈ 4.50
swap value  ≈ 100,000
```

A common solution is standardization:

$$
z =
\frac{x-\mu_x}{\sigma_x}.
$$

Polynomial basis functions are then constructed from $z$:

$$
1,
\quad
z,
\quad
z^2,
\quad
z^3.
$$

Standardization may improve:

- numerical conditioning;
- regression stability;
- coefficient interpretation;
- Python and C++ consistency.

---

## 16. Exercise Decision

Once continuation values are estimated, path $n$ exercises at time $t_m$ if:

$$
E_m^{(n)}
>
\widehat{C}_m^{(n)}.
$$

The path continues if:

$$
E_m^{(n)}
\le
\widehat{C}_m^{(n)}.
$$

In code, the central logic is conceptually:

```text
if immediate_exercise_value > estimated_continuation_value:
    exercise now
else:
    continue
```

This comparison is the core of the LSM algorithm.

---

## 17. Bermudan Swaption Exercise Dates

A Bermudan swaption has a finite exercise schedule.

For example:

```text
Exercise dates:
1Y, 2Y, 3Y, 4Y

Final swap maturity:
5Y
```

If exercised at 1Y, the holder enters a swap from 1Y to 5Y.

If exercised at 2Y, the holder enters a swap from 2Y to 5Y.

If exercised at 3Y, the holder enters a swap from 3Y to 5Y.

If exercised at 4Y, the holder enters a swap from 4Y to 5Y.

The remaining underlying swap becomes shorter at later exercise dates.

Therefore, both the annuity and swap rate must be recalculated at every exercise date.

---

## 18. Example of Backward Induction

Consider three exercise dates:

$$
t_1=1,
\qquad
t_2=2,
\qquad
t_3=3.
$$

### Final date $t_3$

There is no continuation beyond the final exercise date.

Therefore:

$$
V_3=E_3.
$$

For each path, store:

```text
cash flow = E3
cash-flow time = t3
```

### Date $t_2$

Discount the currently stored future cash flow back to $t_2$:

$$
Y_2 =
D(t_2,t_3)E_3.
$$

Regress $Y_2$ on basis functions of the state at $t_2$.

Estimate:

$$
\widehat{C}_2.
$$

Exercise if:

$$
E_2>\widehat{C}_2.
$$

Otherwise retain the future cash flow from $t_3$.

### Date $t_1$

Discount the currently selected future optimal cash flow back to $t_1$.

Regress it on the state at $t_1$.

Exercise if:

$$
E_1>\widehat{C}_1.
$$

Otherwise continue.

Finally, discount each path’s selected optimal cash flow to time zero and average.

---

## 19. Time-Zero Price

After backward induction, every path has one of the following:

- an exercise payoff at one exercise date;
- zero payoff if the option is never exercised.

Let the optimal exercise time on path $n$ be:

$$
\tau_n^*.
$$

The path value at time zero is:

$$
V_0^{(n)} =
D
\left(
0,\tau_n^*
\right)
CF_n^*.
$$

The Monte Carlo estimate is:

$$
V(0)
\approx
\frac{1}{N}
\sum_{n=1}^{N}
D
\left(
0,\tau_n^*
\right)
CF_n^*.
$$

---

## 20. Full LSM Algorithm

The complete procedure is:

```text
1. Simulate all market-factor paths
2. Calculate exercise values at all exercise dates
3. At the final exercise date:
       cash flow = immediate exercise value
4. Move backward through earlier exercise dates
5. For each exercise date:
       a. identify in-the-money paths
       b. discount future selected cash flows to the current date
       c. build regression features
       d. regress discounted future cash flows on current state variables
       e. estimate continuation values
       f. compare immediate exercise with continuation
       g. update exercise decisions and path cash flows
6. Discount final selected path cash flows to time zero
7. Average across paths
```

---

## 21. Pseudocode

```text
simulate state paths

initialize cash flows at final exercise date

for exercise date moving backward:

    identify in-the-money paths

    for each relevant path:

        calculate immediate exercise value

        discount current future cash flow
        back to the exercise date

        construct basis functions

    regress discounted future cash flow
    on current basis functions

    estimate continuation value

    for each relevant path:

        if exercise value > continuation value:

            replace future cash flow
            with immediate exercise value

            replace cash-flow time
            with current exercise date

discount final path cash flows to time zero

price = average discounted cash flow
```

---

## 22. Why the Algorithm Moves Backward

At an early exercise date, the value of continuation depends on what the holder will do at later exercise dates.

Therefore, later exercise decisions must be solved first.

This is the same principle as dynamic programming.

The recursive value relation is:

$$
V_m =
\max
\left[
E_m,
\mathbb{E}
\left(
D(t_m,t_{m+1})V_{m+1}
\mid X_m
\right)
\right].
$$

Backward induction evaluates this recursion from the last date toward the first.

---

## 23. Why the Regression Target Is a Realized Future Cash Flow

The continuation value is an expectation, but each Monte Carlo path provides only one realized future outcome.

For path $n$, the regression target is:

$$
Y_m^{(n)} =
D
\left(
t_m,\tau_n
\right)
CF_n.
$$

Across many paths, the regression learns the average relationship between current state and future discounted value.

Thus:

```text
Single path:
one noisy realized future value

Many paths:
cross-sectional regression approximates conditional expectation
```

---

## 24. Look-Ahead Bias

A basic LSM implementation often uses the same simulated paths to:

- estimate the regression;
- apply the estimated exercise policy;
- calculate the option value.

This can introduce an upward bias because the exercise strategy is fitted and evaluated on the same sample.

A more robust design separates:

```text
Training paths
→ estimate regression coefficients

Pricing paths
→ apply the fixed exercise policy
```

This is often called an out-of-sample or two-pass LSM procedure.

The chapter’s educational implementation may use an in-sample version for clarity, but the distinction is important.

---

## 25. Lower-Bound Interpretation

An exercise strategy generated by LSM is generally suboptimal because the continuation approximation is imperfect.

Applying a fixed admissible exercise strategy produces a lower bound for the true option value.

This means:

$$
V_{\mathrm{LSM}}
\le
V_{\mathrm{true}}
$$

when the policy is evaluated properly out of sample.

The better the continuation-value approximation, the closer the LSM estimate should be to the true value.

---

## 26. Basis-Function Trade-Off

Too few basis functions may underfit.

For example:

$$
\widehat{C}(x) =
\beta_0+\beta_1x
$$

may be too simple.

Too many basis functions may overfit:

$$
1,x,x^2,x^3,x^4,x^5,\ldots
$$

especially when there are relatively few in-the-money paths.

A practical basis should balance:

- flexibility;
- stability;
- interpretability;
- available sample size.

For a simple one-factor Bermudan swaption model, a low-order polynomial basis is often sufficient for demonstration.

---

## 27. Regression Conditioning

The matrix:

$$
\Phi^\top\Phi
$$

may be poorly conditioned if:

- basis functions are highly correlated;
- the state variable has a narrow range;
- too many high-order powers are included;
- too few in-the-money paths are available;
- state variables have very different scales.

Possible remedies include:

- state-variable standardization;
- lower polynomial degree;
- QR regression;
- singular-value decomposition;
- ridge regularization;
- orthogonal basis functions.

---

## 28. Ridge Regression Extension

Ridge regression solves:

$$
\widehat{\beta} =
\arg\min_{\beta}
\left[
\left\|
\Phi\beta-Y
\right\|^2
+
\lambda\left\|\beta\right\|^2
\right].
$$

The solution is:

$$
\widehat{\beta} =
\left(
\Phi^\top\Phi+\lambda I
\right)^{-1}
\Phi^\top Y.
$$

A small regularization parameter $\lambda$ can stabilize regression when the basis matrix is nearly singular.

---

## 29. Common Basis Choices

### Polynomial basis

$$
1,x,x^2,x^3.
$$

### Laguerre basis

$$
1,
$$

$$
e^{-x/2},
$$

$$
e^{-x/2}(1-x),
$$

$$
e^{-x/2}
\left(
1-2x+\frac{x^2}{2}
\right).
$$

### Hermite basis

$$
1,
$$

$$
x,
$$

$$
x^2-1,
$$

$$
x^3-3x.
$$

### Product basis for multiple states

For $x_1,x_2$:

$$
1,
x_1,
x_2,
x_1^2,
x_2^2,
x_1x_2.
$$

The chapter typically uses a polynomial basis because it is transparent and easy to implement in both Python and C++.

---

## 30. Exercise Boundary

The exercise boundary separates states where exercise is optimal from states where continuation is optimal.

For a one-dimensional state variable $x$, the boundary approximately solves:

$$
E(x) =
\widehat{C}(x).
$$

For a payer swaption, the exercise region is often associated with sufficiently high swap rates.

However, the exact boundary also depends on:

- annuity;
- volatility;
- remaining exercise opportunities;
- mean reversion;
- yield-curve shape;
- remaining swap maturity.

---

## 31. Exercise Probabilities

The simulation can report the proportion of paths exercised at each date.

For exercise date $t_m$:

$$
p_m =
\frac{
\text{number of paths exercised at }t_m
}{
N
}.
$$

The no-exercise probability is:

$$
p_{\mathrm{never}} =
1-\sum_m p_m.
$$

These probabilities are useful diagnostics.

Unexpected patterns may indicate:

- incorrect discounting;
- unstable regression;
- wrong intrinsic value;
- indexing mistakes;
- exercise-date errors.

---

## 32. Bermudan, European, and Intrinsic Value Checks

A Bermudan option should generally satisfy:

$$
V_{\mathrm{Bermudan}}
\ge
V_{\mathrm{European}},
$$

because the Bermudan holder has all European exercise opportunities plus additional earlier dates.

It should also satisfy:

$$
V_{\mathrm{Bermudan}}
\ge
V_{\mathrm{intrinsic\ at\ first\ date}}
$$

when values are compared on a consistent basis.

These are important implementation checks.

---

## 33. European Limit

If the exercise schedule contains only one date, LSM should reduce to ordinary European Monte Carlo pricing.

That is:

```text
One exercise date
→ No continuation regression required
→ Payoff evaluated at that date
→ Discount and average
```

This is one of the strongest unit tests for the implementation.

---

## 34. Discounting

Correct discounting is essential.

If a path currently stores a cash flow at time $\tau$, then at exercise date $t_m$ its continuation target is:

$$
Y_m =
D(t_m,\tau)CF.
$$

At the end, the selected cash flow is discounted to time zero:

$$
V_0 =
D(0,\tau)CF.
$$

Using:

$$
D(0,\tau)
$$

when the regression requires:

$$
D(t_m,\tau)
$$

is a common error.

---

## 35. Relationship to the Short-Rate Model

The LSM algorithm is not itself an interest-rate model.

It is an exercise-policy and pricing method.

The underlying state paths may come from:

- Hull–White;
- Vasicek;
- CIR;
- Black–Karasinski;
- LMM;
- multi-factor Gaussian models;
- stochastic-volatility models.

In this chapter, the short-rate or term-structure model supplies:

```text
Simulated rates
Discount factors
Swap rates
Swap annuities
```

LSM then determines when exercise is optimal.

---

## 36. Separation of Model and Exercise Engine

A clean implementation separates:

```text
Interest-rate model
→ generates market states

Product module
→ computes exercise value

LSM engine
→ estimates continuation and chooses exercise

Pricing layer
→ discounts selected cash flows
```

This modular structure allows the same LSM engine to be reused for different products and models.

---

## 37. Python Module Responsibilities

### `basis_functions.py`

Constructs regression features.

Typical responsibilities:

- polynomial basis;
- multivariate interaction terms;
- state standardization;
- basis validation.

---

### `regression.py`

Fits least-squares models.

Typical responsibilities:

- ordinary least squares;
- QR or least-squares solver;
- ridge regularization;
- prediction;
- diagnostics.

---

### `bermudan_swaption.py`

Defines the product.

Typical responsibilities:

- exercise schedule;
- swap maturity;
- strike;
- payer or receiver direction;
- intrinsic value;
- underlying swap state.

---

### `lsm.py`

Contains the backward-induction engine.

Typical responsibilities:

- initialize final exercise cash flows;
- move backward across exercise dates;
- select in-the-money paths;
- build regression targets;
- estimate continuation values;
- apply the exercise rule;
- store optimal path cash flows;
- calculate time-zero value.

---

### `simulation.py`

Produces the market-state paths required by LSM.

Typical outputs may include:

- short-rate paths;
- discount-factor paths;
- swap-rate paths;
- annuity paths;
- state-variable arrays.

---

### `diagnostics.py`

Reports:

- exercise probabilities;
- regression coefficients;
- number of in-the-money paths;
- continuation-value summaries;
- condition numbers;
- standard errors;
- Bermudan versus European values.

---

### `plotting.py`

Typical plots include:

- immediate exercise value versus state;
- estimated continuation curve;
- exercise boundary;
- exercise probability by date;
- regression residuals;
- Bermudan value convergence.

---

## 38. C++ Module Responsibilities

### `BasisFunctions.hpp` and `BasisFunctions.cpp`

Implement:

- polynomial features;
- feature-matrix construction;
- state transformations.

### `Regression.hpp` and `Regression.cpp`

Implement:

- least-squares fitting;
- linear-system solution;
- prediction;
- optional regularization.

### `BermudanSwaption.hpp` and `BermudanSwaption.cpp`

Implement:

- exercise dates;
- strike;
- notional;
- payer or receiver payoff;
- swap annuity;
- intrinsic value.

### `LSMEngine.hpp` and `LSMEngine.cpp`

Implement:

- backward induction;
- in-the-money path selection;
- continuation regression;
- exercise decisions;
- cash-flow updating;
- time-zero pricing.

### `Diagnostics.hpp` and `Diagnostics.cpp`

Implement console reporting for:

- exercise frequencies;
- regression sample size;
- price summaries;
- convergence checks.

### `main.cpp`

Coordinates:

```text
1. Build market model
2. Simulate paths
3. Build product
4. Calculate state variables
5. Run LSM backward induction
6. Print price and diagnostics
```

---

## 39. Minimal Usage Flow

The high-level workflow is:

```text
Build market model
        ↓
Simulate paths
        ↓
Define Bermudan exercise dates
        ↓
Compute intrinsic values and state variables
        ↓
Run backward induction
        ↓
Estimate continuation values
        ↓
Determine pathwise exercise policy
        ↓
Discount optimal cash flows
        ↓
Average to obtain price
```

The README intentionally avoids reproducing the full Python and C++ implementations. The notebook and source files contain the executable examples.

---

## 40. Diagnostics to Inspect

A robust LSM implementation should report at least:

- total number of paths;
- exercise dates;
- number of in-the-money paths per date;
- number of regression observations;
- regression coefficients;
- exercise probability per date;
- probability of never exercising;
- Bermudan price;
- European benchmark price;
- Monte Carlo standard error.

These diagnostics help distinguish model behavior from implementation errors.

---

## 41. Convergence Analysis

The LSM price should be checked against:

- number of Monte Carlo paths;
- time-step size;
- polynomial degree;
- number of basis functions;
- random seed;
- regression method;
- training and pricing sample split.

A stable implementation should not change dramatically under small reasonable adjustments.

---

## 42. Common Implementation Errors

### Wrong discounting interval

The continuation target must be discounted from the future cash-flow date back to the current exercise date.

### Forward instead of backward induction

Exercise decisions must be solved from the final date backward.

### Regressing all paths without consideration

Including many irrelevant out-of-the-money paths may distort the continuation fit.

### Too many basis functions

High-order polynomials may overfit and produce unstable boundaries.

### Wrong exercise payoff

A payer and receiver swaption have opposite intrinsic-value formulas.

### Updating exercised paths incorrectly

Once an earlier exercise decision replaces a later cash flow, the later cash flow must no longer be used.

### Index mismatch

Exercise dates, simulation times, payment dates, and swap periods must align consistently.

### In-sample valuation bias

Using the same paths for fitting and pricing can overstate value.

---

## 43. Numerical Improvements

More advanced implementations may include:

- out-of-sample policy evaluation;
- cross-validation;
- ridge regression;
- orthogonal basis functions;
- adaptive basis selection;
- state-variable standardization;
- QR or SVD solvers;
- dual upper bounds;
- control variates;
- antithetic paths;
- quasi-Monte Carlo;
- parallel simulation.

---

## 44. Duality and Upper Bounds

LSM naturally produces a lower-bound estimate when an admissible exercise strategy is evaluated out of sample.

More advanced methods construct an upper bound using martingale duality.

This creates a valuation interval:

$$
V_{\mathrm{lower}}
\le
V_{\mathrm{true}}
\le
V_{\mathrm{upper}}.
$$

The gap between the bounds provides information about exercise-policy quality.

This extension is beyond the core chapter but is important in production Bermudan pricing.

---

## 45. Interpretation for Bermudan Swaptions

For a payer Bermudan swaption:

```text
High swap rate
→ Immediate exercise becomes attractive

Low swap rate
→ Continue or expire worthless
```

However, exercise does not depend only on current intrinsic value.

Even when the option is in the money, continuation may be more valuable because:

- rates may rise further;
- later exercise opportunities remain;
- volatility has value;
- the remaining swap structure may be more favorable.

LSM explicitly compares the immediate intrinsic value with the estimated value of waiting.

---

## 46. Conceptual Example

Suppose at an exercise date:

```text
Immediate exercise value = 82,000
Estimated continuation value = 95,000
```

Then:

```text
Continue
```

because waiting is estimated to be more valuable.

On another path:

```text
Immediate exercise value = 110,000
Estimated continuation value = 88,000
```

Then:

```text
Exercise now
```

The algorithm performs this comparison path by path and date by date.

---

## 47. Key Conceptual Takeaways

### LSM solves an optimal stopping problem

The holder chooses the best exercise date among several opportunities.

### Immediate exercise value is known

At each exercise date, intrinsic value is calculated from the simulated state.

### Continuation value is unknown

It is a conditional expectation of future optimal cash flows.

### Regression approximates continuation value

Monte Carlo paths provide the training data.

### The algorithm moves backward

Later exercise decisions must be solved before earlier decisions.

### State variables matter

The regression can only learn from information included in the state representation.

### Basis functions matter

Too simple causes underfitting; too complex causes instability.

### LSM is model-independent

It can be combined with many short-rate and term-structure models.

---

## 48. Chapter Summary

The Least-Squares Monte Carlo method combines:

```text
Monte Carlo paths
        ↓
Immediate exercise values
        ↓
Discounted future cash flows
        ↓
Regression-based continuation values
        ↓
Backward exercise decisions
        ↓
Optimal pathwise cash flows
        ↓
Time-zero price
```

The central recursion is:

$$
V_m
=
\max
\left[
E_m,
\mathbb{E}
\left(
D(t_m,t_{m+1})V_{m+1}
\mid X_m
\right)
\right].
$$

LSM replaces the unknown conditional expectation with a regression estimate:

$$
\widehat{C}_m(X_m).
$$

The path exercises when:

$$
E_m>\widehat{C}_m.
$$

This transforms a difficult early-exercise pricing problem into a practical combination of simulation, regression, and backward induction.

---

## 49. Link to the Next Chapter

Chapter 12 focuses on early exercise under a simulated interest-rate environment.

Chapter 13 changes the term-structure representation itself.

Instead of simulating a single short rate and deriving the curve, the next chapter directly simulates a vector of forward rates using the Gaussian LIBOR Market Model.

```text
Chapter 12
Short-rate paths
+
Least-Squares Monte Carlo
+
Bermudan exercise
        ↓
Early-exercise pricing

Chapter 13
Forward-rate vector
+
Correlation
+
Terminal-measure simulation
        ↓
Caplet and swaption pricing
```

Together, the two chapters provide complementary tools:

- LSM for exercise decisions;
- LMM for multi-forward curve dynamics.

---

## Disclaimer

This repository is provided for educational and research purposes only.

It is not intended to provide investment advice, trading recommendations, valuation opinions, or production-ready risk-management infrastructure.
