# Chapter 15 — Interest-Rate Counterparty Exposure and XVA

# 15.1 Chapter Overview

This chapter extends the Gaussian LIBOR Market Model developed in Chapter 13 from derivative pricing to counterparty exposure and valuation adjustment analysis.

Chapter 13 produces Monte Carlo paths of future forward-rate curves. Chapter 15 uses those simulated curves to revalue a portfolio of interest-rate swaps at multiple future dates. The resulting future mark-to-market distributions are then converted into counterparty-risk measures such as Expected Exposure, Expected Positive Exposure, Potential Future Exposure, Credit Valuation Adjustment, Debit Valuation Adjustment, and Funding Valuation Adjustment.

The central workflow is:

```text
Initial yield curve
        ↓
Gaussian LMM forward-rate simulation
        ↓
Future interest-rate curves
        ↓
Future swap mark-to-market values
        ↓
Netting-set portfolio values
        ↓
EE, ENE, EPE, and PFE
        ↓
CVA, DVA, and simplified FVA
```

The chapter deliberately uses the Gaussian LMM from Chapter 13 rather than introducing another interest-rate model. The purpose is to show how an existing market-risk model can become the market-scenario engine of an exposure and XVA framework.

---

# 15.2 Project Structure

```text
15_Interest-Rate Counterparty Exposure and XVA/
├── python/
│   ├── xva_trade.py
│   ├── xva_exposure.py
│   ├── xva_collateral.py
│   ├── xva_metrics.py
│   ├── xva_adjustments.py
│   └── xva_plotting.py
│
├── cpp/
│   ├── XVAData.hpp
│   ├── InterestRateTrade.hpp
│   ├── InterestRateTrade.cpp
│   ├── ExposureEngine.hpp
│   ├── ExposureEngine.cpp
│   ├── ExposureMetrics.hpp
│   ├── ExposureMetrics.cpp
│   ├── XVAAdjustments.hpp
│   ├── XVAAdjustments.cpp
│   └── main.cpp
│
├── notebooks/
│   └── 15_interest_rate_exposure_and_xva.ipynb
│
└── tests/
    └── test.py
```

The Python implementation includes a simplified collateral module for educational comparison. The C++ implementation focuses on the uncollateralized exposure and XVA workflow and directly reuses the Chapter 13 Gaussian LMM source files.

---

# 15.3 From Pricing to Exposure

A traditional derivative-pricing problem asks:

> What is the value of the trade today?

An exposure problem asks:

> What could the value of the trade become at different future dates under different market scenarios?

The current value of a swap is one number:

$$
V(0).
$$

At a future time $t$, however, the swap value is uncertain. Under $M$ Monte Carlo paths, the exposure engine produces a distribution:

$$
V^{(1)}(t),
V^{(2)}(t),
\ldots,
V^{(M)}(t).
$$

Each path represents one possible future state of the interest-rate market.

Counterparty exposure is therefore not determined directly by the present value of a transaction. It is determined by the future distribution of its mark-to-market value.

A transaction that is currently close to zero may still generate substantial future exposure if interest rates move significantly before maturity.

---

# 15.4 Reusing the Chapter 13 Gaussian LMM

The market-scenario engine is the Gaussian LMM introduced in Chapter 13.

For forward rate $L_i(t)$ associated with the accrual period from $T_i$ to $T_{i+1}$, the model has the general form:

$$
dL_i(t)=
\mu_i(t)\,dt
+
\sigma_i(t)
\mathbf{b}_i^{\mathsf{T}}
d\mathbf{W}(t).
$$

Here:

- $L_i(t)$ is the simulated forward rate;
- $\mu_i(t)$ is the measure-consistent drift;
- $\sigma_i(t)$ is the deterministic normal-volatility function;
- $\mathbf{b}_i$ contains the factor loadings;
- $\mathbf{W}(t)$ is a vector of Brownian risk factors.

Chapter 13 produces a three-dimensional collection of simulated forward rates:

```text
forward_paths[path][time][forward]
```

Chapter 15 does not resimulate rates independently. It consumes the forward-rate paths produced by Chapter 13 and converts each simulated forward curve into future discount factors and future swap values.

This separation is important:

```text
Chapter 13
market dynamics and scenario generation

Chapter 15
future valuation, exposure, and XVA
```

---

# 15.5 Reconstructing Discount Factors from Forward Rates

