#include "fra.hpp"

FRA::FRA(
    double N,
    double K,
    double s,
    double e
){

    notional = N;
    strike = K;
    start = s;
    endT = e;
}

double FRA::value(
    YieldCurve& curve
){

    double fwd =
        curve.forward_rate(
            start,
            endT
        );

    double accrual =
        endT - start;

    double df =
        curve.discount_factor(endT);

    return
        notional
        * (fwd - strike)
        * accrual
        * df;
}
