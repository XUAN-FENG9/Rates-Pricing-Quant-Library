#ifndef SWAP_HPP_INCLUDED
#define SWAP_HPP_INCLUDED

#include "curve.hpp"

class InterestRateSwap {

public:

    double notional;
    double fixed_rate;
    double maturity;

     std::vector<double> payment_dates;

    InterestRateSwap(
        double N,
        double K,
        double T
    );

    double npv(
        YieldCurve& curve
    );
};


#endif // SWAP_HPP_INCLUDED
