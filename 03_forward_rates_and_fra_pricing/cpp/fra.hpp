#include "curve.hpp"


#ifndef FRA_HPP_INCLUDED
#define FRA_HPP_INCLUDED


class FRA {

public:

    double notional;
    double strike;
    double start;
    double endT;

    FRA(
        double N,
        double K,
        double s,
        double e
    );

    double value(
        YieldCurve& curve
    );
};


#endif // FRA_HPP_INCLUDED
