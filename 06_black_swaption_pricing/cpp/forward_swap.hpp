#ifndef FORWARD_SWAP_HPP_INCLUDED
#define FORWARD_SWAP_HPP_INCLUDED

#include <vector>

#include "curve.hpp"

class ForwardStartingSwap {

public:

    double notional;

    //double fixed_rate;

    double start;

    double end;

    int frequency;

    std::vector<double> payment_dates;

    ForwardStartingSwap(
        double N,
        //double K,
        double start_time,
        double end_time,
        int freq=2
    );

    double annuity(
        YieldCurve& curve
    );

    double forward_swap_rate(
        YieldCurve& curve
    );
};


#endif // FORWARD_SWAP_HPP_INCLUDED
