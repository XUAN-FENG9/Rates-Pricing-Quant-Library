#ifndef STOCHASTICVOLPRICING_HPP_INCLUDED
#define STOCHASTICVOLPRICING_HPP_INCLUDED

#include "StochasticVolSimulation.hpp"

/*
    Monte Carlo pricing functions for stochastic-volatility short-rate model.
*/

int nearestTimeIndex(
    const std::vector<double>& times,
    double targetTime
);

double monteCarloZeroCouponBondPrice(
    const StochasticVolSimulationResult& result,
    double maturity
);

double monteCarloBondOptionPrice(
    const StochasticVolSimulationResult& result,
    double optionExpiry,
    double bondMaturity,
    double strike,
    bool isCall = true
);

#endif // STOCHASTICVOLPRICING_HPP_INCLUDED
