#ifndef RISK_HPP_INCLUDED
#define RISK_HPP_INCLUDED

#include "curve.hpp"
#include "swap.hpp"

double dv01(
    InterestRateSwap& swap,
    YieldCurve& curve
);

#endif // RISK_HPP_INCLUDED
