#ifndef STOCHASTICVOLSIMULATION_HPP_INCLUDED
#define STOCHASTICVOLSIMULATION_HPP_INCLUDED

#include <vector>

#include "StochasticVolModel.hpp"

/*
    Simulation result for stochastic-volatility short-rate paths.
*/

struct StochasticVolSimulationResult {

    std::vector<double> times;

    std::vector<std::vector<double>> ratePaths;

    std::vector<std::vector<double>> variancePaths;
};

StochasticVolSimulationResult simulateStochasticVolPaths(
    const StochasticVolModel& model,
    double r0,
    double v0,
    double maturity,
    int nSteps,
    int nPaths,
    unsigned int seed = 42
);

double pathDiscountFactor(
    const std::vector<double>& times,
    const std::vector<double>& ratePath,
    int startIndex,
    int endIndex
);

double pathDiscountFactorFromZero(
    const std::vector<double>& times,
    const std::vector<double>& ratePath,
    int endIndex
);

#endif // STOCHASTICVOLSIMULATION_HPP_INCLUDED
