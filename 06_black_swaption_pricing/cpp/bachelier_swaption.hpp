#ifndef BACHELIER_SWAPTION_HPP_INCLUDED
#define BACHELIER_SWAPTION_HPP_INCLUDED

#include "forward_swap.hpp"
#include "curve.hpp"

class BachelierSwaption {

public:

    double notional;

    double strike;

    double expiry;

    double volatility;

    bool payer;

    ForwardStartingSwap swap;

    BachelierSwaption(
        double N,
        double K,
        double T,
        double sigma,
        ForwardStartingSwap underlying_swap,
        bool is_payer=true
    );

    double normal_pdf(double x);

    double normal_cdf(double x);

    double price(
        YieldCurve& curve
    );
};

#endif // BACHELIER_SWAPTION_HPP_INCLUDED
