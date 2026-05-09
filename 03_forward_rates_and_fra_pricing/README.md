# Chapter 03 — Forward Rates and FRA Pricing



# 3.1 Overview



This chapter introduces:



- implied forward rates

- forward curve construction

- FRA pricing

- no-arbitrage relationships



Forward rates are fundamental in fixed income markets because they represent:



> market-implied future interest rates.



---



# 3.2 Forward Rates



Forward rates are derived from discount factors:


$$ F(t\_1,t\_2)  = \\frac{DF(t\_1)}{DF(t\_2)} - 1 $$



Forward curves are critical for:



- swaps

- swaptions

- FRA instruments

- LIBOR market models



---



# 3.3 FRA



Forward Rate Agreements allow counterparties to lock future borrowing/lending rates.



Example:



- 3x6 FRA

- starts in 3 months

- ends in 6 months



---



# 3.4 FRA Valuation



$$
PV = N(F-K)\\Delta DF
$$



where:



- $N$ = notional

- $F$ = forward rate

- $K$ = strike

- $\\Delta$ = accrual



---



# 3.5 FO Perspective



Forward curves are heavily monitored by:



- rates traders

- central banks

- macro hedge funds



because they encode:



- future rate expectations

- policy expectations

- liquidity conditions



---



# 3.6 Key Quant Concepts



This chapter introduces:



- no-arbitrage pricing

- implied rates

- forward discounting

- FRA valuation



These concepts are foundational for:



- swap pricing

- swaption pricing

- HJM models

- LMM frameworks

---

# 3.7 Project Structure
03_forward_rates_and_fra_pricing/
│
├── python/
│   ├── curve.py
│   ├── forward_rates.py
│   ├── fra.py
│   ├── market_data.py
│   └── plotting.py
│
├── cpp/
│   ├── curve.hpp
│   ├── curve.cpp
│   ├── fra.hpp
│   ├── fra.cpp
│   └── main.cpp
│
├── notebooks/
│   └── 03_forward_rates_and_fra_pricing.ipynb
│
├── data/
│   └── usd_zero_curve.csv
│
├── tests/
│   └── test_fra.py
│
└── README.md