The Gaussian LMM directly models forward rates, but swap valuation requires discount factors.

For a simple forward rate over the period from $T_i$ to $T_{i+1}$:

$$
1+\delta_iL_i(t)=
\frac{P(t,T_i)}
{P(t,T_{i+1})},
$$

where:

- $\delta_i$ is the accrual period;
- $P(t,T_i)$ is the discount factor observed at time $t$ for maturity $T_i$.

Therefore:

$$
P(t,T_{i+1})=
\frac{P(t,T_i)}
{1+\delta_iL_i(t)}.
$$

At a tenor-aligned valuation date $t=T_k$:

$$
P(T_k,T_k)=1.
$$

The remaining discount factors are then reconstructed recursively:

$$
P(T_k,T_{k+1})=
\frac{1}
{1+\delta_kL_k(T_k)},
$$

and:

$$
P(T_k,T_{k+2})=
\frac{P(T_k,T_{k+1})}
{1+\delta_{k+1}L_{k+1}(T_k)}.
$$

This recursive relationship transforms every simulated forward curve into a simulated discount curve.

A valid forward state must satisfy:

$$
1+\delta_iL_i(t)>0.
$$

Without this condition, the implied discount factor would be zero or negative.

---

# 15.6 Future Valuation of an Interest-Rate Swap

Consider a fixed-for-floating interest-rate swap with:

- notional $N$;
- fixed rate $K$;
- remaining payment dates $T_{a+1},\ldots,T_b$;
- accrual periods $\delta_j$.

The remaining fixed-leg annuity at time $t$ is:

$$
A(t)=
\sum_{j=a}^{b-1}
\delta_jP(t,T_{j+1}).
$$

The present value of the fixed leg is:

$$
PV_{\mathrm{fixed}}(t)=
NKA(t).
$$

Under the single-curve framework used in this chapter, the floating-leg value is:

$$
PV_{\mathrm{floating}}(t)=
N
\left[
P(t,T_a)-
P(t,T_b)
\right].
$$

The value of a payer-fixed swap is therefore:

$$
V_{\mathrm{payer}}(t)=
N\left[
P(t,T_a)-
P(t,T_b)-
K
\sum_{j=a}^{b-1}
\delta_jP(t,T_{j+1})
\right].
$$

A receiver-fixed swap has the opposite value:

$$
V_{\mathrm{receiver}}(t)=-
V_{\mathrm{payer}}(t).
$$

At every simulation path and exposure date, the chapter repeats this valuation using the simulated forward curve for that path.

The result is a future mark-to-market cube:

```text
trade_values[path][time][trade]
```

---

# 15.7 Netting-Set Exposure

Counterparty exposure is normally calculated at the legally enforceable netting-set level rather than separately for every trade.

For $J$ transactions with the same counterparty, the netting-set value is:

$$
V_{\mathrm{NS}}(t)=
\sum_{j=1}^{J}
V_j(t).
$$

Without netting, total positive exposure would be:

$$
PE_{\mathrm{gross}}(t)=
\sum_{j=1}^{J}
\max
\left[
V_j(t),0
\right].
$$

With close-out netting, positive exposure becomes:

$$
PE_{\mathrm{net}}(t)=
\max
\left[
\sum_{j=1}^{J}V_j(t),
0
\right].
$$

In general:

$$
PE_{\mathrm{net}}(t)
\leq
PE_{\mathrm{gross}}(t).
$$

A trade with positive value can therefore be offset by another trade with negative value, provided both transactions belong to the same enforceable netting agreement.

The exposure engine first sums the simulated trade values and then applies the positive- or negative-exposure transformation.

---

# 15.8 Positive and Negative Exposure

From the bank's perspective, a positive portfolio value means the counterparty owes money to the bank. This creates counterparty credit exposure.

For simulation path $m$:

$$
PE_m(t)=
\max
\left[
V_m(t),0
\right].
$$

A negative portfolio value means the bank owes money to the counterparty. The negative exposure is reported as a positive amount:

$$
NE_m(t)=
\max
\left[
-V_m(t),0
\right].
$$

Positive and negative exposures are therefore non-negative quantities, even though the underlying mark-to-market value can be positive or negative.

They support different valuation adjustments:

```text
Positive exposure
→ counterparty default loss
→ CVA

Negative exposure
→ bank own-default benefit
→ DVA
```

