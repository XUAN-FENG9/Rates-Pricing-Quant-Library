#ifndef BLACK_SWAPTION_HPP_INCLUDED
#define BLACK_SWAPTION_HPP_INCLUDED

#include "forward_swap.hpp"
#include "curve.hpp"

class BlackSwaption {

public:

    double notional;

    double strike;

    double expiry;

    double volatility;

    bool payer;

    ForwardStartingSwap swap;

    BlackSwaption(
        double N,
        double K,
        double T,
        double sigma,
        ForwardStartingSwap underlying_swap,
        bool is_payer=true
    );

    double normal_cdf(double x);

    double price(
        YieldCurve& curve
    );
};

#endif // BLACK_SWAPTION_HPP_INCLUDED
