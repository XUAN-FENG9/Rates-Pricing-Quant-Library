#include "LSMPathSimulation.hpp"

#include <random>
#include <cmath>
#include <algorithm>

/*
    Simulate Hull-White short-rate paths:

        r_{t+dt}
        =
        r_t
        +
        [theta(t) - a r_t] dt
        +
        sigma sqrt(dt) Z
*/

LSMPathSimulationResult simulateHullWhitePathsForLSM(
    const HullWhiteModel& model,
    double r0,
    double maturity,
    int nSteps,
    int nPaths,
    unsigned int seed
){

    double dt =
        maturity
        /
        static_cast<double>(
            nSteps
        );

    LSMPathSimulationResult result;

    result.times.resize(
        nSteps + 1
    );

    for(int i = 0; i <= nSteps; ++i){

        result.times[i] =
            i
            *
            dt;
    }

    result.ratePaths =
        std::vector<std::vector<double>>(
            nPaths,
            std::vector<double>(
                nSteps + 1,
                0.0
            )
        );

    for(int p = 0; p < nPaths; ++p){

        result.ratePaths[p][0] =
            r0;
    }

    std::mt19937 generator(seed);

    std::normal_distribution<double> normal(
        0.0,
        1.0
    );

    for(int step = 0; step < nSteps; ++step){

        double t =
            result.times[step];

        for(int path = 0; path < nPaths; ++path){

            double r =
                result.ratePaths[path][step];

            double z =
                normal(generator);

            double drift =
                model.shortRateDrift(
                    t,
                    r
                );

            result.ratePaths[path][step + 1] =
                r
                +
                drift
                *
                dt
                +
                model.sigma
                *
                std::sqrt(dt)
                *
                z;
        }
    }

    return result;
}

/*
    Nearest time index.
*/

int nearestTimeIndex(
    const std::vector<double>& times,
    double targetTime
){

    int bestIndex =
        0;

    double bestDiff =
        std::abs(
            times[0]
            -
            targetTime
        );

    for(size_t i = 1; i < times.size(); ++i){

        double diff =
            std::abs(
                times[i]
                -
                targetTime
            );

        if(diff < bestDiff){

            bestDiff = diff;
            bestIndex = static_cast<int>(i);
        }
    }

    return bestIndex;
}

/*
    Discount factor from time 0 to index.
*/

double pathDiscountFactorToIndex(
    const std::vector<double>& times,
    const std::vector<double>& ratePath,
    int endIndex
){

    double dt =
        times[1]
        -
        times[0];

    double integral =
        0.0;

    for(int i = 0; i < endIndex; ++i){

        integral +=
            ratePath[i]
            *
            dt;
    }

    return
        std::exp(
            -integral
        );
}

/*
    Discount factor between two time indices.
*/

double pathDiscountFactorBetweenIndices(
    const std::vector<double>& times,
    const std::vector<double>& ratePath,
    int startIndex,
    int endIndex
){

    double dt =
        times[1]
        -
        times[0];

    double integral =
        0.0;

    for(int i = startIndex; i < endIndex; ++i){

        integral +=
            ratePath[i]
            *
            dt;
    }

    return
        std::exp(
            -integral
        );
}