The asymmetry created by the maximum function is fundamental. Exposure cannot be calculated by simply taking the expected portfolio value.

In general:

$$
\mathbb{E}
\left[
\max
\left(
V(t),0
\right)
\right]
\neq
\max
\left[
\mathbb{E}
\left(
V(t)
\right),0
\right].
$$

---

# 15.9 EE, ENE, EPE, and PFE

## Expected Exposure

Expected Exposure is the average positive exposure across Monte Carlo paths at a specific future date:

$$
EE(t_k)=
\frac{1}{M}
\sum_{m=1}^{M}
\max
\left[
V_m(t_k),0
\right].
$$

$EE(t)$ is a profile through time rather than a single number.

## Expected Negative Exposure

Expected Negative Exposure is:

$$
ENE(t_k)=
\frac{1}{M}
\sum_{m=1}^{M}
\max
\left[
-V_m(t_k),0
\right].
$$

It is used in the simplified DVA and funding-benefit calculations.

## Expected Positive Exposure

Expected Positive Exposure is a time average of the EE profile:

$$
EPE=
\frac{1}{T}
\int_0^T
EE(t)\,dt.
$$

In the implementation, the integral is approximated using trapezoidal integration.

## Potential Future Exposure

Potential Future Exposure is a high quantile of the positive-exposure distribution:

$$
PFE_q(t)=
Q_q
\left[
PE(t)
\right],
$$

where $q$ may be $95\%$ or $99\%$.

The distinction is:

```text
EE
average positive exposure

PFE
high-quantile positive exposure

EPE
time average of EE
```

$PFE$ is particularly useful for understanding tail exposure, limit management, and stress in the future mark-to-market distribution.

---

# 15.10 The Typical Shape of an Exposure Profile

Interest-rate swap exposure often follows a hump-shaped pattern.

At inception, exposure may be relatively small because the trade is usually entered near market value.

As time passes, interest-rate uncertainty accumulates and the future mark-to-market distribution widens. Both $EE$ and $PFE$ may therefore increase.

Closer to maturity, fewer cash flows remain and the value of the transaction converges toward zero. Exposure consequently declines.

A simplified qualitative pattern is:

```text
small initial exposure
        ↓
growing market uncertainty
        ↓
peak exposure
        ↓
declining remaining maturity
        ↓
zero exposure at maturity
```

The precise shape depends on:

- trade direction;
- fixed rate;
- current yield curve;
- volatility level;
- correlation structure;
- maturity;
- portfolio netting;
- simulation measure;
- number and timing of remaining cash flows.

A portfolio containing payer and receiver swaps may exhibit materially lower exposure than the individual trades because of offsetting rate sensitivities.

---

# 15.11 Credit Curves and Default Probabilities

The chapter uses a simplified flat-hazard credit model.

For constant hazard rate $\lambda$, survival probability is:

$$
S(t)=
\exp
\left[
-\lambda t
\right].
$$

The unconditional probability of default between $t_{i-1}$ and $t_i$ is approximated by:

$$
\Delta PD_i=
S(t_{i-1})-
S(t_i).
$$

Recovery rate is denoted by $R$. Loss given default is:

$$
LGD=
1-R.
$$

For example, when $R=40\%$:

$$
LGD=
60\%.
$$

The implementation uses one credit curve for the counterparty and another for the bank.

This allows the framework to distinguish:

```text
counterparty default risk
→ CVA

bank own-default risk
→ DVA
```

The credit curves are deterministic and independent of the simulated interest-rate paths. Consequently, the model does not include wrong-way risk.

---

# 15.12 CVA and DVA

## Credit Valuation Adjustment

CVA represents the expected discounted loss caused by counterparty default.

The discrete approximation used in this chapter is:

$$
CVA=
LGD_C
\sum_{i=1}^{n}
DF(0,t_i)
EE(t_i)
\Delta PD_C(t_i).
$$

Here:

- $LGD_C$ is the counterparty loss-given-default;
- $DF(0,t_i)$ is the initial discount factor;
- $EE(t_i)$ is expected positive exposure;
- $\Delta PD_C(t_i)$ is the counterparty marginal default probability.

CVA is reported as a positive cost. It reduces the value of the portfolio:

$$
V_{\mathrm{after\ CVA}}=
V_{\mathrm{risk\ free}}-
CVA.
$$

