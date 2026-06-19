#ifndef HULLWHITEMODEL_HPP_INCLUDED
#define HULLWHITEMODEL_HPP_INCLUDED

#include <vector>

#include "curve.hpp"

/*
    HullWhiteModel.hpp

    One-factor Hull-White short-rate model:

        dr(t) = [theta(t) - a r(t)] dt + sigma dW(t)

    where:
        a     = mean reversion speed
        sigma = short-rate volatility
        theta(t) is fitted to the initial yield curve
*/

class HullWhiteModel {

public:

    double a;
    double sigma;
    YieldCurve* curve;

    HullWhiteModel(
        double meanReversion,
        double volatility,
        YieldCurve* curve_
    );

    double B(
        double t,
        double T
    ) const;

    double instantaneousForwardRate(
        double t,
        double bump = 1e-2
    ) const;

    double instantaneousForwardDerivative(
        double t,
        double bump = 5e-2
    ) const;

    double theta(
        double t
    ) const;

    double shortRateDrift(
        double t,
        double r
    ) const;

    double evolveShortRate(
        double t,
        double r,
        double dt,
        double z
    ) const;
};

#endif // HULLWHITEMODEL_HPP_INCLUDED
