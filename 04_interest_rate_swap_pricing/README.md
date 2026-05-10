\# Chapter 04 — Interest Rate Swap Pricing



\## Overview



This chapter introduces:



\- fixed-for-floating swaps

\- swap cashflows

\- swap NPV

\- par swap rates

\- payer and receiver swaps



Interest rate swaps are among the most important products in fixed income markets.



\---



\# Swap Structure



A plain vanilla swap exchanges:



\- fixed coupons

\- floating coupons



\---



\# Fixed Leg



$$

CF\_{fixed} = N \\times K \\times \\Delta

$$



\---



\# Floating Leg



$$

CF\_{float} = N \\times F \\times \\Delta

$$



\---



\# Swap Valuation



Payer swap:



$$

NPV = PV\_{float} - PV\_{fixed}

$$



\---



\# Par Swap Rate



$$

K = \\frac{1 - DF(T)}{\\sum\_i \\Delta\_i DF(t\_i)}

$$



\---



\# Key Quantitative Concepts



This chapter introduces:



\- discounted cashflow pricing

\- swap valuation

\- forward projection

\- par rates

\- curve sensitivity



These concepts are foundational for:



\- swaptions

\- Bermudan products

\- LMM models

\- XVA systems



\# Project Structure



```text

04\_interest\_rate\_swap\_pricing/

│

├── python/

│   ├── curve.py

│   ├── fixed\_leg.py

│   ├── floating\_leg.py

│   ├── swap.py

│   ├── market\_data.py

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

│   └── 04\_interest\_rate\_swap\_pricing.ipynb

│

├── data/

│   └── usd\_zero\_curve.csv

│

├── tests/

│   └── test\_swap.py

│

└── README.md

```

\---