## Debit Valuation Adjustment

DVA represents the valuation benefit associated with the bank's own default risk.

The simplified formula is:

$$
DVA=
LGD_B
\sum_{i=1}^{n}
DF(0,t_i)
ENE(t_i)
\Delta PD_B(t_i).
$$

DVA is reported as a positive benefit:

$$
V_{\mathrm{after\ CVA,DVA}}=
V_{\mathrm{risk\ free}}-
CVA
+
DVA.
$$

Although DVA is standard in fair-value theory, its economic interpretation is more controversial because the benefit increases when the bank's own credit quality deteriorates.

---

# 15.13 Simplified Funding Valuation Adjustment

The chapter includes a basic funding adjustment to illustrate how exposure can create funding costs or benefits.

Funding Cost Adjustment is approximated by:

$$
FCA=
\sum_{i=1}^{n}
DF(0,t_i)
EE(t_i)
s_B
\Delta t_i,
$$

where $s_B$ is the bank's borrowing spread.

Funding Benefit Adjustment is approximated by:

$$
FBA=
\sum_{i=1}^{n}
DF(0,t_i)
ENE(t_i)
s_L
\Delta t_i,
$$

where $s_L$ is the assumed lending or investment spread.

The chapter defines:

$$
FVA=
FCA-FBA.
$$

The combined net adjustment is:

$$
XVA_{\mathrm{net}}=
-CVA+DVA-
FVA.
$$

The XVA-adjusted portfolio value is:

$$
V_{\mathrm{adjusted}}=
V_{\mathrm{risk\ free}}
+
XVA_{\mathrm{net}}.
$$

This is an educational approximation. Production FVA frameworks depend strongly on funding policy, collateral, treasury transfer pricing, close-out assumptions, and the treatment of own-credit effects.

---

# 15.14 Python and C++ Architecture

The Python and C++ implementations follow the same conceptual separation.

## Trade layer

Defines interest-rate swaps and groups them into a netting set.

## Market-scenario layer

Uses the Chapter 13 Gaussian LMM to generate future forward-rate paths.

## Valuation layer

Reconstructs future discount factors and calculates future swap values.

## Exposure layer

Transforms future portfolio values into:

- positive exposure;
- negative exposure;
- $EE$;
- $ENE$;
- $EPE$;
- $PFE$.

## Adjustment layer

Combines exposure profiles with deterministic credit and funding assumptions to calculate:

- $CVA$;
- $DVA$;
- $FCA$;
- $FBA$;
- $FVA$.

The C++ implementation directly includes and compiles the Chapter 13 Gaussian LMM source files. Chapter 15 therefore does not create an independent interest-rate simulation model.

The architecture is intentionally modular:

```text
market model
        ↓
future valuation
        ↓
exposure metrics
        ↓
valuation adjustments
```

This makes it possible to replace the Gaussian LMM with another scenario engine while retaining most of the exposure and XVA framework.

---

# 15.15 Scope, Limitations, and Key Takeaways

This chapter focuses on the core mechanics of interest-rate exposure and XVA. It does not attempt to reproduce a production bank XVA system.

The main simplifying assumptions are:

- single-currency interest-rate swaps;
- single-curve discounting and forwarding;
- tenor-aligned valuation dates;
- deterministic interest-rate volatility;
- flat deterministic hazard rates;
- constant recovery rates;
- no wrong-way risk;
- no stochastic credit spreads;
- no collateral in the simplified C++ version;
- no initial margin;
- no margin period of risk;
- no replacement close-out;
- no cure period;
- no MVA;
- no KVA;
- no nested Monte Carlo;
- no regulatory effective EPE calculation.

Despite these simplifications, the chapter demonstrates the essential XVA pipeline:

```text
simulate future markets
        ↓
revalue future trades
        ↓
aggregate within a netting set
        ↓
measure future positive and negative exposure
        ↓
combine exposure with default and funding assumptions
        ↓
calculate valuation adjustments
```

The most important conceptual result is that derivative exposure is not equal to current mark-to-market value. It is a time-dependent distribution generated by future market states, contractual cash flows, trade direction, maturity, and netting.

Chapter 13 answers:

> How might the future interest-rate curve evolve?

Chapter 15 answers:

> Given those future curves, how much could the counterparty owe, how large could tail exposure become, and how should credit and funding risks adjust the derivative value?
