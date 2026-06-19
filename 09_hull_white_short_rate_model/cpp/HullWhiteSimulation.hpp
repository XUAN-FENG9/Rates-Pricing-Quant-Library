#ifndef HULLWHITESIMULATION_HPP_INCLUDED
#define HULLWHITESIMULATION_HPP_INCLUDED

#include <vector>

#include "HullWhiteModel.hpp"

/*
    HullWhiteSimulation.hpp

    Monte Carlo simulation utilities.
*/

struct SimulationResult {

    std::vector<double> times;

    std::vector<std::vector<double>> paths;
};

SimulationResult simulateShortRatePaths(
    const HullWhiteModel& model,
    double r0,
    double maturity,
    int nSteps,
    int nPaths,
    unsigned int seed = 42
);

double pathDiscountFactor(
    const std::vector<double>& times,
    const std::vector<double>& path
);

double monteCarloZeroCouponBondPrice(
    const SimulationResult& result
);

#endif // HULLWHITESIMULATION_HPP_INCLUDED
