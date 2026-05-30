#include "bachelier_swaption.hpp"

#include <cmath>

BachelierSwaption::BachelierSwaption(
    double N,
    double K,
    double T,
    double sigma,
    ForwardStartingSwap underlying_swap,
    bool is_payer
)
: swap(underlying_swap)
{

    notional = N;

    strike = K;

    expiry = T;

    volatility = sigma;

    payer = is_payer;
}

double BachelierSwaption::normal_pdf(
    double x
){

    return
        std::exp(-0.5*x*x)
        /
        std::sqrt(2*M_PI);
}

double BachelierSwaption::normal_cdf(
    double x
){

    return
        0.5*erfc(-x/std::sqrt(2));
}

double BachelierSwaption::price(
    YieldCurve& curve
){

    double F =
        swap.forward_swap_rate(curve);

    double K = strike;

    double sigma = volatility;

    double T = expiry;

    double A =
        swap.annuity(curve);

    double stddev =
        sigma * std::sqrt(T);

    double d =
        (F-K)/stddev;

    double value;

    if(payer){

        value =
            notional
            * A
            * (
                (F-K)
                * normal_cdf(d)
                +
                stddev
                * normal_pdf(d)
            );

    }else{

        value =
            notional
            * A
            * (
                (K-F)
                * normal_cdf(-d)
                +
                stddev
                * normal_pdf(d)
            );
    }

    return value;
}
