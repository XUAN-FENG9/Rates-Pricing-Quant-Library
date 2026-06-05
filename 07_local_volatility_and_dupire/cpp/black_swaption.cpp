#include "black_swaption.hpp"

#include <cmath>

BlackSwaption::BlackSwaption(
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

double BlackSwaption::normal_cdf(
    double x
){

    return 0.5 * erfc(-x/std::sqrt(2));
}

double BlackSwaption::price(
    YieldCurve& curve
){

    double F =
        swap.forward_swap_rate(curve);

    double K = strike;

    double sigma = volatility;

    double T = expiry;

    double annuity =
        swap.annuity(curve);

    double d1 =
        (std::log(F/K) + 0.5*sigma*sigma*T) / (sigma*std::sqrt(T));

    double d2 = d1 - sigma*std::sqrt(T);

    double value;

    if(payer){

        value =
            notional
            * annuity
            * (
                F*normal_cdf(d1)
                - K*normal_cdf(d2)
            );

    }else{

        value =
            notional
            * annuity
            * (
                K*normal_cdf(-d2)
                - F*normal_cdf(-d1)
            );
    }

    return value;
}
