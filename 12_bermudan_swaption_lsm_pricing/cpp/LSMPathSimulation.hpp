#ifndef LSMPATHSIMULATION_HPP_INCLUDED
#define LSMPATHSIMULATION_HPP_INCLUDED


#include <vector>

#include "../../09_hull_white_short_rate_model/cpp/HullWhiteModel.hpp"

/*
    LSMPathSimulation.hpp

    Monte Carlo simulation for Hull-White short-rate paths.
*/

struct LSMPathSimulationResult {

    std::vector<double> times;

    std::vector<std::vector<double>> ratePaths;
};

LSMPathSimulationResult simulateHullWhitePathsForLSM(
    const HullWhiteModel& model,
    double r0,
    double maturity,
    int nSteps,
    int nPaths,
    unsigned int seed = 42
);

int nearestTimeIndex(
    const std::vector<double>& times,
    double targetTime
);

double pathDiscountFactorToIndex(
    const std::vector<double>& times,
    const std::vector<double>& ratePath,
    int endIndex
);

double pathDiscountFactorBetweenIndices(
    const std::vector<double>& times,
    const std::vector<double>& ratePath,
    int startIndex,
    int endIndex
);

#endif // LSMPATHSIMULATION_HPP_INCLUDED
