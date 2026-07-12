#ifndef LMMSIMULATION_HPP_INCLUDED
#define LMMSIMULATION_HPP_INCLUDED


#include <vector>

#include "GaussianLMM.hpp"

/*
    LMMSimulation.hpp

    Monte Carlo simulation of Gaussian LMM forward curves.
*/

struct LMMSimulationResult {

    std::vector<double> times;

    /*
        Dimensions:

            path
            กั time
            กั forward
    */

    std::vector<
        std::vector<
            std::vector<double>
        >
    > forwardPaths;
};

LMMSimulationResult simulateGaussianLMM(
    const GaussianLMM& model,
    double simulationEnd,
    int numberOfSteps,
    int numberOfPaths,
    unsigned int seed = 42,
    bool antithetic = true
);

int nearestSimulationIndex(
    const std::vector<double>& times,
    double targetTime
);

#endif // LMMSIMULATION_HPP_INCLUDED
